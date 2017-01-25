import json
from sanic_session.base import BaseSessionInterface, SessionDict
import uuid

from typing import Callable


class RedisSessionInterface(BaseSessionInterface):
    def __init__(self, redis_getter: Callable=None, **kwargs):
        """Initializes a session interface backed by Redis.

        Args:
            redis_getter (Callable):
                Coroutine which should return an asyncio_redis connection pool
                (suggested) or an asyncio_redis Redis connection.
        """
        kw = {k: kwargs.pop(k) for k in list(kwargs.keys())
              if k.startswith('redis_')}

        super().__init__(**kwargs)
        self.redis_getter = redis_getter or self.get_default_redis_getter(**kw)

    def get_default_redis_getter(self, **kwargs):
        import asyncio_redis
        hiredis_ok = True
        if kwargs.pop('redis_protocol', 'hiredis') == 'hiredis':
            try:
                from asyncio_redis import HiRedisProtocol as RedisProtocol
            except ImportError:
                hiredis_ok = False

        if not hiredis_ok:
            from asyncio_redis import RedisProtocol

        class Redis:
            _pool = None

            async def get_redis_pool(self):
                if not self._pool:
                    kw = dict(host=kwargs.get('redis_host', 'localhost'),
                              port=kwargs.get('redis_port', 6379),
                              poolsize=kwargs.get('redis_poolsize', 10),
                              protocol_class=RedisProtocol)
                    self._pool = await asyncio_redis.Pool.create(**kw)

                return self._pool

        return Redis().get_redis_pool

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
        redis_connection = await self.redis_getter()

        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            val = await redis_connection.get(self.prefix + sid)

            if val is not None:
                data = json.loads(val)
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
        redis_connection = await self.redis_getter()

        if 'session' not in request:
            return

        if not request['session']:
            await redis_connection.delete(
                [self.prefix + request['session'].sid])

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = json.dumps(dict(request['session']))

        await redis_connection.setex(
            self.prefix + request['session'].sid, self.expiry, val)

        self._set_cookie_expiration(request, response)

    async def close(self, *args, **kwargs):
        redis_connection = await self.redis_getter()
        redis_connection.close()
