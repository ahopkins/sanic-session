from typing import Optional, Union
from .aioredis import AIORedisSessionInterface
from .memcache import MemcacheSessionInterface
from .memory import InMemorySessionInterface
from .mongodb import MongoDBSessionInterface
from .redis import RedisSessionInterface
from sanic import Sanic
from .base import BaseSessionInterface
from .policy import RenewalPolicy

__all__ = (
    "MemcacheSessionInterface",
    "RedisSessionInterface",
    "InMemorySessionInterface",
    "MongoDBSessionInterface",
    "AIORedisSessionInterface",
    "Session",
)


class Session:
    def __init__(
        self,
        app: Optional[Sanic] = None,
        interface: Optional[BaseSessionInterface] = None,
        renew_cookie: Union[str, RenewalPolicy] = RenewalPolicy.NEVER,
    ):
        self.interface = interface
        self.renew_cookie = (
            renew_cookie
            if isinstance(renew_cookie, RenewalPolicy)
            else RenewalPolicy[renew_cookie.upper()]
        )
        if app:
            self.init_app(app, interface)

    def init_app(
        self, app: Sanic, interface: Optional[BaseSessionInterface] = None
    ):
        self.interface = interface or InMemorySessionInterface()
        self.interface.renew_cookie = self.renew_cookie

        if not hasattr(app.ctx, "extensions"):
            app.ctx.extensions = {}

        app.ctx.extensions[
            self.interface.session_name
        ] = self  # session_name defaults to 'session'

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
