.PHONY: test
test:
	PYTHONPATH=titan coverage run -m pytest

.PHONY: html
html:
	coverage html

.PHONY: report
report:
	coverage report