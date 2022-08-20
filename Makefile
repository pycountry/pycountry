PHONY=sdist

sdist:
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	python generate.py
	python -m pip install build
	python -m build -s
