import time

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


class BaseSessionInterface:
    def _delete_cookie(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['expires'] = 0
        response.cookies[self.cookie_name]['max-age'] = 0

    def _set_cookie_expiration(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['expires'] = _calculate_expires(self.expiry)
        response.cookies[self.cookie_name]['max-age'] = self.expiry
        response.cookies[self.cookie_name]['httponly'] = self.httponly

        if self.domain:
            response.cookies[self.cookie_name]['domain'] = self.domain
