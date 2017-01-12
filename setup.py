from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ''

setup(
    name='sanic_session',
    version='0.1.0',
    description='Provides server-backed sessions for Sanic using Redis, Memcache and more.',
    long_description=long_description,
    url='http://github.com/subyraman/sanic_session',
    author='Suby Raman',
    license='MIT',
    packages=['sanic_session'],
    install_requires=('sanic'),
    zip_safe=False,
    keywords=['sessions', 'sanic', 'redis', 'memcache'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ]
)
