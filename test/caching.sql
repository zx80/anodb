-- name: ran$
-- the point is to detect caching by caching a volatile function
-- CACHED
SELECT RANDOM();

-- name: len^
-- CACHED
SELECT LENGTH(:s), :s, TRUE;

-- name: gen
-- CACHED
WITH RECURSIVE gens(i) AS (
  SELECT 1
    UNION
  SELECT i + 1
  FROM gens
  WHERE i < :n
)
SELECT i, i*(i+1)/2, i*(i+1)*(i+2)/6
  FROM gens
  ORDER BY 1;

-- name: bad#
-- CACHED should be ignored for a non-select
CREATE TABLE IF NOT EXISTS should_not_cache_non_select(id INTEGER);
DROP TABLE IF EXISTS should_not_cache_non_select;
