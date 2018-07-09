from sanic_session.base import BaseSessionInterface

try:
    import aiomcache
except ImportError:  # pragma: no cover
    aiomcache = None


class MemcacheSessionInterface(BaseSessionInterface):
    def __init__(
            self, memcache_connection,
            domain: str=None, expiry: int = 2592000,
            httponly: bool=True, cookie_name: str = 'session',
            prefix: str = 'session:',
            sessioncookie: bool=False):
        """Initializes the interface for storing client sessions in memcache.
        Requires a client object establised with `asyncio_memcache`.

        Args:
            memcache_connection (aiomccache.Client):
                The memcache client used for interfacing with memcache.
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
        if aiomcache is None:
            raise RuntimeError("Please install aiomcache: pip install sanic_session[aiomcache]")

        self.memcache_connection = memcache_connection

        # memcache has a maximum 30-day cache limit
        if expiry > 2592000:
            self.expiry = 0
        else:
            self.expiry = expiry

        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.sessioncookie = sessioncookie

    async def _get_value(self, prefix, sid):
        key = (self.prefix + sid).encode()
        value = await self.memcache_connection.get(key)
        return value.decode() if value else None

    async def _delete_key(self, key):
        return await self.memcache_connection.delete(key.encode())

    async def _set_value(self, key, data):
        return await self.memcache_connection.set(
            key.encode(), data.encode(),
            exptime=self.expiry
        )
