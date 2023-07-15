SHELL	= /bin/bash
.ONESHELL:

MODULE	= anodb
PYTHON	= python
PIP		= pip

.PHONY: check check.mypy check.flake8 check.black check.pytest check.coverage check.pymarkdown
check: check.mypy check.flake8 check.pytest check.coverage check.pymarkdown

check.mypy: venv
	source venv/bin/activate
	mypy $(MODULE).py

check.flake8: venv
	source venv/bin/activate
	flake8 --ignore=E127,E227,E402,E501,W503 $(MODULE).py

check.black: venv
	source venv/bin/activate
	black --check $(MODULE).py test/test_anodb.py

check.pytest: venv
	source venv/bin/activate
	$(MAKE) -C test check

check.coverage: venv
	source venv/bin/activate
	$(MAKE) -C test coverage

check.pymarkdown: venv
	source venv/bin/activate
	pymarkdown -d MD013 scan *.md

.PHONY: clean clean.venv
clean:
	$(RM) -r __pycache__ */__pycache__ dist build .mypy_cache .pytest_cache
	$(MAKE) -C test clean

clean.venv: clean
	$(RM) -r venv *.egg-info

# venv
venv:
	$(PYTHON) -m venv venv
	source venv/bin/activate
	$(PIP) install -U pip
	$(PIP) install -e .[dev,pub,postgres]

# distribution
dist: venv
	source venv/bin/activate
	$(PYTHON) -m build

.PHONY: publish
publish: dist
	# provide pypi ids in ~/.pypirc
	echo twine upload dist/*
