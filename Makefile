SHELL := /bin/bash

test:
	nosetests-2.7 -s --verbosity=2

clean:
	rm -fr build dist
	rm -fr *.egg-info
	find . -name *.pyc -exec rm {} \;
	find . -name *.swp -exec rm {} \;

install:
	python2.7 setup.py install

upload: clean
	python2.7 setup.py sdist upload

