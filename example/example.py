from sanic import Sanic
from sanic.response import text
from sanic_session import Session, InMemorySessionInterface

app = Sanic(name="Example App")
session = Session(app, interface=InMemorySessionInterface())


@app.route("/")
async def index(request):
    # interact with the session like a normal dict
    if not request.ctx.session.get("foo"):
        request.ctx.session["foo"] = 0

    request.ctx.session["foo"] += 1

    return text(request.ctx.session["foo"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
