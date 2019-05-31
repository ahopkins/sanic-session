from sanic_session.utils import ExpiringDict


def test_sets_expiry_internally():
    e = ExpiringDict()
    e.set("foo", "bar", 300)
    assert e.expiry_times["foo"] is not None


def test_returns_value_if_before_expiry():
    e = ExpiringDict()
    e.set("foo", "bar", 300)
    assert e.get("foo") is not None


def test_expires_value_if_after_expiry():
    e = ExpiringDict()
    e.set("foo", "bar", 300)
    e.expiry_times["foo"] = 0

    assert e.get("foo") is None
    assert e.expiry_times.get("foo") is None


def test_deletes_values():
    e = ExpiringDict()
    e.set("foo", "bar", 300)
    e.delete("foo")

    assert e.get("foo") is None
    assert e.expiry_times.get("foo") is None
