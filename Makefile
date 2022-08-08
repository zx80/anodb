SHELL	= /bin/bash
.ONESHELL:

MODULE	= anodb
PYTHON	= python
PIP		= venv/bin/pip

.PHONY: check check.mypy check.flake8 check.black check.pytest check.coverage
check: check.mypy check.flake8 check.black check.pytest check.coverage

check.mypy: $(MODULE).egg-info
	source venv/bin/activate
	mypy $(MODULE).py

check.flake8:
	source venv/bin/activate
	flake8 --ignore=E127,E402,E501,W503 $(MODULE).py

check.black:
	source venv/bin/activate
	black --check $(MODULE).py

check.pytest: $(MODULE).egg-info
	source venv/bin/activate
	$(MAKE) -C test check

check.coverage: $(MODULE).egg-info
	source venv/bin/activate
	$(MAKE) -C test coverage

.PHONY: clean clean.venv
clean:
	$(RM) -r __pycache__ */__pycache__ *.egg-info dist build .mypy_cache .pytest_cache
	$(MAKE) -C test clean

clean.venv: clean
	$(RM) -r venv

.PHONY: install
install: $(MODULE).egg-info

$(MODULE).egg-info: venv
	$(PIP) install -e .

venv:
	$(PYTHON) -m venv venv
	$(PIP) install wheel pytest coverage flake8 black
	$(PIP) install pytest-postgresql psycopg2 psycopg pygresql pg8000
	$(PIP) install pytest-mysql mysqlclient pymysql mysql-connector

dist:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: publish
publish: dist
	# provide pypi ids in ~/.pypirc
	twine upload --repository $(MODULE) dist/*
