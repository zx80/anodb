SHELL   = /bin/bash
.ONESHELL:

PYTEST	= pytest --log-level=debug --capture=tee-sys
PYTOPT	=

.PHONY: check
check:
	source ../venv/bin/activate
	export PGCLIENTENCODING="UTF8"
	$(PYTEST) $(PYTOPT)

.PHONY: coverage
coverage:
	source ../venv/bin/activate
	export PGCLIENTENCODING="UTF8"
	coverage run -m $(PYTEST) $(PYTOPT)
	coverage html ../anodb.py
	coverage report --fail-under=100 --show-missing --precision=1 ../anodb.py

.PHONY: clean
clean:
	$(RM) -r __pycache__ htmlcov .mypy_cache
	$(RM) .coverage
