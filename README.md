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

db.do_some_stuff(key=1, val='hello world')
res = db.do_some_more(key=2, val='hello world')
db.commit()

db.close()
```
