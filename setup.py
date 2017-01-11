from setuptools import setup

setup(
    name='sanic_session',
    version='0.1',
    description='Provides server-backed sessions for Sanic using Redis, Memcache and more.',
    url='http://github.com/subyraman/sanic_session',
    author='Suby Raman',
    license='MIT',
    packages=['sanic_session'],
    install_requires=('sanic'),
    zip_safe=False
)
