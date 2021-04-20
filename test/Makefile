.ONESHELL:

PYTEST	= pytest --log-level=debug --capture=tee-sys

.PHONY: check
check:
	$(PYTEST)

.PHONY: coverage
coverage:
	coverage run -m $(PYTEST)
	coverage html anodb.py

.PHONY: clean
clean:
	$(RM) -r __pycache__ htmlcov .mypy_cache
	$(RM) .coverage
