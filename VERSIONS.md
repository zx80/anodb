# AnoDB Versions

Package distributed from [Pypi](https://pypi.org/project/anodb/).
[Sources](https://github.com/zx80/anodb),
[documentation](https://zx80.github.io/anodb/) and
[issues](https://github.com/zx80/anodb/issues)
are available on [GitHub](https://github.com/).

## TODO

- make it work with "with", i.e. provide relevant __enter__ and __exit__?
- sync drivers with aiosql?
- sync version numbering with aiosql?
- add something about caching?
- remove psycopg2 exclusion for python 3.13 and pypy 3.10 when/if possible.

## 12.0 on 2024-09-07

- improve option versatility to better deal with various database drivers:
  - support `conn_args` and `conn_kwargs` for connect.
  - support `adapter_args` and `adapter_kwargs` for adapter,
    which is forwarded to cursor creation by default.
- improve documentation.
- drop buggy mypy checks.

## 11.0 on 2024-08-17

- Improved pytest tests.
- Use an AnoDB specific exception for generated errors.
- Do not allow to override DB methods (eg `commit`, `close`…).
- Add test about name rejections.
- Add attribute access example to documentation.

## 10.4 on 2024-08-15

- Fix deprecation warning for _Python 3.13_.

## 10.3 on 2024-08-03

- Set debug verbosity when debugging.
- Add _Python 3.13_ and _PyPy 3.10_ testing in GitHub CI.

## 10.2 on 2024-07-31

- Improve internal logging infrastructure.
- Add counter to help identify DB objects.

## 10.1 on 2024-06-04

- Improve README introductory example and run it in tests.
- Add license section to documentation.

## 10.0 on 2024-03-02

- Add `attribute` parameter forwarded to AioSQL _10.0_.
- Use iso format.
- Note: the attribute feature does not seem to work with _pg8000_, for now.

## 9.11 on 2024-03-02

- Do not str-ize undefined timestamps.

## 9.10 on 2024-02-27

- Improve stats data.

## 9.9 on 2024-02-26

- Add `_stats` method to generate JSON-compatible stats.

## 9.8 on 2024-02-21

- More verbose str.

## 9.7 on 2024-02-21

- Collect and show more internal stats.

## 9.6 on 2024-02-20

- Possibly reconnect after a `close`?

## 9.5 on 2024-02-17

- Reconnection refactoring.
- Fix sqlite3 in-memory test.

## 9.4 on 2024-02-13

- Add `exception` parameter to `DB` constructor.
- Improved coverage tests.

## 9.3 on 2024-02-10

- Rename `query` parameter to avoid name collisions.
- Allow Pytest _8_.
- Update doc.
- Add `pyright` type checking to CI.

## 9.2 on 2024-01-28

- Update CI script.
- Forward `kwargs_only` option to AioSQL.
- Avoid Pytest _8_.

## 9.1 on 2023-12-09

- Simpler CI script.
- Improved doc and tests.
- Simpler version code.

## 9.0 on 2023-11-19

- Throttle reconnection attempts from 0.001 to 30.0 seconds.
- Use database exceptions instead of generic `Exception`.
- Generic package loading.
- Add Python _3.12_ tests.

## 8.2 on 2023-07-15

- Improve doc wrt connection creation.
- Fix `pymarkdown` check.

## 8.1 on 2023-06-16

- Fix empty driver name.
- Add version dates.

## 8.0 on 2023-06-16

- Rename `master` to `main`.
- Use `pyproject.toml`
- Fix tests for `aiosql` *8.0* which returns generators.
- Drop support for Python *3.8* and *3.9* for simpler typing.
- Add support for `duckdb`

## 7.3 on 2023-01-21

- Drop `None` from `DB` initialization default values.
- Allow `queries` to be a list of files.

## 7.2 on 2022-12-11

- Fix issue with `mariadb`.
- Improve documentation for `github.io`.

## 7.1 on 2022-11-12

- Test with Python *3.12*.

## 7.0 on 2022-10-26

- Add support for MariaDB driver: `mariadb`.
- Make `connect` return the underlying connection.
- Improved documentation.

## 6.1 on 2022-09-11

- Add GitHub CI configuration.
- Add Markdown checks.
- More badges.

## 6.0 on 2022-08-08

- Make connection string parameter optional, as some drivers do not need it.
- Add support for MySQL drivers: `pymysql`, `mysqlclient`, `mysql-connector`.
- Add support for Postgres drivers: `pygresql`, `pg8000`.
- Improved documentation.
- Improved tests.

## 5.0 on 2022-07-10

- Improve `Makefile`.
- Get `aiosql` version.
- Simplify code.
- Sync driver support with aiosql 4.0.
- Require 100% coverage.

## 4.2.1 on 2022-01-16

- Just fix doc date.

## 4.2.0 on 2022-01-16

- Put back `__version__` automatic extraction from package.
- Add `__version__` attribute to DB class.
- Refactor tests.

## 4.1.0 on 2021-12-12

- Add untested support for MySQL through `aiosql_mysql`.
- Temporary work around an issue between `pkg_resources`, `typing_extensions` and `aiosql`.

## 4.0.2 on 2021-12-12

- Add type hint for mypy.

## 4.0.1 on 2021-12-11

- Add package `__version__`.
- Minor update for `pytest_postgresql` 4.0.0.

## 4.0 on 2021-10-14

- Add [psycopg 3](https://www.psycopg.org/psycopg3/) support, and make it the
default for Postgres.

## 3.0 on 2021-04-20

- Package as a simple module.
- Use simpler `setup.cfg` packaging.
- Include tests in package.
- Add coverage test and make test coverage reach 100%.

## 2.2 on 2021-02-20

- Setup explicit logger instead of relying on default.

## 2.1 on 2021-02-14

- Make `cursor()` reconnect if needed.

- Add automatic reconnection tests.

## 2.0 on 2021-02-13

- Swith from `AnoSQL` to `AioSQL`.

## 1.3 on 2020-08-02

- Make `options` accept different types.

- Make `queries` optional, and allow to load from files or strings.

## 1.2 on 2020-07-31

- Add `options` string parameter to constructor.

## 1.1 on 2020-07-28

- Add `**conn_options` parameter to constructor.

- Add `cursor()` method.

## 1.0 on 2020-07-27

- Initial release.
