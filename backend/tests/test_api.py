"""API smoke + behaviour tests for the basic tier."""
import os
import tempfile

import pytest

# Point the app at a throwaway database before it is imported.
_tmp = tempfile.mkdtemp(prefix="lixin_test_")
os.environ["LIXIN_DATA_DIR"] = _tmp
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp, 'test.db')}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.database import init_db  # noqa: E402


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_gift_crud_and_stats(client):
    # create
    r = client.post(
        "/api/gifts",
        json={"guest_name": "张三", "relation_group": "friend", "channel": "wechat", "amount": 888},
    )
    assert r.status_code == 201
    gid = r.json()["id"]
    assert r.json()["guest_name"] == "张三"
    assert r.json()["amount"] == 888.0

    # duplicate check should now flag the same guest
    r = client.get("/api/gifts/check-duplicate", params={"guest_name": "张三"})
    assert r.status_code == 200
    assert r.json()["duplicate"] is True

    # update
    r = client.put(f"/api/gifts/{gid}", json={"amount": 999})
    assert r.status_code == 200
    assert r.json()["amount"] == 999.0

    # stats reflect the record
    r = client.get("/api/stats")
    s = r.json()
    assert s["total_count"] >= 1
    assert s["total_amount"] >= 999.0
    wechat = next(c for c in s["by_channel"] if c["channel"] == "wechat")
    assert wechat["total"] >= 999.0

    # filter by group
    r = client.get("/api/gifts", params={"group": "friend"})
    assert any(g["id"] == gid for g in r.json())

    # delete
    r = client.delete(f"/api/gifts/{gid}")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_invalid_channel_rejected(client):
    r = client.post(
        "/api/gifts",
        json={"guest_name": "李四", "channel": "bitcoin", "amount": 100},
    )
    assert r.status_code == 422


def test_items(client):
    r = client.post(
        "/api/items",
        json={"guest_name": "王五", "item_name": "四件套", "quantity": 2, "relation_group": "relative"},
    )
    assert r.status_code == 201
    iid = r.json()["id"]
    r = client.get("/api/items")
    assert any(i["id"] == iid for i in r.json())
    assert client.delete(f"/api/items/{iid}").status_code == 200


def test_reminders(client):
    r = client.post(
        "/api/reminders",
        json={"title": "奶奶生日", "kind": "birthday", "remind_date": "2026-09-01"},
    )
    assert r.status_code == 201
    rid = r.json()["id"]
    r = client.get("/api/reminders")
    assert any(x["id"] == rid for x in r.json())
    assert client.delete(f"/api/reminders/{rid}").status_code == 200


def test_lock_flow(client):
    # initially disabled
    assert client.get("/api/lock/status").json()["enabled"] is False
    # set
    assert client.post("/api/lock/set", json={"password": "1234", "hint": "生日"}).status_code == 200
    assert client.get("/api/lock/status").json()["enabled"] is True
    # wrong password
    assert client.post("/api/lock/verify", json={"password": "0000"}).status_code == 401
    # right password
    assert client.post("/api/lock/verify", json={"password": "1234"}).status_code == 200
    # disable
    assert client.post("/api/lock/disable", json={"password": "1234"}).status_code == 200
    assert client.get("/api/lock/status").json()["enabled"] is False


def test_blessings(client):
    r = client.get("/api/blessings", params={"scene": "thanks_wedding"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
    tid = r.json()[0]["id"]
    r = client.get("/api/blessings/render", params={"id": tid, "name": "张姐"})
    assert r.status_code == 200
    assert "张姐" in r.json()["message"]
