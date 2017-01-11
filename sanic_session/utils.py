import time
from typing import Union, Any


class _Missing(object):
    """
    Copyright (c) 2015 by Armin Ronacher and contributors.  See AUTHORS
    in FLASK_LICENSE for more details.
    """
    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'


_missing = _Missing()


class UpdateDictMixin(object):
    """
    Copyright (c) 2015 by Armin Ronacher and contributors.  See AUTHORS
    in FLASK_LICENSE for more details.
    """

    on_update = None

    def calls_update(name):
        def oncall(self, *args, **kw):
            rv = getattr(super(UpdateDictMixin, self), name)(*args, **kw)
            if self.on_update is not None:
                self.on_update(self)
            return rv
        oncall.__name__ = name
        return oncall

    def setdefault(self, key, default=None):
        modified = key not in self
        rv = super(UpdateDictMixin, self).setdefault(key, default)
        if modified and self.on_update is not None:
            self.on_update(self)
        return rv

    def pop(self, key, default=_missing):
        modified = key in self
        if default is _missing:
            rv = super(UpdateDictMixin, self).pop(key)
        else:
            rv = super(UpdateDictMixin, self).pop(key, default)
        if modified and self.on_update is not None:
            self.on_update(self)
        return rv

    __setitem__ = calls_update('__setitem__')
    __delitem__ = calls_update('__delitem__')
    clear = calls_update('clear')
    popitem = calls_update('popitem')
    update = calls_update('update')
    del calls_update


class CallbackDict(UpdateDictMixin, dict):

    """A dict that calls a function passed every time something is changed.
    The function is passed the dict instance.

    Copyright (c) 2015 by Armin Ronacher and contributors.  See AUTHORS
    in FLASK_LICENSE for more details.

    """

    def __init__(self, initial=None, on_update=None):
        dict.__init__(self, initial or ())
        self.on_update = on_update

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            dict.__repr__(self)
        )


class ExpiringDict(dict):
    def __init__(self, prefix=''):
        self.prefix = prefix
        super().__init__()
        self.expiry_times = {}

    def set(self, key: Union[str, int], val: Any, expiry: int):
        self[key] = val
        self.expiry_times[key] = time.time() + expiry

    def get_by_sid(self, key: str):
        key = self.prefix + key
        return self.get(key)

    def get(self, key: Union[str, int]):
        data = dict(self).get(key)

        if not data:
            return None

        if time.time() > self.expiry_times[key]:
            del self[key]
            del self.expiry_times[key]
            return None

        return data

    def delete(self, key: Union[str, int]):
        del self[key]
        del self.expiry_times[key]
