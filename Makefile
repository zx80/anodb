.PHONY: check
check:
	pytest-3 test-anodb.py

.PHONY: clean
clean:
	$(RM) -r venv __pycache__ anodb.egg-info

.PHONY: install
install:
	pip3 install -e .

venv:
	python3 -m venv venv
