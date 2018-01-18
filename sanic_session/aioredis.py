import ujson
from sanic_session.base import BaseSessionInterface, SessionDict
import uuid

from typing import Callable

try:
    import aioredis
except ImportError:
    aioredis = None


class AIORedisSessionInterface(BaseSessionInterface):
    def __init__(
            self, redis_getter: Callable,
            domain: str=None, expiry: int = 2592000,
            httponly: bool=True, cookie_name: str='session',
            prefix: str='session:',
            sessioncookie: bool=False):
        """Initializes a session interface backed by Redis.

        Args:
            redis (Callable):
                aioredis connection or connection pool instance.
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
        """
        if aioredis is None:
            raise RuntimeError("Please install aioredis: pip install sanic_session[aioredis]")

        if isinstance(redis_getter, aioredis.commands.Redis):
            raise RuntimeError("Wrong redis connection provided, please use: await aioredis.create_redis_pool(...) or await aioredis.create_redis(...)")

        self.redis = redis_getter
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.sessioncookie = sessioncookie

    async def open(self, request):
        """Opens a session onto the request. Restores the client's session
        from Redis if one exists.The session data will be available on
        `request.session`.


        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.

        Returns:
            dict:
                the client's session data,
                attached as well to `request.session`.
        """
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            val = await self.redis.get(self.prefix + sid)

            if val is not None:
                data = ujson.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session into Redis and returns appropriate cookies.

        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.

        Returns:
            None
        """
        if 'session' not in request:
            return

        key = self.prefix + request['session'].sid
        if not request['session']:
            await self.redis.delete([key])

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = ujson.dumps(dict(request['session']))

        await self.redis.setex(key, self.expiry, val)

        self._set_cookie_expiration(request, response)
