import warnings

from sanic_session.base import BaseSessionInterface

try:
    import aiomcache
except ImportError:  # pragma: no cover
    aiomcache = None


class MemcacheSessionInterface(BaseSessionInterface):
    def __init__(
        self,
        memcache_connection,
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
            samesite (str, optional):
                Will prevent the cookie from being sent by the browser to
                the target site in all cross-site browsing context, even when
                following a regular link. One of ('lax', 'strict')
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
        if aiomcache is None:
            raise RuntimeError("Please install aiomcache: pip install " "sanic_session[aiomcache]")

        self.memcache_connection = memcache_connection

        if expiry > 2592000:
            warnings.warn("Memcache has a maximum 30-day cache limit")
            expiry = 0

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

    async def _get_value(self, prefix, sid):
        key = (self.prefix + sid).encode()
        value = await self.memcache_connection.get(key)
        return value.decode() if value else None

    async def _delete_key(self, key):
        return await self.memcache_connection.delete(key.encode())

    async def _set_value(self, key, data):
        return await self.memcache_connection.set(key.encode(), data.encode(), exptime=self.expiry)
