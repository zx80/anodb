#
# This marvelous code is Public Domain.
#

from typing import Any, Callable
import logging
import importlib
import functools as ft
import datetime as dt
import time
import aiosql as sql  # type: ignore
from aiosql.types import DriverAdapterProtocol
import json

log = logging.getLogger("anodb")

# get package version
from importlib.metadata import version as pkg_version
__version__ = pkg_version("anodb")


class AnoDBException(Exception):
    """Locally generated exception."""
    pass


#
# DB (Database) class
#
class DB:
    """Hides database connection and queries in here.

    The class provides the DB-API 2.0 connection methods,
    and SQL execution methods from aiosql.
    """

    # global counter to help identify DB objects
    _counter = 0

    # database connection driver and variants, with a little hardcoding
    SQLITE = ("sqlite3", "sqlite")
    POSTGRES = ("psycopg", "pg", "postgres", "postgresql", "psycopg3")
    # others stay as-is: psycopg2 pg8000…

    # connection delays
    _CONNECTION_MIN_DELAY = 0.001
    _CONNECTION_MAX_DELAY = 30.0

    def _log_info(self, m: str):
        log.info(f"DB:{self._db}:{self._id} {m}")

    def _log_debug(self, m: str):
        log.debug(f"DB:{self._db}:{self._id} {m}")

    def _log_warning(self, m: str):
        log.warning(f"DB:{self._db}:{self._id} {m}")

    def _log_error(self, m: str):
        log.error(f"DB:{self._db}:{self._id} {m}")

    def __init__(
        self,
        db: str,
        conn: str|None,
        queries: str|list[str] = [],
        options: str|dict[str, Any] = {},  # undocumented backward compatibility
        # further connection options
        conn_args: list[str] = [],
        conn_kwargs: dict[str, Any] = {},
        # adapter creation options
        adapter_args: list[Any] = [],
        adapter_kwargs: dict[str, Any] = {},
        # anodb behavior
        auto_reconnect: bool = True,
        kwargs_only: bool = False,
        attribute: str = "__",
        exception: Callable[[BaseException], BaseException]|None = None,
        debug: bool = False,
        **conn_options,
    ):
        """
        DB constructor

        - :param db: database engine/driver.
        - :param conn: database-specific simple connection string.
        - :param queries: file(s) holding queries for `aiosql`, may be empty.
        - :param conn_args: database-specific connection options as a list.
        - :param conn_kwargs: database-specific connection options as a dict.
        - :param adapter_args: adapter creation options as a list.
        - :param adapter_kwargs: adapter creation options as a dict.
        - :param auto_reconnect: whether to reconnect on connection errors.
        - :param kwargs_only: whether to require named parameters on query execution.
        - :param attribute: attribute dot access substitution, default is ``"__"``.
        - :param exception: user function to reraise database exceptions.
        - :param debug: debug mode, generate more logs through ``logging``.
        - :param **conn_options: database-specific ``kwargs`` connection options.
        """
        DB._counter += 1
        self._id = DB._counter
        self.__version__ = __version__
        self.__aiosql_version__ = pkg_version("aiosql")
        # this is the class name
        self._db = (
            "sqlite3" if db in self.SQLITE else "psycopg" if db in self.POSTGRES else db
        ).lower()
        assert self._db in sql.aiosql._ADAPTERS, f"database {db} is supported"
        self._log_info("creating DB")
        self._set_db_pkg()
        # connection parameters…
        self._conn = None
        self._conn_args = [] if conn is None else [conn]
        self._conn_args.extend(conn_args)
        self._conn_kwargs: dict[str, Any] = dict(conn_kwargs)
        self._adapter: DriverAdapterProtocol|None = None
        # backward compatibility for "options"
        if isinstance(options, str):
            import ast

            self._conn_kwargs.update(ast.literal_eval(options))
        elif isinstance(options, dict):
            self._conn_kwargs.update(options)
        else:
            raise AnoDBException(f"unexpected type for options: {type(options)}")
        # remaining parameters are associated to the connection
        self._conn_kwargs.update(conn_options)
        # adapter
        self._adapter_args = list(adapter_args)
        self._adapter_kwargs = dict(adapter_kwargs)
        # useful global stats
        self._count: dict[str, int] = {}  # name -> #calls
        self._conn_last = None  # current connection start
        self._conn_count: int = 0  # how many connections succeeded
        self._conn_total: int = 0  # number of "executions" in this connection
        self._conn_ntx: int = 0  # number of tx in this connection
        self._conn_nstat: int = 0  # number of executions (fn, cursors) in current tx
        self._total: int = 0  # total number of executions
        self._ntx: int = 0  # number of tx
        # various boolean flags
        self._debug = debug
        if debug:
            log.setLevel(logging.DEBUG)
            self._log_debug("running in debug mode…")
        self._auto_reconnect = auto_reconnect
        self._kwargs_only = kwargs_only
        self._reconn = False
        # oother parameters
        self._attribute = attribute
        self._exception = exception
        # queries… keep track of calls
        self._queries_file = [queries] if isinstance(queries, str) else queries
        self._queries: list[sql.aiosql.Queries] = []  # type: ignore
        self._available_queries: set[str] = set()
        for fn in self._queries_file:
            self.add_queries_from_path(fn)
        # last thing is to actually create the connection, which may fail
        self._conn_delay: float|None = None  # seconds
        self._conn_last_fail: dt.datetime|None = None
        self._conn_attempts: int = 0
        self._conn_failures: int = 0
        self._do_connect()

    def _possibly_reconnect(self):
        """Detect a connection error for psycopg."""
        # FIXME detect other cases of bad connections?
        self._reconn = self._auto_reconnect and (
            (self._db == "psycopg" and hasattr(self._conn, "closed") and self._conn.closed) or      # type: ignore
            (self._db == "psycopg2" and hasattr(self._conn, "closed") and self._conn.closed == 2))  # type: ignore

    def _call_fn(self, _query, _fn, *args, **kwargs):
        """Forward method call to aiosql query.

        On connection failure, it will try to reconnect on the next call
        if auto_reconnect was set.

        This may or may not be a good idea, but it should be: the failure
        raises an exception which should abort the current request, so that
        the next call should be on a different request.
        """
        _ = self._debug and self._log_debug(f"{_query}({args}, {kwargs})")
        if self._reconn and self._auto_reconnect:
            self._reconnect()
        self._conn_nstat += 1
        self._count[_query] += 1
        try:
            return _fn(self._conn, *args, **kwargs)
        except self._db_error as error:
            self._log_info(f"query {_query} failed: {error}")
            # coldly rollback on any error
            try:
                if self._conn:
                    self._conn.rollback()
            except self._db_error as rolerr:
                self._log_warning(f"rollback failed: {rolerr}")
            self._possibly_reconnect()
            # re-raise error
            raise self._exception(error) if self._exception else error
        except Exception as e:  # pragma: no cover
            self._log_error(f"unexpected exception: {e}")
            raise

    # this could probably be done dynamically by overriding __getattribute__
    def _create_fns(self, queries: sql.aiosql.Queries):  # type: ignore
        """Create call forwarding to insert the database connection."""
        # keep first encountered adapter
        if self._adapter is None:
            self._adapter = queries.driver_adapter
        self._queries.append(queries)
        for q in queries.available_queries:
            f = getattr(queries, q)
            # we skip internal *_cursor attributes
            if callable(f):
                self._log_info(f"adding q={q}")
                if hasattr(self, q):
                    raise AnoDBException(f"cannot override existing method: {q}")
                setattr(self, q, ft.partial(self._call_fn, q, f))
                self._available_queries.add(q)
                self._count[q] = 0

    def add_queries_from_path(self, fn: str):
        """Load queries from a file or directory."""
        self._create_fns(sql.from_path(fn, self._db, *self._adapter_args,
                                       kwargs_only=self._kwargs_only, attribute=self._attribute,
                                       **self._adapter_kwargs))

    def add_queries_from_str(self, qs: str):
        """Load queries from a string."""
        self._create_fns(sql.from_str(qs, self._db, *self._adapter_args,
                                      kwargs_only=self._kwargs_only, attribute=self._attribute,
                                      **self._adapter_kwargs))

    def _set_db_pkg(self):
        """Load database package."""
        package, module = self._db, self._db

        # skip apsw as DB API support is really partial?
        if self._db == "pygresql":
            package, module = "pgdb", "pgdb"
        elif self._db in ("MySQLdb", "mysqldb"):  # pragma: no cover
            package, module = "MySQLdb", "mysqlclient"
        elif self._db in ("mysql-connector", "mysql.connector"):  # pragma: no cover
            package, module = "mysql.connector", "mysql.connector"
        else:
            pass

        # record db package
        try:
            self._db_pkg = importlib.import_module(package)
        except ImportError:  # pragma: no cover
            self._log_error(f"cannot import {package} for {self._db}")
            raise

        # best effort only
        try:
            self._db_version = pkg_version(module)
        except Exception:
            self._db_version = "<unknown>"

        # get exception class
        self._db_error = self._db_pkg.Error if hasattr(self._db_pkg, "Error") else Exception

        # myco does not need to follow the standard?
        if self._db_error == Exception:  # pragma: no cover
            self._log_error(f"missing Error class in {package}, falling back to Exception")

    def __connect(self):
        """Create a database connection (internal)."""
        self._log_info(f"{self._db}: connecting")
        # PEP249 does not impose a unified signature for connect.
        return self._db_pkg.connect(*self._conn_args, **self._conn_kwargs)

    def _do_connect(self):
        """Create a connection, possibly with active throttling."""
        self._conn = None
        try:
            self._conn_attempts += 1
            if self._conn_delay is not None:
                delay = dt.timedelta(seconds=self._conn_delay)
                assert self._conn_last_fail
                wait = (delay - (dt.datetime.now(dt.timezone.utc) - self._conn_last_fail)).total_seconds()
                if wait > 0.0:
                    self._log_info(f"connection wait #{self._conn_attempts}: {wait}")
                    time.sleep(wait)
            self._conn = self.__connect()
            # on success, update stats
            self._ntx += self._conn_ntx
            self._total += self._conn_total
            self._conn_count += 1
            self._conn_last = dt.datetime.now(dt.timezone.utc)
            self._conn_total = 0
            self._conn_ntx = 0
            # on success, reset reconnection stuff
            self._conn_attempts = 0
            self._conn_last_fail = None
            self._conn_delay = None
        except self._db_error as e:
            self._conn_failures += 1
            self._conn_last = None
            self._conn_last_fail = dt.datetime.now(dt.timezone.utc)
            if self._conn_delay is None:
                self._conn_delay = self._CONNECTION_MIN_DELAY
            else:
                self._conn_delay = min(2 * self._conn_delay, self._CONNECTION_MAX_DELAY)
            self._log_error(f"connect failed #{self._conn_attempts}: {e}")
            raise e

    def _reconnect(self):
        """Try to reconnect to database, possibly with some cleanup."""
        self._log_info(f"{self._db}: reconnecting")
        if self._conn:
            # attempt at closing but ignore errors
            try:
                self._conn.close()
            except self._db_error as error:  # pragma: no cover
                self._log_error(f"DB {self._db} close: {error}")
        self._do_connect()
        self._reconn = False

    def connect(self):
        """Create (if needed) and return the database connection."""
        if "_conn" not in self.__dict__ or not self._conn:
            self._do_connect()
        return self._conn

    def cursor(self):
        """Get a cursor on the current connection."""
        if self._reconn and self._auto_reconnect:
            self._reconnect()
        assert self._conn is not None and self._adapter is not None
        self._conn_nstat += 1
        if hasattr(self._adapter, "_cursor"):
            return self._adapter._cursor(self._conn)  # type: ignore
        else:  # pragma: no cover
            return self._conn.cursor()

    def commit(self):
        """Commit database transaction."""
        assert self._conn is not None
        self._conn_ntx += 1
        self._conn_total += self._conn_nstat
        self._conn_nstat = 0
        self._conn.commit()

    def rollback(self):
        """Rollback database transaction."""
        assert self._conn is not None
        self._conn_ntx += 1
        self._conn_total += self._conn_nstat
        self._conn_nstat = 0
        self._conn.rollback()

    def close(self):
        """Close underlying database connection if needed."""
        if self._conn is not None:
            # NOTE only reset if close succeeded?
            self._conn.close()
            self._conn = None
            # should we try to reconnect?
            self._reconn = self._auto_reconnect

    def _stats(self):
        """Generate a JSON-compatible structure for statistics."""
        return {
            "id": self._id,
            "driver": self._db,
            "info": self._conn_args,  # _conn_kwargs?
            "conn": {
                # current connection status
                "nstat": self._conn_nstat,
                "total": self._conn_total,
                "ntx": self._conn_ntx,
                "last": self._conn_last.isoformat() if self._conn_last else None,
                # (re)connection attempt status
                "attempts": self._conn_attempts,
                "failures": self._conn_failures,
                "delay": self._conn_delay,
                "last-fail": self._conn_last_fail.isoformat() if self._conn_last_fail else None,
            },
            # life time
            "total": self._total,
            "ntx": self._ntx,
            "calls": self._count,
            "count": self._conn_count,
        }

    def __str__(self):
        return json.dumps(self._stats())

    def __del__(self):
        if hasattr(self, "_conn") and self._conn:
            self.close()
