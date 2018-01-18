import time
import abc
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

    @abc.abstractclassmethod
    async def open(self, request):
        pass

    @abc.abstractclassmethod
    async def save(self, request, response) -> None:
        pass
