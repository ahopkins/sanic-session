from .memory import InMemorySessionInterface

try:
    from sanic_ext import Extension

    SANIC_EXTENSIONS = True
except ImportError:
    Extension = type("Extension", (), {})  # type: ignore
    SANIC_EXTENSIONS = False


class Session(Extension):
    name = "session"

    def __init__(self, app=None, interface=None):
        self.interface = interface
        if app:
            self.init_app(app, interface)

    def init_app(self, app, interface):
        self.interface = interface or InMemorySessionInterface()
        if not hasattr(app.ctx, "extensions"):
            app.ctx.extensions = {}

        app.ctx.extensions[
            self.interface.session_name
        ] = self  # session_name defaults to 'session'

        async def add_session_to_request(request):
            """Before each request initialize a session
            using the client's request."""
            await self.interface.open(request)

        async def save_session(request, response):
            """After each request save the session, pass
            the response to set client cookies.
            """
            await self.interface.save(request, response)

        app.request_middleware.appendleft(add_session_to_request)
        app.response_middleware.append(save_session)

    def startup(self, _) -> None:
        if not SANIC_EXTENSIONS:
            raise RuntimeError("Sanic Extensions is not installed")
        self.init_app(self.app, self.interface)

    def label(self):
        return self.interface.__class__.__name__
