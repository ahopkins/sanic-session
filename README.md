### sanic_session

sanic_session is an extension for sanic that integrates server-backed sessions with a Flask-like API. 

sanic_session provides a number of *session interfaces* for you to store a client's session data. The interfaces available right now are:

* Redis
* Memcache
* In-Memory (suitable for testing and development environments)

## Installation

Install with `pip`:

`pip install sanic_session`

## Documentation

Documentation is available at [PythonHosted](https://pythonhosted.org/sanic_session/).

## Example

A simple example uses the in-memory session interface.


```python
    from sanic import Sanic
    from sanic.response import text
    import sanic_session


    app = Sanic()
    sanic_session.install_middleware(app, 'InMemorySessionInterface')


    @app.route("/")
    async def index(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        return text(request['session']['foo'])

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)
```

Examples of using redis and memcache backed sessions can be found in the documentation, under [Using the Interfaces](https://pythonhosted.org/sanic_session/using_the_interfaces.html).
