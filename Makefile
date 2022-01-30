SHELL	= /bin/bash
.ONESHELL:

MODULE	= anodb
PYTHON	= python
PIP		= venv/bin/pip

.PHONY: check
check: install
	. venv/bin/activate
	type $(PYTHON)
	mypy $(MODULE).py
	flake8 --ignore=E127 $(MODULE).py
	cd test && make check

.PHONY: clean clean-venv
clean:
	$(RM) -r __pycache__ */__pycache__ *.egg-info dist build .mypy_cache .pytest_cache

clean-venv:
	$(RM) -r venv

.PHONY: install
install: $(MODULE).egg-info

$(MODULE).egg-info: venv
	$(PIP) install -e .

venv:
	$(PYTHON) -m venv venv
	$(PIP) install wheel pytest coverage
	$(PIP) install pytest-postgresql psycopg2 psycopg pymysql

dist:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: publish
publish: dist
	# provide pypi login/pw…
	twine upload --repository $(MODULE) dist/*
