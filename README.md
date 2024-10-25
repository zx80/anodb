# AnoDB

Convenient Wrapper around [aiosql](https://github.com/nackjicholson/aiosql)
and a [Database Connection](https://www.python.org/dev/peps/pep-0249).

![Status](https://github.com/zx80/anodb/actions/workflows/anodb-package.yml/badge.svg?branch=main&style=flat)
![Tests](https://img.shields.io/badge/tests-16%20✓-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-success)
![Python](https://img.shields.io/badge/python-3-informational)
![Databases](https://img.shields.io/badge/databases-6-informational)
![Drivers](https://img.shields.io/badge/drivers-15-informational)
![Version](https://img.shields.io/pypi/v/anodb)
![Badges](https://img.shields.io/badge/badges-9-informational)
![License](https://img.shields.io/pypi/l/anodb?style=flat)

## Description

This class creates a persistent database connection and imports
SQL queries from a file as simple Python functions.

If the connection is broken, a new connection is attempted with increasing
throttling delays.

Compared to `aiosql`, the point is not to need to pass a connection
as an argument on each call: The `DB` class embeds both connection
*and* query methods.

For concurrent programming (threads, greenlets…), a relevant setup
should also consider thread-locals and pooling issues at some higher level.

## Example

Install the module with `pip install anodb` or whatever method you like.
Once available:

```python
import anodb
# parameters: driver, connection string, SQL file
db = anodb.DB("sqlite3", "test.db", "test.sql", kwargs_only=True)

db.create_stuff()
db.do_some_insert(key=1, val="hello")
db.do_some_update(key=1, val="world")
print("data", db.do_some_select(key=1))
print("norm", db.compute_norm(c=3+4j))
db.commit()

db.close()
```

With file `test.sql` containing something like:

```sql
-- name: create_stuff#
CREATE TABLE Stuff(key INTEGER PRIMARY KEY, val TEXT NOT NULL);

-- name: do_some_select^
SELECT * FROM Stuff WHERE key = :key;

-- name: do_some_insert!
INSERT INTO Stuff(key, val) VALUES (:key, :val);

-- name: do_some_update!
UPDATE Stuff SET val = :val WHERE key = :key;

-- name: compute-norm$
SELECT SQRT(:c.real * :c.real + :c.imag * :c.imag);
```

## Documentation

The `anodb` module provides the `DB` class which embeds both a
[PEP 249](https://peps.python.org/pep-0249/) database connection
(providing methods `commit`, `rollback`, `cursor`, `close` and
its `connect` counterpart to re-connect) *and* SQL queries wrapped
into dynamically generated functions by
[aiosql](https://pypi.org/project/aiosql/).
Such functions may be loaded from a string (`add_queries_from_str`) or a
path (`add_queries_from_path`).

The `DB` constructor main parameters are:

- `db` the name of the database driver: `sqlite3`, `psycopg`, `pymysql`, see
  [aiosql documentation](https://nackjicholson.github.io/aiosql/database-driver-adapters.html)
  for a list of supported drivers.
- `conn` an optional connection string used to initiate a connection with the driver.
  For instance, `psycopg` accepts a
  [libpq connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
  such as: `"host=db1.my.org port=5432 dbname=acme user=calvin …"`.
- `queries` a path name or list of path names from which to read query definitions.
- `conn_args` and `conn_kwargs` a list and dictionary of further connection parameters.
- `auto_reconnect` whether to attempt a reconnection if the connection is lost.
  Default is `True`. Reconnection attempts are throttled exponentially
  following powers of two delays from *0.001* and capped at *30.0* seconds.
- `kwargs_only` whether to only accept named parameters to python functions.
  This helps avoiding silly bugs!
- `debug` whether to generate debugging messages through `logging`.
- other named parameters are passed as additional connection parameters.
  For instance you might consider using `autocommit=True` with `psycopg`.

```python
import anodb

db = anodb.DB("sqlite3", "acme.db", "acme-queries.sql")
db = anodb.DB("duckdb", "acme.db", "acme-queries.sql")
db = anodb.DB("psycopg", "host=localhost dbname=acme", "acme-queries.sql", autocommit=True)
db = anodb.DB("psycopg", None, "acme-queries.sql", host="localhost", user="calvin", password="...", dbname="acme")
db = anodb.DB("psycopg2", "host=localhost dbname=acme", "acme-queries.sql")
db = anodb.DB("pygresql", None, "acme-queries.sql", host="localhost:5432", user="calvin", password="...", database="acme")
db = anodb.DB("pg8000", None, "acme-queries.sql", host="localhost", port=5432, user="calvin", password="...", database="acme")
db = anodb.DB("MySQLdb", None, "acme-queries.sql", host="localhost", port=3306, user="calvin", password="...", database="acme")
db = anodb.DB("pymysql", None, "acme-queries.sql", host="localhost", port=3306, user="calvin", password="...", database="acme")
db = anodb.DB("mysql-connector", None, "acme-queries.sql", host="localhost", port=3306, user="calvin", password="...", database="acme")
db = anodb.DB("mariadb", None, "acme-queries.sql", host="localhost", port=3306, user="calvin", password="...", database="acme")
db = anodb.DB("pymssql", None, "acme-queries.sql", server="localhost", port=1433, user="sa", password="...", database="acme", as_dict=True, autocommit=False)
```

See DB docstring for knowing about all parameters.

## License

This code is [Public Domain](https://creativecommons.org/publicdomain/zero/1.0/).

All software has bug, this is software, hence… Beware that you may lose your
hairs or your friends because of it. If you like it, feel free to send a
postcard to the author.

## Versions

[Sources](https://github.com/zx80/anodb),
[documentation](https://zx80.github.io/anodb/) and
[issues](https://github.com/zx80/anodb/issues)
are available on [GitHub](https://github.com/).

See [all versions](VERSIONS.md) and
get [packages](https://pypi.org/project/anodb/) from [PyPI](https://pypi.org/).
