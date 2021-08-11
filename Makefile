.DEFAULT_GOAL := help

# Show this help
help:
ifeq ($(OS), Windows_NT)
	@type "${MAKEFILE_LIST}" | docker run --rm -i xanders/make-help
else
	@cat $(MAKEFILE_LIST) | docker run --rm -i xanders/make-help
endif

# Set source to venv and install packages
install: 
	python3 -m venv venv
	source venv/bin/activate 
	python setup.py

# Run unit tests
test: 
	coverage run -m pytest  -W ignore::UserWarning

# Run unit tests in stepwise manner
stepwise: 
	coverage run -m pytest --sw

# Generate code gutters for vscode	
gutters: 
	coverage xml 

# Generate Coverage Report
coverage: 
	coverage report --fail-under=90


# Runs the test suite, generates code gutters, gives coverage readouts, and runs pylint
full_test: test gutters coverage lint