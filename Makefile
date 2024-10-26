SHELL	= /bin/bash
.ONESHELL:

MODULE	= anodb
PYTHON	= python
PIP		= pip

.PHONY: check
check: check.pyright check.ruff check.pytest check.coverage check.pymarkdown

.PHONY: check.mypy
check.mypy: venv
	source venv/bin/activate
	mypy $(MODULE).py

.PHONY: check.pyright
check.pyright: venv
	source venv/bin/activate
	pyright $(MODULE).py

IGNORE  = E227,E402,E501

.PHONY: check.flake8
check.flake8: venv
	source venv/bin/activate
	flake8 --ignore=E127,W503,W504,$(IGNORE) $(MODULE).py

.PHONY: check.ruff
check.ruff: venv
	source venv/bin/activate
	ruff check --ignore=$(IGNORE) $(MODULE).py

.PHONY: check.black
check.black: venv
	source venv/bin/activate
	black --check $(MODULE).py test/test_anodb.py

.PHONY: check.pytest
check.pytest: venv
	source venv/bin/activate
	$(MAKE) -C test check

.PHONY: check.coverage
check.coverage: venv
	source venv/bin/activate
	$(MAKE) -C test coverage

.PHONY: check.pymarkdown
check.pymarkdown: venv
	source venv/bin/activate
	pymarkdown -d MD013 scan *.md

# targets for development environment
.PHONY: dev
dev: venv/.dev

.PHONY: clean.dev
clean.dev: clean.venv

# cleanup
.PHONY: clean
clean:
	$(RM) -r __pycache__ */__pycache__ dist build .mypy_cache .pytest_cache .ruff_cache
	$(MAKE) -C test clean

.PHONY: clean.venv
clean.venv: clean
	$(RM) -r venv *.egg-info

# venv
venv:
	$(PYTHON) -m venv venv
	source venv/bin/activate
	$(PIP) install -U pip
	$(PIP) install -e .

venv/.dev: venv
	source venv/bin/activate
	$(PIP) install -e .[postgres,dev]
	touch $@

.PHONY: venv.check
venv.check: venv/.dev
	source venv/bin/activate
	pip install -e .[mysql]

venv/.pub: venv/.dev
	source venv/bin/activate
	$(PIP) install -e .[pub]
	touch $@

# distribution
dist: venv/.pub
	source venv/bin/activate
	$(PYTHON) -m build

.PHONY: publish
publish: dist
	# provide pypi ids in ~/.pypirc
	echo ./venv/bin/twine upload dist/*
