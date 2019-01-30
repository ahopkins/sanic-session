release:
	rm -r dist
	. venv/bin/activate; python setup.py sdist bdist_wheel && twine upload dist/*
	rm -r dist