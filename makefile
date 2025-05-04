.PHONY: test
test:
	PYTHONPATH=titan coverage run -m pytest

.PHONY: html
html:
	coverage html