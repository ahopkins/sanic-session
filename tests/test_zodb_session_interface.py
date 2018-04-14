import time
from sanic.response import text
from ..zodb_session_interface import ZODBSessionInterface  # change to sanic_session.zodb_session_interface
# on production
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


def get_zodb_conn():
    import ZODB, ZODB.FileStorage

    database_im = ZODB.DB(None)
    db_im_connection = database_im.open()
    db_im_root = db_im_connection.root()

    return db_im_connection


@pytest.mark.asyncio
async def test_should_create_new_sid_if_no_cookie(mocker, mock_dict):
    request = mock_dict()
    request.cookies = {}

    mocker.spy(uuid, 'uuid4')
    session_interface = ZODBSessionInterface(get_zodb_conn())
    await session_interface.open(request)

    assert uuid.uuid4.call_count == 1, 'should create a new SID with uuid'
    assert request['session'].keys() == {}.keys(), 'should return an empty dict as session'

"""
@pytest.mark.asyncio
async def test_should_return_data_from_session_store(mocker, mock_dict):
    request = mock_dict()

    request.cookies = COOKIES

    mocker.spy(uuid, 'uuid4')
    data = {'foo': 'bar'}

    session_interface = ZODBSessionInterface(*get_zodb_conn(),
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

    session_interface = ZODBSessionInterface(*get_zodb_conn(),
        cookie_name=COOKIE_NAME,
        prefix=prefix)
    session_interface.session_store.get = mocker.MagicMock(
        return_value=ujson.dumps(data))
    await session_interface.open(request)

    assert session_interface.session_store.get.call_args_list[0][0][0] == \
        '{}{}'.format(prefix, SID), 'should call redis with prefix + SID'




"""
