def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"


def test_health_redis_ok(client, monkeypatch):
    from db.redis import redis_client

    monkeypatch.setattr(redis_client, "ping", lambda: True)

    res = client.get("/health/redis")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_health_redis_unavailable(client, monkeypatch):
    from db.redis import redis_client

    def raise_error():
        raise Exception("boom")

    monkeypatch.setattr(redis_client, "ping", raise_error)

    res = client.get("/health/redis")
    assert res.status_code == 503
