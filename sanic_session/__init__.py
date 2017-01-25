#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .memcache_session_interface import MemcacheSessionInterface
from .redis_session_interface import RedisSessionInterface
from .in_memory_session_interface import InMemorySessionInterface


class SessionInterface:
    def __new__(cls, *args, **kwargs):
        backend = kwargs.pop('backend', 'memory')
        if backend == 'redis':
            return RedisSessionInterface(*args, **kwargs)
        elif backend == 'memcache':
            return MemcacheSessionInterface(*args, **kwargs)
        else:
            return InMemorySessionInterface(**kwargs)
