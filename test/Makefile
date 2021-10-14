.ONESHELL:

PYTEST	= pytest --log-level=debug --capture=tee-sys

.PHONY: check check-pg check-pg2
check-pg:
	export PSYCOPG=psycopg
	$(PYTEST)

check-pg2:
	export PSYCOPG=psycopg2
	$(PYTEST)

check:
	$(MAKE) check-pg
	$(MAKE) check-pg2

.PHONY: coverage
coverage:
	coverage run -m $(PYTEST)
	coverage html anodb.py

.PHONY: clean
clean:
	$(RM) -r __pycache__ htmlcov .mypy_cache
	$(RM) .coverage
