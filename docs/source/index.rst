.. sanic_session documentation master file, created by
   sphinx-quickstart on Tue Jan 10 00:43:29 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sanic_session
=========================================

.. toctree::
   :maxdepth: 1

   self
   using_the_interfaces
   api
   configuration
   testing

sanic_session is an extension for sanic that integrates server-backed sessions with a Flask-like API. 

sanic_session provides a number of *session interfaces* for you to store a client's session data. The interfaces available right now are:

* Redis
* Memcache
* In-Memory (suitable for testing and development environments)

See :ref:`using_the_interfaces` for instructions on using each.

A simple example uses the in-memory session interface.

.. code-block:: python

    from sanic import Sanic
    from sanic.response import text
    from sanic_session import InMemorySessionInterface


    app = Sanic()
    session_interface = InMemorySessionInterface()

    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)


    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)

    @app.route("/")
    async def index(request):
        # interact with the session like a normal dict
        if not request['session'].get('foo'):
            request['session']['foo'] = 0

        request['session']['foo'] += 1

        return text(request['session']['foo'])

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000, debug=True)



==================

* :ref:`using_the_interfaces`
* :ref:`api`
* :ref:`configuration`
* :ref:`testing`


