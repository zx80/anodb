import pytest  # type: ignore
import anodb
import re
from os import environ as ENV

# check that the db connection cursor works
def run_42(db: anodb.DB):
    assert db is not None
    cur = db.cursor()
    cur.execute("SELECT 42 AS fourtytwo")
    assert cur.description[0][0] == "fourtytwo"
    assert cur.fetchone()[0] == 42
    db.close()
    db.connect()

# do various stuff, common to sqlite & pg tests
def run_stuff(db: anodb.DB):
    assert db is not None
    # create table Foo
    db.create_foo()
    # with some data
    assert db.count_foo()[0] == 0
    db.insert_foo(pk=1, val="one")
    assert db.count_foo()[0] == 1
    db.insert_foo(pk=2, val="two")
    db.commit()
    # more checks
    assert db.count_foo()[0] == 2
    assert re.search(r"two", db.select_foo_pk(pk=2)[0][0])
    db.update_foo_pk(pk=2, val="deux")
    db.delete_foo_pk(pk=1)
    db.commit()
    assert db.count_foo()[0] == 1
    assert re.search(r"deux", db.select_foo_pk(pk=2)[0][0])
    # data cleanup
    db.delete_foo_all()
    db.commit()
    assert db.count_foo()[0] == 0
    # check rollback
    db.insert_foo(pk=3, val="three")
    db.insert_foo(pk=4, val="four")
    db.insert_foo(pk=5, val="five")
    assert db.count_foo()[0] == 3
    db.rollback()
    assert db.count_foo()[0] == 0
    # table cleanup
    db.drop_foo()
    db.commit()
    # check reconnection
    db.close()
    db.connect()
    run_42(db)

# sqlite memory test
def test_sqlite():
    db = anodb.DB("sqlite", ":memory:", "test.sql", '{"check_same_thread":False}')
    run_stuff(db)
    db.close()

# sqlite memory test with options
def test_options():
    db = anodb.DB("sqlite", ":memory:", "test.sql",
                  timeout=10, check_same_thread=False, isolation_level=None)
    run_42(db)
    db.close()
    db = anodb.DB("sqlite", ":memory:", "test.sql",
                  {"timeout":10, "check_same_thread":False, "isolation_level":None})
    run_42(db)
    db.close()
    db = anodb.DB("sqlite", ":memory:", "test.sql",
                  '{"timeout":10, "check_same_thread":False, "isolation_level":None}')
    run_42(db)
    db.close()


def run_test_sql(driver, dsn):
    db = anodb.DB(driver, dsn, "test.sql")
    run_stuff(db)
    db.close()
    return db


# NOTE We do not want to use the postgresql fixture because we want to test
# that anodb creates and recreates its own connections.
@pytest.fixture
def pg_dsn(postgresql_proc):
    p = postgresql_proc
    # NOTE pg.dbname is not created, use postgres own database instead
    yield f"postgres://{p.user}:{p.password}@{p.host}:{p.port}/{p.user}"


# postgres basic test
# pg_dsn is the string returned by the above fixture
# test may use psycopg or psycopg2 driver depending on $PSYCOPG
def test_postgres(pg_dsn):
    assert re.match(r"postgres://", pg_dsn)
    driver = ENV.get("PSYCOPG", "psycopg")  # default to psycopg 3
    assert driver in ("psycopg", "psycopg2")
    db = run_test_sql(driver, pg_dsn)
    # further checks on the db object:
    if driver == "psycopg":
        assert re.match(r"3\.", db._db_version)
    elif driver == "psycopg2":
        assert re.match(r"2\.", db._db_version)
    else:
        assert False, f"unsupported db version: {db._db} {db._db_version}"
    # check auto-reconnect for postgres
    db.connect()
    try:
        db.kill_me_pg()
        assert False, "1. backend should have been killed"
    except:
        assert True, "1. backend was killed"
    # should reconnect automatically
    assert db.hello_world()[0] == "hello world!"
    # again from cursor
    try:
        db.kill_me_pg()
        assert False, "2. backend should have been killed"
    except:
        assert True, "2. backend was killed"
    run_42(db)
    db.close()

# mysql tests
@pytest.fixture
def my_dsn(mysql_proc):
    p = mysql_proc
    yield { "user": p.user, "host": p.host, "port": p.port }

@pytest.mark.skip("wip")
def test_mysql(my_dsn):
    driver = ENV.get("MYSQL", "mysqldb")
    assert driver in ("mysqldb", "pymysql")
    db = run_test_sql(driver, my_dsn)
    db.close()

# test from-string queries
def test_from_str():
    db = anodb.DB("sqlite", ":memory:")
    assert "connection to sqlite" in str(db)
    db.add_queries_from_str("-- name: next\nSELECT :arg + 1 AS next;\n")
    assert db.next(arg=1)[0][0] == 2
    db.add_queries_from_str("-- name: prev\nSELECT :arg - 1 AS prev;\n")
    assert db.next(arg=41)[0][0] == 42
    assert db.prev(arg=42)[0][0] == 41
    # override previous definition
    db.add_queries_from_str("-- name: foo\nSELECT :arg + 42 AS foo;\n")
    assert db.foo(arg=0)[0][0] == 42
    db.add_queries_from_str("-- name: foo\nSELECT :arg - 42 AS foo;\n")
    assert db.foo(arg=42)[0][0] == 0
    assert db.next(arg=42)[0][0] == 43
    assert db.prev(arg=43)[0][0] == 42
    assert sorted(db._available_queries) == ["foo", "foo_cursor", "next", "next_cursor", "prev", "prev_cursor"]
    db.__del__()

# test non existing database
def test_misc():
    try:
        db = anodb.DB("foodb", "anodb", "test.sql")
        assert False, "there is no foodb"
    except Exception as err:
        assert True, "foodb is not supported"
