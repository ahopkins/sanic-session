venv/bin/activate:
	python3 -m venv venv

setup: ## project setup and run migrations
	pip install -e .[aioredis,redis,mongo,aiomcache,dev]

release: ## create new release
	rm -rf dist
	python setup.py sdist bdist_wheel && twine upload dist/*
	rm -rf dist

lint: ## run linter
	flake8 sanic_session/ tests
	isort sanic_session tests --check
	black sanic_session tests --check

format: ## format code
	isort sanic_session tests
	black sanic_session tests

pretty: format

test: ## run tests
	py.test -vs --cov sanic_session/ tests

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

