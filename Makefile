test:
	nosetests -dsv tests/test_*.py

develop:
	pip install -r requirements/development.txt

clean:
	rm -rf reg_settings.py* *.pyc pypln/*.pyc tests/*.pyc

.PHONY:	test develop clean
