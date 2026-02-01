import uuid

from core.config import LOGIN_RATE_LIMIT, SIGNUP_RATE_LIMIT, TWEET_RATE_LIMIT


def test_login_rate_limit_exceeded(client, create_user, monkeypatch):
    from db.redis import redis_client

    user = create_user()

    def fake_eval(*_args, **_kwargs):
        return (LOGIN_RATE_LIMIT + 1, 30)

    monkeypatch.setattr(redis_client, "eval", fake_eval)

    res = client.post(
        "/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert res.status_code == 429


def test_signup_rate_limit_exceeded(client, create_user, monkeypatch):
    from db.redis import redis_client

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
        "password": "@Test1234-",
    }

    def fake_eval(*_args, **_kwargs):
        return (SIGNUP_RATE_LIMIT + 1, 30)

    monkeypatch.setattr(redis_client, "eval", fake_eval)

    res = client.post(
        "/auth/signup",
        json=payload,
    )
    assert res.status_code == 429


def test_tweet_rate_limit_exceeded(client, login_user, monkeypatch):
    from db.redis import redis_client

    _, headers = login_user()

    def fake_eval(*_args, **_kwargs):
        return (TWEET_RATE_LIMIT + 1, 30)

    monkeypatch.setattr(redis_client, "eval", fake_eval)

    res = client.post(
        "/tweet",
        json={"body": "Rate limited tweet"},
        headers=headers,
    )
    assert res.status_code == 429
