PHONY=all

all:
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	python generate.py
	poetry build
