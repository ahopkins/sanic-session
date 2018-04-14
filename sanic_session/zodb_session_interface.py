"""
ZODB allows different storages for different tasks:
    - FileStorage for storing data on disk,
    - In-memory storage for storing data into RAM,
    - ClientStorage for accesing ZODB server by URL,
        can be used as database in production,
        also as in-memory store in production.
TODO:
    implement it.
    - add async function-worker, who'll clean all expired sessions
        one per several minutes.
        It must only work when Sanic doesn't handle any request.
      Or store по очереди в список времи истечения, каждый запрос проверяем первый,
        скорость возростет
"""

import ujson
from sanic_session.base import BaseSessionInterface, SessionDict, _calculate_expires
from sanic_session.utils import ExpiringDict
import uuid


class ZODBSessionInterface(BaseSessionInterface):
    def __init__(self,
                 zodb_connection,
                 domain: str=None,
                 expiry: int = 2592000,
                 httponly: bool=True,
                 cookie_name: str = 'session',
                 prefix: str='session:',
                 sessioncookie: bool=False
                ):

        self.expiry = expiry
        self.prefix = 'sanic_session'
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.sessioncookie = sessioncookie
        self.zodb_connection = zodb_connection
        self.zodb_root = zodb_connection.root()

        import BTrees.OOBTree
        import transaction
        from persistent import Persistent

        self.zodb_root[self.prefix] = BTrees.OOBTree.BTree()
        self.zodb_transaction = transaction

        class PersistentSessionDict(Persistent):
            """Session dict, which is also subclass of ZODB Persistant class,
            which allows saving all data using "transaction.commit()".
            Note, that when changing changeable (lists, dicts) attributes
            of Persistent class,
            than you have to manually set "_p_changed" attribute to true
            for object to be saved on "transaction.commit()".
            """
            def __init__(self, sid=None):
                self.session_dict = {}
                self.sid = sid
                self.expiration = expiry

            def __setattr__(self, *args, **kwargs):
                super().__setattr__(*args, **kwargs)

            def __delattr__(self, *args, **kwargs):
                super().__delattr__(*args, **kwargs)
                self._p_changed = True

            def __setitem__(self, *args, **kwargs):
                super().__setitem__(*args, **kwargs)
                self._p_changed = True

            def __delitem__(self, *args, **kwargs):
                super().__delitem__(*args, **kwargs)
                self._p_changed = True

            def __getitem__(self, *args, **kwargs):
                return self.session_dict.__getitem__(*args, **kwargs)

            def keys(self, *args, **kwargs):
                return self.session_dict.keys(*args, **kwargs)

            sid = None
            expiration = None
            session_dict = None

        self.PersistentSessionDict = PersistentSessionDict

    async def open(self, request):
        """Opens an ZODB session onto the request. Restores the client's session
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
            persistent_session_dict = self.PersistentSessionDict(sid=sid)
            self.zodb_root[self.prefix][sid] = persistent_session_dict
        else:
            try:
                persistent_session_dict = self.zodb_root[self.prefix][sid]
            except KeyError:
                persistent_session_dict = self.PersistentSessionDict(sid=sid)
                self.zodb_root[self.prefix][sid] = persistent_session_dict

        request['session'] = persistent_session_dict
        return persistent_session_dict

    async def save(self, request, response) -> None:
        """Saves the session to the ZODB session store.

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
        if not request['session'].keys():
            if sid in self.zodb_root[self.prefix]:
                del self.zodb_root[self.prefix][sid]
                self.zodb_root._p_changed = True
                self.zodb_transaction.commit()
            if request['session']._p_changed:
                self._delete_cookie(request, response)
            return

        if request['session']._p_changed:
            self.zodb_root[self.prefix][sid].expires = _calculate_expires(self.expiry)
            self.zodb_transaction.commit()

        self._set_cookie_expiration(request, response)
        # BEFORE finishing must run removing old stuff from database

    def get_session(self, sid):
        try:
            val = self.zodb_root[self.prefix][sid]
        except KeyError:
            val = None
        return val
