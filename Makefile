.ONESHELL:

.PHONY: check
check: venv
	. venv/bin/activate
	type python3
	mypy anodb.py
	flake8 anodb.py
	cd test && make check

.PHONY: clean
clean:
	$(RM) -r venv __pycache__ */__pycache__ *.egg-info dist build .mypy_cache .pytest_cache

.PHONY: install
install:
	pip3 install -e .

venv:
	python3 -m venv venv
	venv/bin/pip install wheel pytest pytest-postgresql psycopg2 coverage
	venv/bin/pip install --pre psycopg[binary,pool] psycopg-c
	venv/bin/pip install -e .

dist:
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish: dist
	# provide pypi login/pw…
	twine upload --repository anodb dist/*
