# AnoDB

Convenient Wrapper around [aiosql](https://github.com/nackjicholson/aiosql)
and a [Database Connection](https://www.python.org/dev/peps/pep-0249).

## Description

This class creates a persistent database connection and imports
SQL queries from a file.

If the connection is broken, a new connection is attempted.

Compared do aiosql, the point is not to need to pass a connection
as an argument on each call.

## Example

```Python
import anodb
db = anodb.DB('sqlite3', 'test.db', 'test.sql')

db.do_some_insert(key=1, val='hello')
db.do_some_update(key=1, val='world')
db.commit()

db.close()
```

With file `test.sql` containing something like:

```SQL
-- name: do_some_insert!
INSERT INTO Stuff(key, val) VALUES (:key, :val);

-- name: do_some_update!
UPDATE Stuff SET val = :val WHERE key = :key;
```

## Versions

Sources are available on [GitHub](https://github.com/zx80/anodb).

### 2.1

Make `cursor()` reconnect if needed.

Add automatic reconnection tests.

### 2.0

Swith from AnoSQL to AioSQL.

### 1.3

Make `options` accept different types.

Make `queries` optional, and allow to load from files or strings.

### 1.2

Add `options` string parameter to constructor.

### 1.1

Add `**conn_options` parameter to constructor.

Add `cursor()` method.

### 1.0

Initial release.
