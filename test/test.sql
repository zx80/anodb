-- name: create-foo#
-- create table foo
CREATE TABLE Foo(pk INT PRIMARY KEY, val TEXT NOT NULL);

-- name: drop-foo#
-- drop table foo
DROP TABLE IF EXISTS Foo;

-- name: count-foo()^
-- count number of items in foo
SELECT COUNT(*) FROM Foo;

-- name: insert-foo(pk, val)!
-- insert one item into foo
INSERT INTO Foo(pk, val) VALUES (:pk, :val);

-- name: select-foo-pk(pk)
-- extract one value from foo
SELECT val FROM Foo WHERE pk = :pk;

-- name: select-foo-all()
-- extract all values from foo
SELECT pk, val FROM Foo ORDER BY 1;

-- name: update-foo-pk(pk, val)!
-- update a value in foo
UPDATE Foo SET val = :val WHERE pk = :pk;

-- name: delete-foo-pk(pk)!
-- delete an item in foo
DELETE FROM Foo WHERE pk = :pk;

-- name: delete-foo-all()!
-- delete all items
DELETE FROM Foo WHERE TRUE;

-- name: hello-world()^
-- simple hello world expression
SELECT 'hello world!';

-- name: kill-me-pg()!
-- kill current backend process, to test reconnections
SELECT pg_terminate_backend(pg_backend_pid());

-- name: syntax-error(s)$
SELECT :s + ;

-- name: module(x)$
SELECT SQRT(:x.real * :x.real + :x.imag * :x.imag);

--
-- README example
--

-- name: create_stuff#
CREATE TABLE Stuff(key INTEGER PRIMARY KEY, val TEXT NOT NULL);

-- name: add_stuff(key, val)!
INSERT INTO Stuff(key, val) VALUES (:key, :val);

-- name: change_stuff(key, val)!
UPDATE Stuff SET val = :val WHERE key = :key;

-- name: get_stuff(key)^
SELECT * FROM Stuff WHERE key = :key;

-- name: get_all_stuff()
SELECT * FROM Stuff ORDER BY 1;

-- name: compute-norm(c)$
SELECT SQRT(:c.real * :c.real + :c.imag * :c.imag);
