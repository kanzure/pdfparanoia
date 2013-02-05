SHELL := /bin/bash

test:
	nosetests-2.7 -s --verbosity=2

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	find . -type f -name "*.pyc" -exec rm '{}' \;

install:
	python2.7 setup.py install

upload: clean
	python2.7 setup.py sdist upload

