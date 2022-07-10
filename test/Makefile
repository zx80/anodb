.ONESHELL:

PYTEST	= pytest --log-level=debug --capture=tee-sys
PYTOPT	=

.PHONY: check check-pg check-pg2
check-pg:
	export PSYCOPG=psycopg
	$(PYTEST) $(PYTOPT)

check-pg2:
	export PSYCOPG=psycopg2
	$(PYTEST) $(PYTOPT)

check:
	$(MAKE) check-pg
	$(MAKE) check-pg2

.PHONY: coverage
coverage:
	export PSYCOPG=psycopg
	coverage run -m $(PYTEST) $(PYTOPT)
	export PSYCOPG=psycopg2
	coverage run -a -m $(PYTEST) $(PYTOPT)
	coverage html anodb.py
	coverage report --fail-under=100 anodb.py

.PHONY: clean
clean:
	$(RM) -r __pycache__ htmlcov .mypy_cache
	$(RM) .coverage
