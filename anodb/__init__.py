#
# This marvelous code is Public Domain.
#

from typing import Any, Dict
import logging
import functools
import anosql as sql # type: ignore


class DB:
	"""Hides database connection and queries in here.

	The class provides the DB-API 2.0 connection methods,
	and SQL execution methods from anosql.
	"""

	def __init__(self, db: str, conn: str, queries: str, options: Any = None,
				 auto_reconnect: bool = True, debug: bool = False, **conn_options):
		"""DB constructor

		- db: database engine, `sqlite` or `postgres`
		- conn: database-specific connection string
		- queries: file holding queries for `anosql`
		- options: database-specific options in various forms
		- auto_reconnect: whether reconnecting on connection errors
		- debug: debug mode generate more logs through `logging`
		- conn_options: database-specific `kwargs` constructor options
		"""
		logging.info(f"creating DB for {db}")
        # database connection
		self._db = 'sqlite3' if db in ('sqlite3', 'sqlite') else \
			'psycopg2' if db in ('pg', 'postgres', 'postgresql', 'psycopg2') else \
			None
		assert self._db is not None, f"database {db} is supported"
		self._conn_str = conn
		self._queries_file = queries
		# accept connection options as they are
		self._conn_options: Dict[str,Any] = {}
		if options is None:
			pass
		elif isinstance(options, str):
			import ast
			self._conn_options.update(ast.literal_eval(options))
		elif isinstance(options, dict):
			self._conn_options.update(options)
		else:
			raise Exception(f"unexpected type for options: {type(options)}")
		self._conn_options.update(conn_options)
		self._debug = debug
		self._auto_reconnect = auto_reconnect
		self._reconn = False
		self._count = {}
		self._conn = self._connect()
		self._queries = sql.from_path(queries, self._db)
		# forward queries with inserted database connection
		# self.some_query(args) -> self._queries.some_query(self._conn, args)
		for q in self._queries.available_queries:
			setattr(self, q, functools.partial(self._call_query, q))
			self._count[q] = 0

	def _call_query(self, query, *args, **kwargs): 
		"""Forward method call to anosql query

		On connection failure, it will try to reconnect on the next call
		if auto_reconnect was specified.

		This may or may not be a good idea, but it should be: the failure
		raises an exception which should abort the current request, so that
		the next call should be on a different request.
		"""
		if self._debug:
			logging.debug(f"DB y: {query}({args}, {kwargs})")
		if self._reconn and self._auto_reconnect:
			self._reconnect()
		try:
			self._count[query] += 1
			return getattr(self._queries, query)(self._conn, *args, **kwargs)
		except Exception as error:
			logging.info(f"DB {self._db} query {query} failed: {error}")
			# coldly rollback on any error
			try:
				self._conn.rollback()
			except Exception as rolerr:
				logging.warning(f"DB {self._db} rollback failed: {rolerr}")
			# detect a connection error for psycopg2, to attempt a reconnection
			# should more cases be handled?
			if hasattr(self._conn, 'closed') and self._conn.closed == 2 and self._auto_reconnect:
				self._reconn = True
			raise error

	def _connect(self):
		"""Create a database connection."""
		logging.info(f"DB {self._db}: connecting")
		if self._db == 'sqlite3':
			import sqlite3 as db
			return db.connect(self._conn_str, **self._conn_options)
		elif self._db == 'psycopg2':
			import psycopg2 as db # type: ignore
			return db.connect(self._conn_str, **self._conn_options)
		else:
			# note: anosql currently supports sqlite & postgres
			raise Exception(f"unexpected db {self._db}")

	def _reconnect(self):
		"""Try to reconnect to database."""
		logging.info(f"DB {self._db}: reconnecting")
		if self._conn is not None:
			# attempt at closing but ignore errors
			try:
				self._conn.close()
			except Exception as error:
				logging.error(f"DB {self._db} close: {error}")
		self._conn = self._connect()
		self._reconn = False

	def connect(self):
		"""Create database connection if needed."""
		if self._conn is None:
			self._conn = self._connect()

	def cursor(self):
		"""Get a cursor on the current connection."""
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
