# AnoDB

Convenient Wrapper around [aiosql](https://github.com/nackjicholson/aiosql)
and a [Database Connection](https://www.python.org/dev/peps/pep-0249).

![Status](https://github.com/zx80/anodb/actions/workflows/anodb-package.yml/badge.svg?branch=master&style=flat)
![Tests](https://img.shields.io/badge/tests-11%20✓-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-success)
![Python](https://img.shields.io/badge/python-3-informational)
![Databases](https://img.shields.io/badge/databases-4-informational)
![Drivers](https://img.shields.io/badge/drivers-9-informational)
![Version](https://img.shields.io/pypi/v/anodb)
![Badges](https://img.shields.io/badge/badges-9-informational)
![License](https://img.shields.io/pypi/l/anodb?style=flat)

## Description

This class creates a persistent database connection and imports
SQL queries from a file as simple Python functions.

If the connection is broken, a new connection is attempted.

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
db = anodb.DB("sqlite3", "test.db", "test.sql")

db.do_some_insert(key=1, val="hello")
db.do_some_update(key=1, val="world")
print("data", db.do_some_select(key=1))
db.commit()

db.close()
```

With file `test.sql` containing something like:

```SQL
-- name: do_some_select
SELECT * FROM Stuff WHERE key = :key;

-- name: do_some_insert!
INSERT INTO Stuff(key, val) VALUES (:key, :val);

-- name: do_some_update!
UPDATE Stuff SET val = :val WHERE key = :key;
```

## Documentation

The `anodb` module provides the `DB` class which embeds both a
[PEP 249](https://peps.python.org/pep-0249/) database connection
(providing methods `commit`, `rollback`, `cursor`, `close` and
its `connect` counterpart to re-connect) *and* SQL queries wrapped
into dynamically generated functions by [aiosql](https://pypi.org/project/aiosql/).
Such functions may be loaded from a string (`add_queries_from_str`) or a
path (`add_queries_from_path`).

The `DB` constructor parameters are:

- `db` the name of the database driver: `sqlite3`, `psycopg`, `pymysql`,
  see [aiosql documentation](https://nackjicholson.github.io/aiosql/database-driver-adapters.html)
  for a list of supported drivers.
- `conn` an optional connection string used to initiate a connection with the driver.
  For instance, `psycopg` accepts a
  [libpq connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
  such as: `"host=db1.my.org port=5432 dbname=acme user=calvin …"`.
- `queries` an optional path name from which to read query definitions.
- `options` an optional dictionary or string to pass additional connection
  parameters.
- `auto_reconnect` whether to attempt a reconnection if the connection is lost.
  Default is `True`.
- `debug` whether to generate debugging messages.
  Default is `False`.
- other named parameters are passed as additional connection parameters.

```python
import anodb

db = anodb.DB("sqlite3", ":memory:", "acme-queries.sql")
db = anodb.DB("psycopg", "host=localhost dbname=acme", "acme-queries.sql")
```

## Versions

Sources are available on [GitHub](https://github.com/zx80/anodb).

### 7.1 on 2022-11-12

Test with Python *3.12*.

### 7.0 on 2022-10-26

Add support for MariaDB driver: `mariadb`.
Make `connect` return the underlying connection.
Improved documentation.

### 6.1 on 2022-09-11

Add GitHub CI configuration.
Add Markdown checks.
More badges.

### 6.0 on 2022-08-08

Make connection string parameter optional, as some drivers do not need it.
Add support for MySQL drivers: `pymysql`, `mysqlclient`, `mysql-connector`.
Add support for Postgres drivers: `pygresql`, `pg8000`.
Improved documentation.
Improved tests.

### 5.0 on 2022-07-10

Improve `Makefile`.
Get `aiosql` version.
Simplify code.
Sync driver support with aiosql 4.0.
Require 100% coverage.

### 4.2.1 on 2022-01-16

Just fix doc date.

### 4.2.0 on 2022-01-16

Put back `__version__` automatic extraction from package.
Add `__version__` attribute to DB class.
Refactor tests.

### 4.1.0 on 2021-12-12

Add untested support for MySQL through `aiosql_mysql`.
Temporary work around an issue between `pkg_resources`, `typing_extensions` and `aiosql`.

### 4.0.2 on 2021-12-12

Add type hint for mypy.

### 4.0.1 on 2021-12-11

Add package `__version__`.
Minor update for `pytest_postgresql` 4.0.0.

### 4.0 on 2021-10-14

Add [psycopg 3](https://www.psycopg.org/psycopg3/) support, and make it the
default for Postgres.

### 3.0 on 2021-04-20

Package as a simple module.
Use simpler `setup.cfg` packaging.
Include tests in package.
Add coverage test and make test coverage reach 100%.

### 2.2 on 2021-02-20

Setup explicit logger instead of relying on default.

### 2.1 on 2021-02-14

Make `cursor()` reconnect if needed.

Add automatic reconnection tests.

### 2.0 on 2021-02-13

Swith from `AnoSQL` to `AioSQL`.

### 1.3 on 2020-08-02

Make `options` accept different types.

Make `queries` optional, and allow to load from files or strings.

### 1.2 on 2020-07-31

Add `options` string parameter to constructor.

### 1.1 on 2020-07-28

Add `**conn_options` parameter to constructor.

Add `cursor()` method.

### 1.0 on 2020-07-27

Initial release.

## TODO

- make it work with "with", i.e. provide relevant __enter__ and __exit__
- sync drivers with aiosql?
- add something about caching?
- sync version numbering with aiosql?
