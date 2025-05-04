.PHONY: test
test:
	PYTHONPATH=titan coverage run -m pytest

.PHONY: html
html:
	coverage html

.PHONY: report
report:
	coverage report

.PHONY: clean
clean:
	rm -rf htmlcov output
	rm -f .coverage
	rm -f compiler_log.txt