.ONESHELL:

.PHONY: check
check: venv
	mypy anodb
	. venv/bin/activate
	type python3
	mypy anodb
	cd tests && pytest-3 test-anodb.py

.PHONY: clean
clean:
	$(RM) -r venv __pycache__ anodb.egg-info dist build */__pycache__ .mypy_cache .pytest_cache

.PHONY: install
install:
	pip3 install -e .

venv:
	python3 -m venv venv
	venv/bin/pip3 install wheel
	venv/bin/pip3 install -e .

dist:
	python3 setup.py sdist bdist_wheel
