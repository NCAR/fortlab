NAME := fortlab
DOCREPO := ../fortlabdoc

.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 ${NAME} tests

test: ## run tests quickly with the default Python
	python setup.py test

test-all: ## run tests on every Python version with tox
	tox

test-admin: ## run tests on admin tasks
	$(MAKE) -C tests -f admin_task_tests.mak

coverage: ## check code coverage quickly with the default Python
	coverage run --source ${NAME} -m unittest
	coverage report -m
	#coverage html
	#$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML docsumentation, including API docs
	rm -f docs/${NAME}.rst
	rm -f docs/modules.rst
	#sphinx-apidocs -o docs/ ${NAME}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html

pushdoc: docs
	cp -rf docs/build/html/. ${DOCREPO}
	cd ${DOCREPO}; git add . ; git commit -m "pushed new updates"; git push origin master
	
servedoc: docs ## compile the docss watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*
	#/Users/youngsun/Library/Python/2.7/bin/twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel --universal
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

dev-install: clean ## install the package locally
	python setup.py develop
	#python setup.py develop --user --user is not work with virtualenv

####### NOTES #######

# >>> pip install Sphinx
# >>> pip install sphinx_rtd_theme
#
ncl:
	pyloco fortlab/data/ncread.py tests/data/sresa1b_ncar_ccsm3-example.nc --import fortlab/core/nctools_util.py -l

ncv:
	pyloco fortlab/data/ncread.py tests/data/sresa1b_ncar_ccsm3-example.nc --import fortlab/core/nctools_util.py -i ua

plot:
	pyloco fortlab/data/ncread.py tests/data/sresa1b_ncar_ccsm3-example.nc --import fortlab/core/nctools_util.py -v ua -- fortlab/plot/ncplot.py -p 'lon,lat,ua@contourf' -s cont1.png -t 'ua.long_name'
	xdg-open cont1.png
