# Sanic session management for humans
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fxen%2Fsanic_session.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fxen%2Fsanic_session?ref=badge_shield)


`sanic_session` is session management extension for [Sanic](http://sanic.readthedocs.io/) that integrates server-backed sessions with most convenient API.

`sanic_session` provides a number of *session interfaces* for you to store a client's session data. The interfaces available right now are:

  * Redis (supports both drivers `aioredis` and `asyncio_redis`)
  * Memcache (via `aiomcache`)
  * Mongodb (via `sanic_motor` and `pymongo`)
  * In-Memory (suitable for testing and development environments)

## Installation

Install with `pip` (there is other options for different drivers, check documentation):

`pip install sanic_session`

or if you prefer `Pipenv`:

`pipenv install sanic_session`

## Documentation

Documentation is available at [sanic-session.readthedocs.io](http://sanic-session.readthedocs.io/en/latest/).

## Example

A simple example uses the in-memory session interface.

```python
from sanic import Sanic
from sanic.response import text
from sanic_session import Session, InMemorySessionInterface

app = Sanic()
session = Session(app, interface=InMemorySessionInterface())

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

Examples of using redis and memcache backed sessions can be found in the documentation, under [Using the Interfaces](http://sanic-session.readthedocs.io/en/latest/using_the_interfaces.html).


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fxen%2Fsanic_session.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fxen%2Fsanic_session?ref=badge_large)