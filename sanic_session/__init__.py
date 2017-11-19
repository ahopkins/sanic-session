from .memcache_session_interface import MemcacheSessionInterface
from .redis_session_interface import RedisSessionInterface
from .in_memory_session_interface import InMemorySessionInterface

# Delay exceptions for missing mongodb dependencies to allow us to
# work as long as mongodb is not being used.
try:
    from .mongodb_session_interface import MongoDBSessionInterface
except ModuleNotFoundError as e:
    saved_exception = e
    class MongoDBSessionInterface(object):
        def __init__(self, *args, **kwargs):
            raise saved_exception
