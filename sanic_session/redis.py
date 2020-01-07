from typing import Callable
from sanic_session.base import BaseSessionInterface

try:
    import asyncio_redis
except ImportError:
    asyncio_redis = None


class RedisSessionInterface(BaseSessionInterface):
    def __init__(
        self,
        redis_getter: Callable,
        domain: str = None,
        expiry: int = 2592000,
        httponly: bool = True,
        cookie_name: str = "session",
        prefix: str = "session:",
        sessioncookie: bool = False,
        samesite: str = None,
        session_name: str = "session",
        secure: bool = False,
    ):
        """Initializes a session interface backed by Redis.

        Args:
            redis_getter (Callable):
                Coroutine which should return an asyncio_redis connection pool
                (suggested) or an asyncio_redis Redis connection.
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            prefix (str, optional):
                Memcache keys will take the format of `prefix+session_id`;
                specify the prefix here.
            sessioncookie (bool, optional):
                Specifies if the sent cookie should be a 'session cookie', i.e
                no Expires or Max-age headers are included. Expiry is still
                fully tracked on the server side. Default setting is False.
            samesite (str, optional):
                Will prevent the cookie from being sent by the browser to the
                target site in all cross-site browsing context, even when
                following a regular link.
                One of ('lax', 'strict')
                Default: None
            session_name (str, optional):
                Name of the session that will be accessible through the
                request.
                e.g. If ``session_name`` is ``alt_session``, it should be
                accessed like that: ``request['alt_session']``
                e.g. And if ``session_name`` is left to default, it should be
                accessed like that: ``request['session']``
                Default: 'session'
            secure (bool, optional):
                Adds the `Secure` flag to the session cookie.
        """
        if asyncio_redis is None:
            raise RuntimeError("Please install asyncio_redis: pip install sanic_session[redis]")

        self.redis_getter = redis_getter

        super().__init__(
            expiry=expiry,
            prefix=prefix,
            cookie_name=cookie_name,
            domain=domain,
            httponly=httponly,
            sessioncookie=sessioncookie,
            samesite=samesite,
            session_name=session_name,
            secure=secure,
        )

    async def _get_value(self, prefix, key):
        redis_connection = await self.redis_getter()
        return await redis_connection.get(prefix + key)

    async def _delete_key(self, key):
        redis_connection = await self.redis_getter()
        await redis_connection.delete([key])

    async def _set_value(self, key, data):
        redis_connection = await self.redis_getter()
        await redis_connection.setex(key, self.expiry, data)
