.. _testing:

Testing
=====================

When building your application you'll eventually want to test that your sessions are behaving as expected. You can use the :code:`InMemorySessionInterface` for testing purposes. You'll want to insert some logic in your application so that in a testing environment, your application uses the :code:`InMemorySessionInterface`. An example is like follows:

**main.py**

.. code-block:: python

    import asyncio_redis
    import os

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import (
        RedisSessionInterface,
        InMemorySessionInterface
    )


    app = Sanic()


    class Redis:
        _pool = None

        async def get_redis_pool(self):
            if not self._pool:
                self._pool = await asyncio_redis.Pool.create(
                    host='localhost', port=6379, poolsize=10
                )

            return self._pool


    redis = Redis()

    # If we are in the testing environment, use the in-memory session interface
    if os.environ.get('TESTING'):
        Session(app, interface = InMemorySessionInterface())
    else:
        Session(app, interface = RedisSessionInterface(redis.get_redis_pool))


    @app.route("/")
    async def index(request):
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        response = text(request['session']['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)

Let's say we want to test that the route :code:`/` does in fact increment a counter on subsequent requests. There's a few things to remember:

- When a session is saved, a :code:`session` parameter is included in the response cookie.
- Use this session ID to retrieve the server-stored session data from the :code:`session_interface`.
- You can also use this session ID on future requests to reuse the same client session.

An example is like follows:

.. code-block:: python

    import os
    os.environ['TESTING'] = 'True'

    from main import app, session_interface

    import pytest
    import aiohttp
    from sanic.utils import sanic_endpoint_test


    def test_session_increments_counter():
        request, response = sanic_endpoint_test(app, uri='/')

        # A session ID is passed in the response cookies, save that
        session_id = response.cookies['session'].value

        # retrieve the session data using the session_id
        session = session_interface.get_session(session_id)

        assert session['foo'] == 1, 'foo should initially equal 1'

        # use the session ID to test the endpoint against the same session
        request, response = sanic_endpoint_test(
            app, uri='/', cookies={'session': session_id})

        # again retrieve the session data using the session_id
        session = session_interface.get_session(session_id)

        assert session['foo'] == 2, 'foo should increment on subsequent requests'
