from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

# Set requirements here
requirements = (
    "sanic",
    "ujson",
)

extras_require = {
    "aioredis": ["aioredis>=1.0.0"],
    "redis": ["asyncio_redis"],
    "mongo": ["sanic_motor", "pymongo"],
    "aiomcache": ["aiomcache>=0.5.2"],
    "dev": [
        "pytest",
        "aiohttp",
        "pytest-asyncio",
        "pytest-mock",
        "pytest-cov",
        "wheel",
        "black;python_version>='3.6'",
        "isort",
        "mypy",
        "sphinx",
        "sphinxcontrib-fulltoc",
        "flake8",
    ],
}


setup(
    name="sanic-session",
    version="0.8.0",
    description=(
        "Provides server-backed sessions for Sanic "
        "using Redis, Memcache and more."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/subyraman/sanic_session",
    author="Suby Raman, Mikhail Kashkin, Adam Hopkins",
    author_email="adam@amhopkins.com",
    license="MIT",
    packages=["sanic_session"],
    # Kludge: Specifying requirements for setup and install works around
    # problem with easyinstall finding sanic_motor instead of sanic.
    # See similar problem:
    #   https://stackoverflow.com/questions/27497470/setuptools-finds-wrong-package-during-install
    #   https://github.com/numpy/numpy/issues/2434
    setup_requires=requirements,
    install_requires=requirements,
    extras_require=extras_require,
    zip_safe=False,
    keywords=["sessions", "sanic", "redis", "memcache"],
    classifiers=[
        "Framework :: AsyncIO",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Session",
    ],
)
