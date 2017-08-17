import time
from sanic.response import text
from sanic_session.in_memory_session_interface import InMemorySessionInterface
import pytest
import uuid
import ujson


SID = '5235262626'
COOKIE_NAME = 'cookie'
COOKIES = {COOKIE_NAME: SID}


@pytest.fixture
def mock_dict():
    class MockDict(dict):
        pass

    return MockDict

@pytest.mark.asyncio
async def test_should_create_new_sid_if_no_cookie(mocker, mock_dict):
    request = mock_dict()
    request.cookies = {}

    mocker.spy(uuid, 'uuid4')
    session_interface = InMemorySessionInterface()
    await session_interface.open(request)

    assert uuid.uuid4.call_count == 1, 'should create a new SID with uuid'
    assert request['session'] == {}, 'should return an empty dict as session'


@pytest.mark.asyncio
async def test_custom_sid_generator(mocker, mock_dict):
    SID = "c0fe70cbd8ca8b798ceec7392bc3172c"

    def custom_generator():
        """A dummy SID generation protocol that returns a constant SID for unit testing"""
        return SID

    request = mock_dict()
    request.cookies = {}

    session_interface = InMemorySessionInterface(sid_generator=custom_generator)
    await session_interface.open(request)

    assert request["session"].sid == SID


@pytest.mark.asyncio
async def test_should_return_data_from_session_store(mocker, mock_dict):
    request = mock_dict()

    request.cookies = COOKIES

    mocker.spy(uuid, 'uuid4')
    data = {'foo': 'bar'}

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps(data))

    session = await session_interface.open(request)

    assert uuid.uuid4.call_count == 0, 'should not create a new SID'
    assert session_interface.session_store.get.call_count == 1, \
        'should call on redis once'

    assert session_interface.session_store.get.call_args_list[0][0][0] == \
        'session:{}'.format(SID), 'should get from store with prefix + SID'

    assert session.get('foo') == 'bar', 'session data is pulled from store'


@pytest.mark.asyncio
async def test_should_use_prefix_in_store_key(mocker, mock_dict):
    request = mock_dict()
    prefix = 'differentprefix:'
    data = {'foo': 'bar'}

    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps(data))
    await session_interface.open(request)

    assert session_interface.session_store.get.call_args_list[0][0][0] == \
        '{}{}'.format(prefix, SID), 'should call redis with prefix + SID'


@pytest.mark.asyncio
async def test_should_use_return_empty_session_via_store(mocker, mock_dict):
    request = mock_dict()
    prefix = 'differentprefix:'
    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=None)

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    session = await session_interface.open(request)

    assert session == {}


@pytest.mark.asyncio
async def test_should_attach_session_to_request(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=None)
    session = await session_interface.open(request)

    assert session == request['session']


@pytest.mark.asyncio
async def test_should_delete_session_from_store(mocker, mock_dict):
    request = mock_dict()
    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store['session:{}'.format(SID)] = '{foo:1}'
    session_interface.session_store.get = mocker.MagicMock(return_value=None)
    session_interface.session_store.delete = mocker.MagicMock()
    await session_interface.open(request)

    response = mocker.MagicMock()
    response.cookies = {}

    await session_interface.save(request, response)

    assert session_interface.session_store.delete.call_count == 1
    assert session_interface.session_store.delete.call_args_list[0][0][0] == \
        'session:{}'.format(SID)
    assert response.cookies == {}, 'should not change response cookies'


@pytest.mark.asyncio
async def test_should_expire_cookies_if_modified(mock_dict, mocker):
    request = mock_dict()
    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps({'foo': 'bar'}))
    session_interface.session_store.delete = mocker.MagicMock()

    await session_interface.open(request)
    response = text('foo')

    request['session'].clear()
    await session_interface.save(request, response)
    assert response.cookies[COOKIE_NAME]['max-age'] == 0
    assert response.cookies[COOKIE_NAME]['expires'] == 0


@pytest.mark.asyncio
async def test_should_save_in_memory_for_time_specified(mock_dict, mocker):
    request = mock_dict()
    request.cookies = COOKIES

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps({'foo': 'bar'}))
    session_interface.session_store.set = mocker.MagicMock()

    await session_interface.open(request)
    response = text('foo')
    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    session_interface.session_store.set.assert_called_with(
        'session:{}'.format(SID), ujson.dumps(request['session']), 2592000)


@pytest.mark.asyncio
async def test_should_reset_cookie_expiry(mocker, mock_dict):
    response = text('foo')

    request = mock_dict()
    request.cookies = COOKIES
    mocker.patch("time.time")
    time.time.return_value = 1488576462.138493

    session_interface = InMemorySessionInterface(
        cookie_name=COOKIE_NAME)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps({'foo': 'bar'}))
    session_interface.session_store.set = mocker.MagicMock()

    await session_interface.open(request)

    request['session']['foo'] = 'baz'
    await session_interface.save(request, response)

    assert response.cookies[COOKIE_NAME].value == SID
    assert response.cookies[COOKIE_NAME]['max-age'] == 2592000
    assert response.cookies[COOKIE_NAME]['expires'] == "Sun, 02-Apr-2017 21:27:42 GMT"
