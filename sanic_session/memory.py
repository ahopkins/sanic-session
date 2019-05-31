from sanic_session.base import BaseSessionInterface
from sanic_session.utils import ExpiringDict


class InMemorySessionInterface(BaseSessionInterface):
    def __init__(
        self,
        domain: str = None,
        expiry: int = 2592000,
        httponly: bool = True,
        cookie_name: str = "session",
        prefix: str = "session:",
        sessioncookie: bool = False,
        samesite: str = None,
        session_name="session",
        secure: bool = False,
    ):

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
        self.session_store = ExpiringDict()

    async def _get_value(self, prefix, sid):
        return self.session_store.get(self.prefix + sid)

    async def _delete_key(self, key):
        if key in self.session_store:
            self.session_store.delete(key)

    async def _set_value(self, key, data):
        self.session_store.set(key, data, self.expiry)
