# AioDB

Convenient Wrapper around [aiosql](https://github.com/nackjicholson/aiosql)
and a [Database Connection](https://www.python.org/dev/peps/pep-0249).

## Description

This class creates a persistent database connection and imports
SQL queries from a file.

## Example

```Python
import aiodb
db = aiodb.DB('sqlite3', 'test.db', 'test.sql')

db.do_some_insert(key=1, val='hello')
db.do_some_update(key=1, val='world')
db.commit()

db.close()
```

## Versions

Not released yet.
