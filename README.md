# AnoDB

Convenient Wrapper around [anosql](https://github.com/honza/anosql)
and a [Database Connection](https://www.python.org/dev/peps/pep-0249).

## Description

This class creates a persistent database connection and imports
SQL queries from a file.

## Example

```Python
import anodb
db = anodb.DB('sqlite3', 'test.db', 'test.sql')

db.do_some_insert(key=1, val='hello')
res = db.do_some_update(key=1, val='world')
db.commit()

db.close()
```

## Versions

### 1.3

Make `options` accept different types.

Make `queries` optional, and allow to load from a file or a string.

### 1.2

Add `options` string parameter to constructor.

### 1.1

Add `**conn_options` parameter to constructor.

Add `cursor()` method.

### 1.0

Initial release.
