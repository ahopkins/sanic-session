import time
from typing import Optional
from sanic_session.base import BaseSessionInterface

from sanic import Sanic, Request
from multiprocessing import Manager


class MultiMemorySessionInterface(BaseSessionInterface):
    def __init__(
        self,
        domain: Optional[str] = None,
        expiry: int = 2592000,
        httponly: bool = True,
        cookie_name: str = "session",
        prefix: str = "session:",
        sessioncookie: bool = False,
        samesite: Optional[str] = None,
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

    async def _get_value(self, prefix, sid):
        key = self.prefix + sid
        current = Request.get_current()
        data = current.app.shared_ctx.session_info.get(key)

        if not data:
            return None

        if time.time() > current.app.shared_ctx.expiry_info[key]:
            with current.app.shared_ctx.session_lock:
                await self._delete_key(key)
            return None

        return data

    async def _delete_key(self, key):
        current = Request.get_current()
        current.app.shared_ctx.session_info.pop(key, None)
        current.app.shared_ctx.expiry_info.pop(key, None)

    async def _set_value(self, key, data):
        current = Request.get_current()
        with current.app.shared_ctx.session_lock:
            current.app.shared_ctx.session_info[key] = data
            current.app.shared_ctx.expiry_info[key] = time.time() + self.expiry

    def _attach_app(self, app: Sanic):
        app.main_process_start(self.main_process_start)
        app.main_process_ready(self.main_process_ready)
        app.main_process_stop(self.main_process_stop)

    async def main_process_start(self, _):
        self.manager = Manager()
        self.session_info = self.manager.dict()
        self.expiry_info = self.manager.dict()
        self.lock = self.manager.Lock()

    async def main_process_ready(self, app: Sanic):
        app.shared_ctx.session_info = self.session_info
        app.shared_ctx.expiry_info = self.expiry_info
        app.shared_ctx.session_lock = self.lock

    async def main_process_stop(self, _):
        self.manager.shutdown()
