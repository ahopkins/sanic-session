import uuid

from datetime import datetime, timedelta

from sanic_motor import BaseModel
from sanic_session.base import BaseSessionInterface, SessionDict



class SessionModel(BaseModel):
	__coll__ = 'session'




class MongoDBSessionInterface(BaseSessionInterface):
	def __init__(
			self, app, domain: str=None, db_expiry: int=30*24*60*60,
			cookie_name: str='session'):
		self.expiry = 12*30*24*60*60        # 1year in browser
		self.cookie_name = cookie_name
		self.domain = domain
		self.httponly = True
		self.db_expiry = db_expiry

		# add indexes to session document
		@app.listener('after_server_start')
		async def apply_session_indexes(app, loop):
			await SessionModel.create_index('session:sid')
			await SessionModel.create_index('session:expiry', expireAfterSeconds=0)


	async def open(self, request):
		sid = request.cookies.get(self.cookie_name)

		if not sid:
			sid = uuid.uuid4().hex
			session_dict = SessionDict(sid=sid)
		else:
			document = await SessionModel.find_one({'session:sid': sid}, as_raw=True)

			if document is not None:
				document.pop('_id', None)
				document.pop('session:expiry', None)
				document.pop('session:sid', None)
				session_dict = SessionDict(document, sid=sid)
			else:
				session_dict = SessionDict(sid=sid)

		request['session'] = session_dict
		return session_dict


	async def save(self, request, response) -> None:
		if 'session' not in request:
			return

		sid = request['session'].sid	

		if not request['session']:
			await SessionModel.delete_one({'sid': sid})
			
			if request['session'].modified:
				self._delete_cookie(request, response)						

			return

		document = dict(request['session'])

		document['session:sid'] = sid
		document['session:expiry'] = \
			datetime.utcnow() + timedelta(seconds=self.db_expiry)

		await SessionModel.replace_one(
							{'session:sid': sid},
							document, upsert=True)

		self._set_cookie_expiration(request, response)
