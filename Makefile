SHELL	= /bin/bash
.ONESHELL:

MODULE	= anodb
PYTHON	= python
PIP		= venv/bin/pip

.PHONY: check check.mypy check.flake8 check.black check.pytest check.coverage check.pymarkdown
check: check.mypy check.flake8 check.black check.pytest check.coverage check.pymarkdown

check.mypy: $(MODULE).egg-info
	source venv/bin/activate
	mypy $(MODULE).py

check.flake8:
	source venv/bin/activate
	flake8 --ignore=E127,E402,E501,W503 $(MODULE).py

check.black:
	source venv/bin/activate
	black --check $(MODULE).py test/test_anodb.py

check.pytest: $(MODULE).egg-info
	source venv/bin/activate
	$(MAKE) -C test check

check.coverage: $(MODULE).egg-info
	source venv/bin/activate
	$(MAKE) -C test coverage

check.pymarkdown:
	source venv/bin/activate
	pymarkdown scan *.md

.PHONY: clean clean.venv
clean:
	$(RM) -r __pycache__ */__pycache__ *.egg-info dist build .mypy_cache .pytest_cache
	$(MAKE) -C test clean

clean.venv: clean
	$(RM) -r venv

# venv
$(MODULE).egg-info: venv
	$(PIP) install -e .

venv:
	$(PYTHON) -m venv venv
	$(PIP) install -U pip

.PHONY: venv.dev
venv.dev: $(MODULE).egg-info
	$(PIP) install -r dev-requirements.txt

venv.dev: $(MODULE).egg-info

# distribution
dist:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: publish
publish: dist
	# provide pypi ids in ~/.pypirc
	twine upload --repository $(MODULE) dist/*
