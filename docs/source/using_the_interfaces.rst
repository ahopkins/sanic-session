.. _using_the_interfaces:

Using the interfaces
=====================

For now project has set of different interfaces. You can install each manually or using the extra parameters:

:code:`pip install sanic_session[aioredis]`

Other supported backend keywords:

- :code:`aioredis` (dependency 'aioredis'),
- :code:`redis` ('asyncio_redis'),
- :code:`mongo` ('sanic_motor' and 'pymongo'),
- :code:`aiomcache` ('aiomcache')


Redis (asyncio_redis)
-----------------
`Redis <https://redis.io/>`_ is a popular and widely supported key-value store. In order to interface with redis, you will need to add :code:`asyncio_redis` to your project. Do so with pip:

:code:`pip install asyncio_redis` or :code:`pip install sanic_session[redis]`

To integrate Redis with :code:`sanic_session` you need to pass a getter method into the :code:`RedisSessionInterface` which returns a connection pool. This is required since there is no way to synchronously create a connection pool. An example is below:

.. code-block:: python

    import asyncio_redis

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import Session, RedisSessionInterface

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

    Session(app, interface=RedisSessionInterface(redis.get_redis_pool))


    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request.ctx.session.get('foo'):
            request.ctx.session['foo'] = 0

        request.ctx.session['foo'] += 1

        response = text(request.ctx.session['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)


Redis (aioredis)
-----------------
`aioredis` have little better syntax and more popular since it supported by `aiohttp` team.

:code:`pip install asyncio_redis` or :code:`pip install sanic_session[aioredis]`

This example shows little different approach. You can use classic Flask extensions approach with factory based initialization process. You can use it with different backends also.

.. code-block:: python

    import aioredis

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import Session, AIORedisSessionInterface

    app = Sanic(__name__, load_env=False)
    # init extensions
    session = Session()

    @app.listener('before_server_start')
    async def server_init(app, loop):
        app.redis = await aioredis.create_redis_pool(app.config['redis'])
        # init extensions fabrics
        session.init_app(app, interface=AIORedisSessionInterface(app.redis))


    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request.ctx.session.get('foo'):
            request.ctx.session['foo'] = 0

        request.ctx.session['foo'] += 1

        response = text(request.ctx.session['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)


Memcache
-----------------
`Memcache <https://memcached.org/>`_ is another popular key-value storage system. In order to interface with memcache, you will need to add :code:`aiomcache` to your project. Do so with pip:

:code:`pip install aiomcache` or :code:`pip install sanic_session[aiomcache]`

To integrate memcache with :code:`sanic_session` you need to pass an :code:`aiomcache.Client` into the session interface, as follows:


.. code-block:: python

    import aiomcache
    import uvloop

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import Session, MemcacheSessionInterface

    app = Sanic()

    # create a uvloop to pass into the memcache client and sanic
    loop = uvloop.new_event_loop()

    # create a memcache client
    client = aiomcache.Client("127.0.0.1", 11211, loop=loop)

    # pass the memcache client into the session
    session = Session(app, interface=MemcacheSessionInterface(client))

    @app.route("/")
    async def test(request):
        # interact with the session like a normal dict
        if not request.ctx.session.get('foo'):
            request.ctx.session['foo'] = 0

        request.ctx.session['foo'] += 1

        response = text(request.ctx.session['foo'])

        return response

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True, loop=loop)

In-Memory
-----------------

:code:`sanic_session` comes with an in-memory interface which stores sessions in a Python dictionary available at :code:`session_interface.session_store`. This interface is meant for testing and development purposes only. **This interface is not suitable for production**.

.. code-block:: python

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import Session


    app = Sanic()

    Session(app)  # because InMemorySessionInterface used by default

    # of full syntax:
    #   from sanic_session import InMemorySessionInterface
    #   session = Session(app, interface=InMemorySessionInterface())

    @app.route("/")
    async def index(request):
        # interact with the session like a normal dict
        if not request.ctx.session.get('foo'):
            request.ctx.session['foo'] = 0

        request.ctx.session['foo'] += 1

        return text(request.ctx.session['foo'])

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)
