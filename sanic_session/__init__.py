from .memcache_session_interface import MemcacheSessionInterface
from .redis_session_interface import RedisSessionInterface
from .in_memory_session_interface import InMemorySessionInterface
from .zodb_session_interface import ZODBSessionInterface

# Delay exceptions for missing mongodb dependencies to allow us to
# work as long as mongodb is not being used.
try:
    from .mongodb_session_interface import MongoDBSessionInterface
except ModuleNotFoundError as e:
    saved_exception = e
    class MongoDBSessionInterface(object):
        def __init__(self, *args, **kwargs):
            raise saved_exception


def install_middleware(app, interface):
    """Installs middleware to application, which will be launched every request.
    'app' - sanic 'Application' instance to add middleware.
    'interface' - name of interface to use.
    Can be:
        InMemorySessionInterface, RedisSessionInterface,
        MemcacheSessionInterface, MongoDBSessionInterface
    """
    global session_interface
    if interface == 'InMemorySessionInterface':
        session_interface = InMemorySessionInterface()
    elif interface == 'MemcacheSessionInterface':
        session_interface = MemcacheSessionInterface()
    elif interface == 'RedisSessionInterface':
        session_interface = RedisSessionInterface()
    elif interface == 'MongoDBSessionInterface':
        session_interface = MongoDBSessionInterface()
    elif interface == 'ZODBSessionInterface':
        session_interface = ZODBSessionInterface()

    @app.middleware('request')
    async def add_session_to_request(request):
        """Before each request initialize a session using the client's request.
        """
        await session_interface.open(request)

    @app.middleware('response')
    async def save_session(request, response):
        """After each request save the session,
        pass the response to set client cookies.
        """
        await session_interface.save(request, response)
