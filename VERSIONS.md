# AnoDB Versions

[Sources](https://github.com/zx80/anodb),
[documentation](https://zx80.github.io/anodb/) and
[issues](https://github.com/zx80/anodb/issues)
are available on [GitHub](https://github.com/).

## TODO

- make it work with "with", i.e. provide relevant __enter__ and __exit__?
- sync drivers with aiosql?
- add something about caching?
- sync version numbering with aiosql?

## 7.2 on 2022-12-11

Fix issue with `mariadb`.
Improve documentation for `github.io`.

## 7.1 on 2022-11-12

Test with Python *3.12*.

## 7.0 on 2022-10-26

Add support for MariaDB driver: `mariadb`.
Make `connect` return the underlying connection.
Improved documentation.

## 6.1 on 2022-09-11

Add GitHub CI configuration.
Add Markdown checks.
More badges.

## 6.0 on 2022-08-08

Make connection string parameter optional, as some drivers do not need it.
Add support for MySQL drivers: `pymysql`, `mysqlclient`, `mysql-connector`.
Add support for Postgres drivers: `pygresql`, `pg8000`.
Improved documentation.
Improved tests.

## 5.0 on 2022-07-10

Improve `Makefile`.
Get `aiosql` version.
Simplify code.
Sync driver support with aiosql 4.0.
Require 100% coverage.

## 4.2.1 on 2022-01-16

Just fix doc date.

## 4.2.0 on 2022-01-16

Put back `__version__` automatic extraction from package.
Add `__version__` attribute to DB class.
Refactor tests.

## 4.1.0 on 2021-12-12

Add untested support for MySQL through `aiosql_mysql`.
Temporary work around an issue between `pkg_resources`, `typing_extensions` and `aiosql`.

## 4.0.2 on 2021-12-12

Add type hint for mypy.

## 4.0.1 on 2021-12-11

Add package `__version__`.
Minor update for `pytest_postgresql` 4.0.0.

## 4.0 on 2021-10-14

Add [psycopg 3](https://www.psycopg.org/psycopg3/) support, and make it the
default for Postgres.

## 3.0 on 2021-04-20

Package as a simple module.
Use simpler `setup.cfg` packaging.
Include tests in package.
Add coverage test and make test coverage reach 100%.

## 2.2 on 2021-02-20

Setup explicit logger instead of relying on default.

## 2.1 on 2021-02-14

Make `cursor()` reconnect if needed.

Add automatic reconnection tests.

## 2.0 on 2021-02-13

Swith from `AnoSQL` to `AioSQL`.

## 1.3 on 2020-08-02

Make `options` accept different types.

Make `queries` optional, and allow to load from files or strings.

## 1.2 on 2020-07-31

Add `options` string parameter to constructor.

## 1.1 on 2020-07-28

Add `**conn_options` parameter to constructor.

Add `cursor()` method.

## 1.0 on 2020-07-27

Initial release.
