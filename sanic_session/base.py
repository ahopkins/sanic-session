#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic_session.utils import CallbackDict


class SessionDict(CallbackDict):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)

        self.sid = sid
        self.modified = False


class BaseSessionInterface:
    def __init__(self, app=None, domain=None, expiry=2592000,
                 httponly=True, cookie_name='session',
                 prefix='session:', **kwargs):
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.middleware('request')
        async def add_session_to_request(request):
            # before each request initialize a session
            # using the client's request
            await self.open(request)

        @app.middleware('response')
        async def save_session(request, response):
            # after each request save the session,
            # pass the response to set client cookies
            await self.save(request, response)

    def _delete_cookie(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['expires'] = 0
        response.cookies[self.cookie_name]['max-age'] = 0

    def _set_cookie_expiration(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['expires'] = self.expiry
        response.cookies[self.cookie_name]['httponly'] = self.httponly

        if self.domain:
            response.cookies[self.cookie_name]['domain'] = self.domain

    async def close(self, *args, **kwargs):
        pass
