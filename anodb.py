#
# This marvelous code is Public Domain.
#

from typing import Any, Dict, Set, List, Union
import logging
import functools as ft
import aiosql as sql  # type: ignore

log = logging.getLogger("anodb")

# get package version
import pkg_resources as pkg  # type: ignore

__version__ = pkg.require("anodb")[0].version


#
# DB (Database) class
#
class DB:
    """Hides database connection and queries in here.

    The class provides the DB-API 2.0 connection methods,
    and SQL execution methods from aiosql.
    """

    # database connection driver and variants, with a little hardcoding
    SQLITE = ("sqlite3", "sqlite")
    POSTGRES = ("psycopg", "pg", "postgres", "postgresql", "psycopg3")
    # other stay as-is: psycopg2 pg8000…

    def __init__(
        self,
        db: str,
        conn: str,
        queries: str = None,
        options: Union[None, str, Dict[str, Any]] = None,
        auto_reconnect: bool = True,
        debug: bool = False,
        **conn_options,
    ):
        """DB constructor

        - db: database engine/driver)
        - conn: database-specific connection string
        - queries: file holding queries for `aiosql`, may be empty
        - options: database-specific options in various forms
        - auto_reconnect: whether to reconnect on connection errors
        - debug: debug mode generate more logs through `logging`
        - conn_options: database-specific `kwargs` constructor options
        """
        self.__version__ = __version__
        self.__aiosql_version__ = pkg.require("aiosql")[0].version
        log.info(f"creating DB for {db}")
        self._db = (
            "sqlite3" if db in self.SQLITE else "psycopg" if db in self.POSTGRES else db
        )
        assert self._db in sql.aiosql._ADAPTERS, f"database {db} is supported"
        # connection…
        self._conn = None
        self._conn_str = conn
        self._conn_options: Dict[str, Any] = {}
        if not options:
            pass
        elif isinstance(options, str):
            import ast

            self._conn_options.update(ast.literal_eval(options))
        elif isinstance(options, dict):
            self._conn_options.update(options)
        else:  # pragma: no cover
            raise Exception(f"unexpected type for options: {type(options)}")
        self._conn_options.update(conn_options)
        # various boolean flags
        self._debug = debug
        self._auto_reconnect = auto_reconnect
        self._reconn = False
        # queries… keep track of calls
        self._queries_file = queries
        self._queries: List[sql.aiosql.Queries] = []
        self._count: Dict[str, int] = {}
        self._available_queries: Set[str] = set()
        if queries:
            self.add_queries_from_path(queries)
        # last thing is to actually create the connection, which may fail
        self._conn = self._connect()

    def _call_fn(self, query, fn, *args, **kwargs):
        """Forward method call to aiosql query

        On connection failure, it will try to reconnect on the next call
        if auto_reconnect was specified.

        This may or may not be a good idea, but it should be: the failure
        raises an exception which should abort the current request, so that
        the next call should be on a different request.
        """
        if self._debug:  # pragma: no cover
            log.debug(f"DB: {query}({args}, {kwargs})")
        if self._reconn and self._auto_reconnect:
            self._reconnect()
        try:
            self._count[query] += 1
            return fn(self._conn, *args, **kwargs)
        except Exception as error:
            log.info(f"DB {self._db} query {query} failed: {error}")
            # coldly rollback on any error
            try:
                self._conn.rollback()
            except Exception as rolerr:
                log.warning(f"DB {self._db} rollback failed: {rolerr}")
            # detect a connection error for psycopg[23], to attempt a
            # reconnection should more cases be handled?
            if (
                self._db == "psycopg"
                and hasattr(self._conn, "closed")
                and self._conn.closed
                and self._auto_reconnect
            ):
                self._reconn = True
            elif (
                self._db == "psycopg2"
                and hasattr(self._conn, "closed")
                and self._conn.closed == 2
                and self._auto_reconnect
            ):
                self._reconn = True
            # re-raise initial error
            raise error

    # this could probably be done dynamic by overriding __getattribute__
    def _create_fns(self, queries: sql.aiosql.Queries):
        """Create call forwarding to insert the database connection."""
        self._queries.append(queries)
        for q in queries.available_queries:
            f = getattr(queries, q)
            # we skip internal *_cursor attributes
            if callable(f):
                setattr(self, q, ft.partial(self._call_fn, q, f))
                self._available_queries.add(q)
                self._count[q] = 0

    def add_queries_from_path(self, fn: str):
        """Load queries from a file or directory."""
        self._create_fns(sql.from_path(fn, self._db))

    def add_queries_from_str(self, qs: str):
        """Load queries from a string."""
        self._create_fns(sql.from_str(qs, self._db))

    def _connect(self):
        # FIXME could/should be more generic?
        """Create a database connection."""
        log.info(f"DB {self._db}: connecting")
        # load module
        if self._db == "sqlite3":
            import sqlite3 as db

            self._db_version = db.version
        # skip apsw as DB API support is really partial
        elif self._db == "psycopg":
            import psycopg as db  # type: ignore
        elif self._db == "psycopg2":
            import psycopg2 as db  # type: ignore
        elif self._db == "pymysql":  # pragma: no cover
            import pymysql as db  # type: ignore
        elif self._db == "mysqldb":  # pragma: no cover
            import MySQLdb as db  # type: ignore
        elif self._db == "mysql-connector":  # pragma: no cover
            import mysql.connector as db  # type: ignore
        else:  # pragma: no cover
            raise Exception(f"unexpected db {self._db}")
        # get version if needed
        if not hasattr(self, "_db_version"):
            if hasattr(db, "__version__"):
                self._db_version = db.__version__
            else:  # pragma: no cover
                self._db_version = pkg.require(self._db)[0].version
        # do connect
        return db.connect(self._conn_str, **self._conn_options)

    def _reconnect(self):
        """Try to reconnect to database."""
        log.info(f"DB {self._db}: reconnecting")
        if self._conn:
            # attempt at closing but ignore errors
            try:
                self._conn.close()
            except Exception as error:  # pragma: no cover
                log.error(f"DB {self._db} close: {error}")
        self._conn = self._connect()
        self._reconn = False

    def connect(self):
        """Create database connection if needed."""
        if "_conn" not in self.__dict__ or not self._conn:
            self._conn = self._connect()

    def cursor(self):
        """Get a cursor on the current connection."""
        if self._reconn and self._auto_reconnect:
            self._reconnect()
        return self._conn.cursor()

    def commit(self):
        """Commit database transaction."""
        self._conn.commit()

    def rollback(self):
        """Rollback database transaction."""
        self._conn.rollback()

    def close(self):
        """Close underlying database connection."""
        self._conn.close()
        self._conn = None

    def __str__(self):
        return f"connection to {self._db} database ({self._conn_str})"

    def __del__(self):
        if hasattr(self, "_conn") and self._conn:
            self.close()
