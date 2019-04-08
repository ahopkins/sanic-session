import time
import datetime
from sanic.response import text
from sanic_session.memcache import MemcacheSessionInterface
import pytest
import uuid
import ujson

from unittest.mock import Mock

SID = '5235262626'
COOKIE_NAME = 'cookie'
COOKIES = {COOKIE_NAME: SID}


@pytest.fixture
def mock_dict():
    class MockDict(dict):
        pass

    return MockDict


@pytest.fixture
def mock_memcache():
    class MockMemcacheConnection:
        pass

    return MockMemcacheConnection


def mock_coroutine(return_value=None):
    async def mock_coro(*args, **kwargs):
        return return_value

    return Mock(wraps=mock_coro)


async def get_interface_and_request(mocker, memcache_connection, data=None):
    request = mock_dict()
    request.cookies = COOKIES
    data = data or {}

    memcache_connection = mock_memcache()
    memcache_connection.get = mock_coroutine(ujson.dumps(data))

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)
    await session_interface.open(request)

    return session_interface, request


@pytest.mark.asyncio
async def test_memcache_should_create_new_sid_if_no_cookie(
        mocker, mock_memcache, mock_dict):
    request = mock_dict()
    request.cookies = {}
    memcache_connection = mock_memcache()
    memcache_connection.get = mock_coroutine()

    mocker.spy(uuid, 'uuid4')
    session_interface = MemcacheSessionInterface(memcache_connection)
    await session_interface.open(request)

    assert uuid.uuid4.call_count == 1, 'should create a new SID with uuid'
    assert request['session'] == {}, 'should return an empty dict as session'


@pytest.mark.asyncio
async def test_should_return_data_from_memcache(
        mocker, mock_dict, mock_memcache):
    request = mock_dict()

    request.cookies = COOKIES

    mocker.spy(uuid, 'uuid4')
    data = {'foo': 'bar'}

    memcache_connection = mock_memcache()
    memcache_connection.get = mock_coroutine(ujson.dumps(data).encode())

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)
    session = await session_interface.open(request)

    assert uuid.uuid4.call_count == 0, 'should not create a new SID'
    assert memcache_connection.get.call_count == 1,\
        'should call on memcache once'
    assert memcache_connection.get.call_args_list[0][0][0] == \
        'session:{}'.format(SID).encode(), \
        'should call memcache with prefix + SID'
    assert session.get('foo') == 'bar', 'session data is pulled from memcache'


@pytest.mark.asyncio
async def test_should_use_prefix_in_memcache_key(
        mocker, mock_dict, mock_memcache):
    request = mock_dict()
    prefix = 'differentprefix:'
    data = {'foo': 'bar'}

    request.cookies = COOKIES

    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine(ujson.dumps(data).encode())

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    await session_interface.open(request)

    assert memcache_connection.get.call_args_list[0][0][0] == \
        '{}{}'.format(prefix, SID).encode(), \
        'should call memcache with prefix + SID'


@pytest.mark.asyncio
async def test_should_use_return_empty_session_via_memcache(
        mock_memcache, mock_dict):
    request = mock_dict()
    prefix = 'differentprefix:'
    request.cookies = COOKIES

    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine()

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    session = await session_interface.open(request)

    assert session == {}


@pytest.mark.asyncio
async def test_should_attach_session_to_request(mock_memcache, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES

    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine()

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)
    session = await session_interface.open(request)

    assert session == request['session']


@pytest.mark.asyncio
async def test_should_delete_session_from_memcache(mocker, mock_memcache, mock_dict):
    request = mock_dict()
    response = mock_dict()
    request.cookies = COOKIES
    response.cookies = {}

    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine()
    memcache_connection.delete = mock_coroutine()

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)

    await session_interface.open(request)
    await session_interface.save(request, response)

    assert memcache_connection.delete.call_count == 1
    assert(
        memcache_connection.delete.call_args_list[0][0][0] ==
        'session:{}'.format(SID).encode())
    assert response.cookies == {}, 'should not change response cookies'


@pytest.mark.asyncio
async def test_should_expire_memcache_cookies_if_modified(mock_dict, mock_memcache):
    request = mock_dict()
    response = text('foo')
    request.cookies = COOKIES

    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine()
    memcache_connection.delete = mock_coroutine()

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)

    await session_interface.open(request)

    request['session'].clear()
    await session_interface.save(request, response)
    assert response.cookies[COOKIE_NAME]['max-age'] == 0
    assert response.cookies[COOKIE_NAME]['expires'] < datetime.datetime.now()


@pytest.mark.asyncio
async def test_should_save_in_memcache_for_time_specified(mock_dict, mock_memcache):
    request = mock_dict()
    request.cookies = COOKIES
    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine(
        ujson.dumps({'foo': 'bar'}).encode())
    memcache_connection.set = mock_coroutine()
    response = text('foo')

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)

    await session_interface.open(request)

    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    memcache_connection.set.assert_called_with(
        'session:{}'.format(SID).encode(),
        ujson.dumps(request['session']).encode(), exptime=2592000)


@pytest.mark.asyncio
async def test_should_reset_cookie_expiry(mocker, mock_dict, mock_memcache):
    request = mock_dict()
    request.cookies = COOKIES
    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine(
        ujson.dumps({'foo': 'bar'}).encode())
    memcache_connection.set = mock_coroutine()
    response = text('foo')
    mocker.patch("time.time")
    time.time.return_value = 1488576462.138493

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME)

    await session_interface.open(request)
    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME].value == SID
    assert response.cookies[COOKIE_NAME]['max-age'] == 2592000
    assert response.cookies[COOKIE_NAME]['expires'] < datetime.datetime.now()


@pytest.mark.asyncio
async def test_sessioncookie_should_omit_request_headers(mocker, mock_dict, mock_memcache):
    request = mock_dict()
    request.cookies = COOKIES
    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine(
        ujson.dumps({'foo': 'bar'}).encode())
    memcache_connection.set = mock_coroutine()
    memcache_connection.delete = mock_coroutine()
    response = text('foo')

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME,
        sessioncookie=True)

    await session_interface.open(request)
    await session_interface.save(request, response)

    assert 'max-age' not in response.cookies[COOKIE_NAME]
    assert 'expires' not in response.cookies[COOKIE_NAME]


@pytest.mark.asyncio
async def test_sessioncookie_delete_has_expiration_headers(mocker, mock_dict, mock_memcache):
    request = mock_dict()
    request.cookies = COOKIES
    memcache_connection = mock_memcache
    memcache_connection.get = mock_coroutine(
        ujson.dumps({'foo': 'bar'}).encode())
    memcache_connection.set = mock_coroutine()
    memcache_connection.delete = mock_coroutine()
    response = text('foo')

    session_interface = MemcacheSessionInterface(
        memcache_connection,
        cookie_name=COOKIE_NAME,
        sessioncookie=True)

    await session_interface.open(request)
    await session_interface.save(request, response)
    request['session'].clear()
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME]['max-age'] == 0
    assert response.cookies[COOKIE_NAME]['expires'] < datetime.datetime.now()
