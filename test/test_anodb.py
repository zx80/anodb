import pytest  # type: ignore
import anodb
import re
from os import environ as ENV
import logging

log = logging.getLogger(__name__)

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
    log.debug(f"driver={driver} dsn={dsn}")
    if isinstance(dsn, str):
        db = anodb.DB(driver, dsn, "test.sql")
    elif isinstance(dsn, dict):
        db = anodb.DB(driver, None, "test.sql", **dsn)
    else:
        raise Exception(f"unexpected dsn type: {type(dsn)}")
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
def run_postgres(driver, dsn, skip_kill=False):
    if driver in ("psycopg", "psycopg2"):
        assert re.match(r"postgres://", dsn)
    assert driver in ("psycopg", "psycopg2", "pygresql", "pg8000")
    db = run_test_sql(driver, dsn)
    # further checks on the db object:
    if driver == "psycopg":
        assert re.match(r"3\.", db._db_version)
    elif driver == "psycopg2":
        assert re.match(r"2\.", db._db_version)
    elif driver in ("pygresql", "pg8000"):
        pass
    else:
        assert False, f"unsupported db version: {db._db} {db._db_version}"
    # check auto-reconnect for postgres
    db.connect()
    if skip_kill:
        log.warning(f"skipping kill test for {driver}")
        return
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


def has_module(name):
    try:
        __import__(name)
        return True
    except ModuleNotFoundError:
        return False


@pytest.mark.skipif(not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test")
@pytest.mark.skipif(not has_module("psycopg"), reason="missing psycopg for test")
def test_psycopg(pg_dsn):
    run_postgres("psycopg", pg_dsn)


@pytest.mark.skipif(not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test")
@pytest.mark.skipif(not has_module("psycopg2"), reason="missing psycopg2 for test")
def test_psycopg2(pg_dsn):
    run_postgres("psycopg2", pg_dsn)


@pytest.mark.skipif(not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test")
@pytest.mark.skipif(not has_module("pgdb"), reason="missing pgdb for test")
def test_pygresql(postgresql_proc):
    pp = postgresql_proc
    dsn = {
        "host": f"{pp.host}:{pp.port}",
        "user": pp.user,
        "password": pp.password,
        "database": pp.user,
    }
    log.debug(f"dsn={dsn}")
    run_postgres("pygresql", dsn, skip_kill=True)


@pytest.mark.skipif(not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test")
@pytest.mark.skipif(not has_module("pg8000"), reason="missing pg8000 for test")
def test_pg8000(postgresql_proc):
    pp = postgresql_proc
    dsn = {
        "host": pp.host,
        "port": pp.port,
        "user": pp.user,
        "password": pp.password,
        "database": pp.user,
    }
    log.debug(f"dsn={dsn}")
    run_postgres("pg8000", dsn, skip_kill=True)


# mysql tests
@pytest.fixture
def my_dsn(mysql_proc):
    p = mysql_proc
    log.debug(f"unix socket={p.unixsocket} port={p.port}")
    yield { "user": p.user, "host": p.host, "port": p.port, "password": "" }


@pytest.mark.skipif(not has_module("pytest_mysql"), reason="missing pytest_mysql for test")
@pytest.mark.skipif(not has_module("MySQLdb"), reason="missing MySQLdb for test")
def test_mysqldb(my_dsn, mysql, mysql_proc):
    my_dsn["database"] = "test"
    if mysql_proc.unixsocket:
        my_dsn["unix_socket"] = mysql_proc.unixsocket
        del my_dsn["port"]
    db = run_test_sql("MySQLdb", my_dsn)


@pytest.mark.skipif(not has_module("pytest_mysql"), reason="missing pytest_mysql for test")
@pytest.mark.skipif(not has_module("pymysql"), reason="missing pymysql for test")
def test_pymysql(my_dsn, mysql):
    my_dsn["database"] = "test"
    db = run_test_sql("pymysql", my_dsn)


@pytest.mark.skipif(not has_module("pytest_mysql"), reason="missing pytest_mysql for test")
@pytest.mark.skipif(not has_module("mysql.connector"), reason="missing mysql.connector for test")
def test_myco(my_dsn, mysql):
    my_dsn["database"] = "test"
    db = run_test_sql("mysql-connector", my_dsn)


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

# test non existing database and other miscellanous errors
def test_misc():
    try:
        db = anodb.DB("foodb", "anodb", "test.sql")
        assert False, "there is no foodb"
    except Exception as err:
        assert True, "foodb is not supported"
    try:
        db = anodb.DB("psycopg", None, "test.sql", options=False)
        assert False, "bad type for options"
    except Exception as err:
        assert True, f"oops: {err}"
