from .memcache import MemcacheSessionInterface
from .redis import RedisSessionInterface
from .memory import InMemorySessionInterface
from .mongodb import MongoDBSessionInterface
from .aioredis import AIORedisSessionInterface
from .base import BaseSessionInterface

__all__ = ('MemcacheSessionInterface', 'RedisSessionInterface',
           'InMemorySessionInterface', 'MongoDBSessionInterface',
           'AIORedisSessionInterface', 'Session')


class Session:

    def __init__(self, app=None, interface=None):
        self.app = app
        if app:
            self.init_app(app, interface=interface)

    def init_app(self, app, interface=None):
        if interface is None:
            interface = InMemorySessionInterface()

        self.interface = interface
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['session'] = self

        # @app.middleware('request')
        async def add_session_to_request(request):
            """Before each request initialize a session
            using the client's request."""
            await self.interface.open(request)

        # @app.middleware('response')
        async def save_session(request, response):
            """After each request save the session, pass
            the response to set client cookies.
            """
            await self.interface.save(request, response)

        app.request_middleware.appendleft(add_session_to_request)
        app.response_middleware.append(save_session)