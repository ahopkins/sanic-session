.. _using_the_interfaces:

Using the interfaces
=====================

Redis
-----------------
`Redis <https://redis.io/>`_ is a popular and widely supported key-value store. In order to interface with redis, you will need to add :code:`asyncio_redis` to your project. Do so with pip:

:code:`pip install asyncio_redis`

To integrate Redis with :code:`sanic_session` you need to pass a getter method into the :code:`RedisSessionInterface` which returns a connection pool. This is required since there is no way to synchronously create a connection pool. An example is below:

.. code-block:: python

    import asyncio_redis

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import RedisSessionInterface


    app = Sanic()


    class Redis:
        """
        A simple wrapper class that allows you to share a connection
        pool across your application.
        """
        _pool = None

        async def get_redis_pool(self):
            if not self._pool:
                self._pool = await asyncio_redis.Pool.create(
                    host='localhost', port=6379, poolsize=10
                )

            return self._pool


    redis = Redis()

    # pass the getter method for the connection pool into the session
    session_interface = RedisSessionInterface(redis.get_redis_pool)


    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)


    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)


    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        response = text(request['session']['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)

Memcache
-----------------
`Memcache <https://memcached.org/>`_ is another popular key-value storage system. In order to interface with memcache, you will need to add :code:`aiomcache` to your project. Do so with pip:

:code:`pip install aiomcache`

To integrate memcache with :code:`sanic_session` you need to pass an :code:`aiomcache.Client` into the session interface, as follows:


.. code-block:: python

    import aiomcache
    import uvloop

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import MemcacheSessionInterface

    app = Sanic()

    # create a uvloop to pass into the memcache client and sanic
    loop = uvloop.new_event_loop()

    # create a memcache client
    client = aiomcache.Client("127.0.0.1", 11211, loop=loop)

    # pass the memcache client into the session
    session_interface = MemcacheSessionInterface(client)


    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)


    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)


    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        response = text(request['session']['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True, loop=loop)

In-Memory
-----------------

:code:`sanic_session` comes with an in-memory interface which stores sessions in a Python dictionary available at :code:`session_interface.session_store`. This interface is meant for testing and development purposes only. **This interface is not suitable for production**.

.. code-block:: python

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import InMemorySessionInterface


    app = Sanic()
    session_interface = InMemorySessionInterface()

    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)


    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)

    @app.route("/")
    async def index(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        return text(request['session']['foo'])

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)