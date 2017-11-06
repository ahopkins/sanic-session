import uuid

from datetime import datetime, timedelta

from sanic_motor import BaseModel
from sanic_session.base import BaseSessionInterface, SessionDict



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



class MongoDBSessionInterface(BaseSessionInterface):
    def __init__(
            self, app, coll: str='session',
            domain: str=None,
            expiry: int=30*24*60*60,
            httponly: bool=True,
            cookie_name: str='session'):
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
        """
        self.expiry = expiry
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = True

        # set collection name
        _SessionModel.__coll__ = coll

        @app.listener('after_server_start')
        async def apply_session_indexes(app, loop):
            """Create indexes in session collection
            if doesn't exist.

            Indexes:
                sid:
                    For faster lookup.
                expiry:
                    For document expiration.
            """
            await _SessionModel.create_index('sid')
            await _SessionModel.create_index('expiry', expireAfterSeconds=0)


    async def open(self, request):
        """Opens a session onto the request. Restores the client's session
        from MongoDB if one exists.The session data will be available on
        `request.session`.


        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.

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
            document = await _SessionModel.find_one({'sid': sid}, as_raw=True)

            if document is not None:
                session_dict = SessionDict(document['data'], sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request['session'] = session_dict
        return session_dict


    async def save(self, request, response) -> None:
        """Saves the session into MongoDB and returns appropriate cookies.

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

        sid = request['session'].sid    

        if not request['session']:
            await _SessionModel.delete_one({'sid': sid})
            
            if request['session'].modified:
                self._delete_cookie(request, response)                      

            return

        data = dict(request['session'])
        expiry = datetime.utcnow() + timedelta(seconds=self.expiry)

        await _SessionModel.replace_one(
                            {'sid': sid},
                            {
                                'sid': sid,
                                'expiry': expiry,
                                'data': data
                            },
                            upsert=True)

        self._set_cookie_expiration(request, response)
