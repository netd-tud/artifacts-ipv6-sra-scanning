#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = artifacts-ipv6-sra-scanning
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python3
SHELL := /bin/bash

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find ./notebooks/ -type f -name "*.html" -delete
	find ./reports/figures/ -type f -name "*.pdf" -delete
	find ./reports/figures/ -type f -name "*.png" -delete

## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

python_env:
	$(PYTHON_INTERPRETER) -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

notebooks = notebooks/tables.ipynb
notebooks_html = notebooks/tables.html

%.html: %.ipynb
	jupyter nbconvert $(NBCONVERT_PARAMS) --to html $<

tables: NBCONVERT_PARAMS=--execute
tables: $(notebooks_html)

## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) artifacts_ipv6_sra_scanning/dataset.py

.PHONY: plots
plots: requirements
	$(PYTHON_INTERPRETER) artifacts_ipv6_sra_scanning/plots.py

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
