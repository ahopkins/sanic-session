.. _configuration:

Configuration
=========================================

When initializing a session interface, you have a number of optional arguments for configuring your session. 

**domain** (str, optional):
    Optional domain which will be attached to the cookie. Defaults to None.
**expiry** (int, optional):
    Seconds until the session should expire. Defaults to *2592000* (30 days). Setting this to 0 or None will set the session as permanent.
**httponly** (bool, optional):
    Adds the `httponly` flag to the session cookie. Defaults to True.
**cookie_name** (str, optional):
    Name used for the client cookie. Defaults to "session".
**prefix** (str, optional):
    Storage keys will take the format of `prefix+<session_id>`. Specify the prefix here.

**Example:**

.. code-block:: python

    session_interface = InMemorySessionInterface(
        domain='.example.com', expiry=0,
        httponly=False, cookie_name="cookie", prefix="sessionprefix:")

Will result in a session that:

- Will be valid only on *example.com*.
- Will never expire. 
- Will be accessible by Javascript.
- Will be named "cookie" on the client.
- will be named "sessionprefix:<sid>" in the session store.