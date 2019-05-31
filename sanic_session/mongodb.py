from datetime import datetime, timedelta
from sanic_session.base import BaseSessionInterface
import warnings

try:
    from sanic_motor import BaseModel

    class _SessionModel(BaseModel):
        """Collection for session storing.

        Collection name (default session)

        Fields:
            sid
            expiry
            data:
                User's session data
        """

        pass


except ImportError:  # pragma: no cover
    _SessionModel = None


class MongoDBSessionInterface(BaseSessionInterface):
    def __init__(
        self,
        app,
        coll: str = "session",
        domain: str = None,
        expiry: int = 30 * 24 * 60 * 60,
        httponly: bool = True,
        cookie_name: str = "session",
        sessioncookie: bool = False,
        samesite: str = None,
        session_name: str = "session",
        secure: bool = False,
    ):
        """Initializes the interface for storing client sessions in MongoDB.

        Args:
            app (sanic.Sanic):
                Sanic instance to register listener('after_server_start')
            coll (str, optional):
                MongoDB collection name for session
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            sessioncookie (bool, optional):
                Specifies if the sent cookie should be a 'session cookie', i.e
                no Expires or Max-age headers are included. Expiry is still
                fully tracked on the server side. Default setting is False.
            samesite (str, optional):
                Will prevent the cookie from being sent by the browser to
                the target site in all cross-site browsing context, even when
                following a regular link.
                One of ('lax', 'strict')
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
        if _SessionModel is None:
            raise RuntimeError("Please install Mongo dependencies: " "pip install sanic_session[mongo]")

        # prefix not needed for mongodb as mongodb uses uuid4 natively
        prefix = ""

        if httponly is not True:
            warnings.warn(
                """
                httponly default arg has changed.
                To spare you some debugging time, httponly is currently
                hardcoded as True. This message will be removed with the
                next release. And ``httponly`` will no longer be hardcoded
            """,
                DeprecationWarning,
            )

        super().__init__(
            expiry=expiry,
            prefix=prefix,
            cookie_name=cookie_name,
            domain=domain,
            # I'm gonna leave this as True because changing it might
            # be hazardous. But this should be changed to __init__'s
            # httponly kwarg instead of being hardcoded
            httponly=True,
            sessioncookie=sessioncookie,
            samesite=samesite,
            session_name=session_name,
            secure=secure,
        )

        # set collection name
        _SessionModel.__coll__ = coll

        @app.listener("after_server_start")
        async def apply_session_indexes(app, loop):
            """Create indexes in session collection
            if doesn't exist.

            Indexes:
                sid:
                    For faster lookup.
                expiry:
                    For document expiration.
            """
            await _SessionModel.create_index("sid")
            await _SessionModel.create_index("expiry", expireAfterSeconds=0)

    async def _get_value(self, prefix, key):
        value = await _SessionModel.find_one({"sid": key}, as_raw=True)
        return value["data"] if value else None

    async def _delete_key(self, key):
        await _SessionModel.delete_one({"sid": key})

    async def _set_value(self, key, data):
        expiry = datetime.utcnow() + timedelta(seconds=self.expiry)
        await _SessionModel.replace_one({"sid": key}, {"sid": key, "expiry": expiry, "data": data}, upsert=True)
