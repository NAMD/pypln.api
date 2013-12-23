test:
	clear
	nosetests -dsv --with-yanc --with-coverage --cover-package pypln.api tests/test_*.py

develop:
	pip install -r requirements/development.txt

clean:
	rm -rf reg_settings.py* *.pyc pypln/*.pyc tests/*.pyc build/ dist/ pypln.api.egg-info/

.PHONY:	test develop clean
