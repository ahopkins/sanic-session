from .memcache import MemcacheSessionInterface
from .redis import RedisSessionInterface
from .memory import InMemorySessionInterface
from .mongodb import MongoDBSessionInterface
from .aioredis import AIORedisSessionInterface

__all__ = (
    "MemcacheSessionInterface",
    "RedisSessionInterface",
    "InMemorySessionInterface",
    "MongoDBSessionInterface",
    "AIORedisSessionInterface",
    "Session",
)


class Session:
    def __init__(self, app=None, interface=None):
        self.interface = None
        if app:
            self.init_app(app, interface)

    def init_app(self, app, interface):
        self.interface = interface or InMemorySessionInterface()
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions[self.interface.session_name] = self  # session_name defaults to 'session'

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
