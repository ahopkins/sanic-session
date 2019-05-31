venv/bin/activate:
	python3 -m venv venv

setup: venv/bin/activate dev_requirements.txt
	. venv/bin/activate; pip install -U pip
	. venv/bin/activate; pip install -Ur dev_requirements.txt


release:
	rm -r dist
	. venv/bin/activate; python setup.py sdist bdist_wheel && twine upload dist/*
	rm -r dist