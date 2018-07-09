import time
import abc
import ujson
import uuid
from sanic_session.utils import CallbackDict


class SessionDict(CallbackDict):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)

        self.sid = sid
        self.modified = False


def _calculate_expires(expiry):
    expires = time.time() + expiry
    return time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires))


class BaseSessionInterface(metaclass=abc.ABCMeta):
    # this flag show does this Interface need request/responce middleware hooks

    def _delete_cookie(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid

        # We set expires/max-age even for session cookies to force expiration
        response.cookies[self.cookie_name]['expires'] = 0
        response.cookies[self.cookie_name]['max-age'] = 0

    def _set_cookie_expiration(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['httponly'] = self.httponly

        # Set expires and max-age unless we are using session cookies
        if not self.sessioncookie:
            response.cookies[self.cookie_name]['expires'] = _calculate_expires(self.expiry)
            response.cookies[self.cookie_name]['max-age'] = self.expiry

        if self.domain:
            response.cookies[self.cookie_name]['domain'] = self.domain

    @abc.abstractmethod
    async def _get_value(self, prefix: str, sid: str):
        '''
        Get value from datastore. Specific implementation for each datastore.

        Args:
            prefix:
                A prefix for the key, useful to namespace keys.
            sid:
                a uuid in hex string
        '''
        raise NotImplementedError

    @abc.abstractmethod
    async def _delete_key(self, prefix: str, key: str):
        '''Delete key from datastore'''
        raise NotImplementedError

    @abc.abstractmethod
    async def _set_value(self, key: str, data: SessionDict):
        '''Set value for datastore'''
        raise NotImplementedError

    async def open(self, request) -> SessionDict:
        """
        Opens a session onto the request. Restores the client's session
        from the datastore if one exists.The session data will be available on
        `request.session`.


        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.

        Returns:
            SessionDict:
                the client's session data,
                attached as well to `request.session`.
        """
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            val = await self._get_value(self.prefix, sid)

            if val is not None:
                data = ujson.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        # attach the session data to the request, return it for convenience
        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session to the datastore.

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

        key = (self.prefix + request['session'].sid)
        if not request['session']:
            await self._delete_key(key)

            if request['session'].modified:
                self._delete_cookie(request, response)
            return

        val = ujson.dumps(dict(request['session']))
        await self._set_value(key, val)
        self._set_cookie_expiration(request, response)
