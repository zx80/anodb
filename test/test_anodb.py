import pytest  # type: ignore
import anodb
import sqlite3
import re
from os import environ as ENV
import logging
from pathlib import Path
import shutil
import datetime as dt

log = logging.getLogger(__name__)

# look for actual SQL test file
for f in ["test.sql", "test/test.sql"]:
    if Path(f).exists():
        TEST_SQL = f
assert TEST_SQL


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
def run_stuff(db: anodb.DB, skip_dot=False):
    assert db is not None
    # create table Foo
    db.create_foo()
    # with some data
    assert list(db.count_foo())[0] == 0
    db.insert_foo(pk=1, val="one")
    assert list(db.count_foo())[0] == 1
    db.insert_foo(pk=2, val="two")
    db.commit()
    # more checks
    assert list(db.count_foo())[0] == 2
    assert re.search(r"two", list(db.select_foo_pk(pk=2))[0][0])
    db.update_foo_pk(pk=2, val="deux")
    db.delete_foo_pk(pk=1)
    db.commit()
    assert list(db.count_foo())[0] == 1
    assert re.search(r"deux", list(db.select_foo_pk(pk=2))[0][0])
    # data cleanup
    db.delete_foo_all()
    db.commit()
    assert list(db.count_foo())[0] == 0
    # check rollback
    db.insert_foo(pk=3, val="three")
    db.insert_foo(pk=4, val="four")
    db.insert_foo(pk=5, val="five")
    assert list(db.count_foo())[0] == 3
    db.rollback()
    assert list(db.count_foo())[0] == 0
    # table cleanup
    db.drop_foo()
    db.commit()
    # check module
    if not skip_dot:
        assert db.module(x=(3+4j)) == 5.0
        db.commit()
    # check reconnection
    db.close()
    db.connect()
    run_42(db)


# sqlite memory test
def test_sqlite():
    db = anodb.DB("sqlite", ":memory:", TEST_SQL, '{"check_same_thread":False}')
    run_stuff(db)
    db.close()


# sqlite memory test with options
def test_options():
    db = anodb.DB(
        "sqlite",
        ":memory:",
        TEST_SQL,
        timeout=10,
        check_same_thread=False,
        isolation_level=None,
    )
    run_42(db)
    db.close()
    db = anodb.DB(
        "sqlite",
        ":memory:",
        TEST_SQL,
        {"timeout": 10, "check_same_thread": False, "isolation_level": None},
    )
    run_42(db)
    db.close()
    db = anodb.DB(
        "sqlite",
        ":memory:",
        TEST_SQL,
        '{"timeout":10, "check_same_thread":False, "isolation_level":None}',
    )
    run_42(db)
    db.close()


def run_test_sql(driver, dsn, skip_dot=False):
    log.debug(f"driver={driver} dsn={dsn}")
    if isinstance(dsn, str):
        db = anodb.DB(driver, dsn, TEST_SQL)
    elif isinstance(dsn, dict):
        db = anodb.DB(driver, None, TEST_SQL, **dsn)
    else:
        raise Exception(f"unexpected dsn type: {type(dsn)}")
    run_stuff(db, skip_dot)
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
def run_postgres(driver, dsn, skip_kill=False, skip_dot=False):
    if driver in ("psycopg", "psycopg2"):
        assert re.match(r"postgres://", dsn)
    assert driver in ("psycopg", "psycopg2", "pygresql", "pg8000")
    db = run_test_sql(driver, dsn, skip_dot)
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


def has_command(cmd):
    return shutil.which(cmd) is not None


@pytest.mark.skipif(
    not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test"
)
@pytest.mark.skipif(not has_module("psycopg"), reason="missing psycopg for test")
def test_psycopg(pg_dsn):
    run_postgres("psycopg", pg_dsn)


@pytest.mark.skipif(
    not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test"
)
@pytest.mark.skipif(not has_module("psycopg2"), reason="missing psycopg2 for test")
def test_psycopg2(pg_dsn):
    run_postgres("psycopg2", pg_dsn)


@pytest.mark.skipif(
    not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test"
)
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


@pytest.mark.skipif(
    not has_module("pytest_postgresql"), reason="missing pytest_postgresql for test"
)
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
    run_postgres("pg8000", dsn, skip_kill=True, skip_dot=True)


# mysql tests
@pytest.fixture
def my_dsn(mysql_proc):
    p = mysql_proc
    log.debug(f"unix socket={p.unixsocket} port={p.port}")
    yield {"user": p.user, "host": p.host, "port": p.port, "password": ""}


@pytest.mark.skipif(not has_command("mysqld"), reason="missing mysqd for test")
@pytest.mark.skipif(
    not has_module("pytest_mysql"), reason="missing pytest_mysql for test"
)
@pytest.mark.skipif(not has_module("MySQLdb"), reason="missing MySQLdb for test")
def test_mysqldb(my_dsn, mysql, mysql_proc):
    my_dsn["database"] = "test"
    if mysql_proc.unixsocket:
        my_dsn["unix_socket"] = mysql_proc.unixsocket
        del my_dsn["port"]
    db = run_test_sql("MySQLdb", my_dsn)


@pytest.mark.skipif(not has_command("mysqld"), reason="missing mysqd for test")
@pytest.mark.skipif(
    not has_module("pytest_mysql"), reason="missing pytest_mysql for test"
)
@pytest.mark.skipif(not has_module("pymysql"), reason="missing pymysql for test")
def test_pymysql(my_dsn, mysql):
    my_dsn["database"] = "test"
    db = run_test_sql("pymysql", my_dsn)


@pytest.mark.skipif(not has_command("mysqld"), reason="missing mysqd for test")
@pytest.mark.skipif(
    not has_module("pytest_mysql"), reason="missing pytest_mysql for test"
)
@pytest.mark.skipif(
    not has_module("mysql.connector"), reason="missing mysql.connector for test"
)
def test_myco(my_dsn, mysql):
    my_dsn["database"] = "test"
    db = run_test_sql("mysql-connector", my_dsn)


# test from-string queries
def test_from_str():
    db = anodb.DB("sqlite", ":memory:")
    assert "sqlite" in str(db)
    db.add_queries_from_str("-- name: next\nSELECT :arg + 1 AS next;\n")
    assert list(db.next(arg=1))[0][0] == 2
    db.add_queries_from_str("-- name: prev\nSELECT :arg - 1 AS prev;\n")
    assert list(db.next(arg=41))[0][0] == 42
    assert list(db.prev(arg=42))[0][0] == 41
    # override previous definition
    db.add_queries_from_str("-- name: foo\nSELECT :arg + 42 AS foo;\n")
    assert list(db.foo(arg=0))[0][0] == 42
    db.add_queries_from_str("-- name: foo\nSELECT :arg - 42 AS foo;\n")
    assert list(db.foo(arg=42))[0][0] == 0
    assert list(db.next(arg=42))[0][0] == 43
    assert list(db.prev(arg=43))[0][0] == 42
    assert sorted(db._available_queries) == [
        "foo",
        "foo_cursor",
        "next",
        "next_cursor",
        "prev",
        "prev_cursor",
    ]
    db.__del__()


# test non existing database and other miscellanous errors
def test_misc():
    try:
        db = anodb.DB("foodb", "anodb", TEST_SQL)
        assert False, "there is no foodb"
    except Exception as err:
        assert True, "foodb is not supported"
    try:
        db = anodb.DB("psycopg", None, TEST_SQL, options=False)
        assert False, "bad type for options"
    except Exception as err:
        assert True, f"oops: {err}"


class ThriceFail:
    """Always fails thrice before connecting."""

    def __init__(self):
        self._fails = 0

    def connect(self, *args, **kwargs):
        if self._fails < 3:
            self._fails += 1
            raise sqlite3.Error(f"connect intentional failure #{self._fails}")
        else:
            self._fails = 0
            return sqlite3.connect(*args, **kwargs)

    Error = Exception


# NOTE this tests has an unlikely race condition for coverage
def test_reconnect_delays():
    start = dt.datetime.now()
    db = anodb.DB("sqlite", ":memory:", TEST_SQL)
    db.close()
    # replace some stuff for testing
    db._CONNECTION_MIN_DELAY = 0.01
    db._db_pkg = ThriceFail()
    errors = 0
    for _ in range(12):
        try:
            db.connect()
            db.close()
        except sqlite3.Error:
            errors += 1
    assert errors == 9
    end = dt.datetime.now()
    # 0, 1 and 2 ms delays, 3 times
    assert (end - start).total_seconds() >= 0.09


class MyException(BaseException):
    pass


def test_exception():
    db = anodb.DB("sqlite", ":memory:", TEST_SQL, kwargs_only=True, exception=MyException)
    try:
        d = db.syntax_error(s="2024-12-34")
        assert False, f"exception should be raised (d={d})"
    except MyException as e:
        assert True, "good, exception was raised"


def test_readme():
    import anodb
    db = anodb.DB("sqlite3", ":memory:", "test.sql")
    res = db.create_stuff()
    assert res == "DONE"
    res = db.do_some_insert(key=1, val="hello")
    assert res == 1
    res = db.do_some_update(key=1, val="world")
    assert res == 1
    res = db.do_some_select(key=1)
    assert res == (1, "world")
    # not in readme
    res = db.do_some_select(key=2)
    assert res is None
    db.commit()
    db.close()
