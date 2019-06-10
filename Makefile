venv/bin/activate:
	python3 -m venv venv

setup:
	pip install -e .[aioredis,redis,mongo,aiomcache,dev]


release:
	rm -rf dist
	python setup.py sdist bdist_wheel && twine upload dist/*
	rm -rf dist

lint:
	flake8 sanic_session/ tests
	black -l 120 --check sanic_session/ tests

format:
	black -l 120 sanic_session/ tests

test:
	py.test -vs --cov sanic_session/ tests
