.ONESHELL:

.PHONY: check
check: venv
	. venv/bin/activate
	type python3
	mypy anodb
	flake8 anodb
	cd tests && pytest test.py

.PHONY: clean
clean:
	$(RM) -r venv __pycache__ *.egg-info dist build */__pycache__ .mypy_cache .pytest_cache

.PHONY: install
install:
	pip3 install -e .

venv:
	python3 -m venv venv
	venv/bin/pip3 install wheel ipython pytest pytest-postgresql psycopg2
	venv/bin/pip3 install -e .

dist:
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish: dist
	# provide pypi login/pw…
	twine upload dist/*
