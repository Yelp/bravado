.PHONY: all install test tests clean

all: test

build:
	./setup.py bdist_egg

dev: clean
	./setup.py develop

install:
	pip install .

test:
	tox

tests: test

clean:
	@rm -fr .tox
	@rm -fr build
	@rm -fr dist
	@rm -fr docs/build
	@rm -fr *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
