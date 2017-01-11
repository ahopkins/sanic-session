import json
from sanic_session.base import BaseSessionInterface, SessionDict
from sanic_session.utils import ExpiringDict
import uuid


class InMemorySessionInterface(BaseSessionInterface):
    def __init__(
            self, domain: str=None, expiry: int = 2592000,
            httponly: bool=True, cookie_name: str = 'session',
            prefix: str='session:'):
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.session_store = ExpiringDict()

    async def open(self, request) -> SessionDict:
        """Opens an in-memory session onto the request. Restores the client's session
        from memory if one exists.The session will be available on
        `request.session`.


        Args:
            request (sanic.request.Request):
                The request, which a session will be opened onto.

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
            val = self.session_store.get(self.prefix + sid)

            if val is not None:
                data = json.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session to the in-memory session store.

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

        if not request['session']:
            self.session_store.delete(
                self.prefix + request['session'].sid)

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = json.dumps(dict(request['session']))

        self.session_store.set(
            self.prefix + request['session'].sid, val,
            self.expiry)

        self._set_cookie_expiration(request, response)

    def get_session(self, sid):
        key = self.prefix + sid
        val = self.session_store.get(key)

        if val:
            return SessionDict(json.loads(val), sid=sid)
