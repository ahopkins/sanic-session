# Sanic session management for humans
[![ReadTheDocs](https://img.shields.io/readthedocs/sanic_session.svg)](https://sanic-session.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/sanic_session.svg)](https://pypi.org/project/sanic_session/)


`sanic-session` is session management extension for [Sanic](https://sanic.dev) that integrates server-backed sessions with most convenient API.

`sanic-session` provides a number of *session interfaces* for you to store a client's session data. The interfaces available right now are:

  * Redis (supports both drivers `aioredis` and `asyncio_redis`)
  * Memcache (via `aiomcache`)
  * Mongodb (via `sanic_motor` and `pymongo`)
  * In-Memory (suitable for testing and development environments)

## Installation

Install with `pip` (there is other options for different drivers, check documentation):

`pip install sanic_session`


## Documentation

Documentation is available at [sanic-session.readthedocs.io](http://sanic-session.readthedocs.io/en/latest/).

Also, make sure you read [OWASP's Session Management Cheat Sheet](https://www.owasp.org/index.php/Session_Management_Cheat_Sheet) for some really useful info on session management.

## Example

A simple example uses the in-memory session interface.

```python
from sanic import Sanic
from sanic.response import text
from sanic_session import Session, InMemorySessionInterface

app = Sanic(name="ExampleApp")
session = Session(app, interface=InMemorySessionInterface())

@app.route("/")
async def index(request):
    # interact with the session like a normal dict
    if not request.ctx.session.get('foo'):
        request.ctx.session['foo'] = 0

    request.ctx.session['foo'] += 1

    return text(str(request.ctx.session["foo"]))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Examples of using redis and memcache backed sessions can be found in the documentation, under [Using the Interfaces](http://sanic-session.readthedocs.io/en/latest/using_the_interfaces.html).

<p align="center">&mdash; ⭐️ &mdash;</p>
