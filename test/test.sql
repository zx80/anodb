-- name: create-foo!
-- create table foo
CREATE TABLE Foo(pk INT PRIMARY KEY, val TEXT NOT NULL);

-- name: drop-foo! 
-- drop table foo
DROP TABLE IF EXISTS Foo;

-- name: count-foo^ 
-- count number of items in foo
SELECT COUNT(*) FROM Foo;

-- name: insert-foo!		
-- insert one item into foo
INSERT INTO Foo(pk, val) VALUES (:pk, :val);

-- name: select-foo-pk
-- extract one value from foo
SELECT val FROM Foo WHERE pk = :pk;

-- name: select-foo-all
-- extract all values from foo
SELECT pk, val FROM Foo ORDER BY 1;

-- name: update-foo-pk!
-- update a value in foo
UPDATE Foo SET val = :val WHERE pk = :pk;

-- name: delete-foo-pk!
-- delete an item in foo
DELETE FROM Foo WHERE pk = :pk;

-- name: delete-foo-all!
-- delete all items
DELETE FROM Foo WHERE TRUE;

-- name: hello-world^
-- simple hello world expression
SELECT 'hello world!';

-- name: kill-me-pg!
-- kill current backend process, to test reconnections
SELECT pg_terminate_backend(pg_backend_pid());

-- name: syntax-error$
SELECT :s + ;

-- name: module$
SELECT SQRT(:x.real * :x.real + :x.imag * :x.imag);

--
-- README example
--

-- name: create_stuff#
CREATE TABLE Stuff(key INTEGER PRIMARY KEY, val TEXT NOT NULL);

-- name: do_some_select^
SELECT * FROM Stuff WHERE key = :key;

-- name: do_some_insert!
INSERT INTO Stuff(key, val) VALUES (:key, :val);

-- name: do_some_update!
UPDATE Stuff SET val = :val WHERE key = :key;

-- name: compute-norm$
SELECT SQRT(:c.real * :c.real + :c.imag * :c.imag);
