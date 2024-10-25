-- name: rand$
-- the point is to detect caching by caching a volatile function
-- CACHED
SELECT RANDOM();

-- name: len^
-- CACHED
SELECT LENGTH(:s), :s;
