import json
from sanic_session.base import BaseSessionInterface, SessionDict
import uuid


class MemcacheSessionInterface(BaseSessionInterface):
    def __init__(self, memcache_connection, **kwargs):
        """Initializes the interface for storing client sessions in memcache.
        Requires a client object establised with `asyncio_memcache`.

        Args:
            memcache_connection (aiomccache.Client):
                The memcache client used for interfacing with memcache.
        """
        super().__init__(**kwargs)
        self.memcache_connection = memcache_connection
        # memcache has a maximum 30-day cache limit
        if self.expiry > 2592000:
            self.expiry = 0

    async def open(self, request) -> dict:
        """Opens a session onto the request. Restores the client's session
        from memcache if one exists.The session data will be available on
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
            key = (self.prefix + sid).encode()
            val = await self.memcache_connection.get(key)

            if val is not None:
                data = json.loads(val.decode())
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        # attach the session data to the request, return it for convenience
        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session to memcache.

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

        key = (self.prefix + request['session'].sid).encode()

        if not request['session']:
            await self.memcache_connection.delete(key)

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = json.dumps(dict(request['session'])).encode()

        await self.memcache_connection.set(
            key, val,
            exptime=self.expiry)

        self._set_cookie_expiration(request, response)

    async def close(self, *args, **kwargs):
        memcache_connection = await self.memcache_connection
        await memcache_connection.close()
