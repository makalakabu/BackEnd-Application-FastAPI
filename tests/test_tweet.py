from core.jwt import decode_access_token


def _user_id_from_headers(headers: dict) -> int:
    token = headers["Authorization"].split(" ", 1)[1]
    payload = decode_access_token(token)
    return int(payload["sub"])


def test_tweet_create_sucessful(client, login_user):
    _, header = login_user()
    
    res = client.post(
        "/tweet",
        json={
            "body": "Test Tweet 123"
        },
        headers=header
    )
    assert res.status_code == 201

    data = res.json()
    assert data["body"] == "Test Tweet 123"
    assert "id" in data
    assert "created_at" in data
    assert "user" in data

def test_tweet_create_unauthorized(client):
    res = client.post(
        "/tweet",
        json={
            "body": "Test Tweet 123"
        }
    )
    assert res.status_code == 401

def test_list_of_tweets(client):
    res = client.get("/tweet/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_list_tweets_contains_created_tweet(client, login_user):
    _, headers = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Hello from list test"},
        headers=headers,
    )
    assert create_res.status_code == 201

    list_res = client.get("/tweet")
    assert list_res.status_code == 200

    data = list_res.json()
    assert len(data) >= 1
    assert data[0]["body"] == "Hello from list test"

def test_update_tweet_successful(client, login_user):
    _, headers = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Test Tweet 123"},
        headers=headers,
    )
    assert create_res.status_code == 201
    create_data = create_res.json()

    tweet_id = create_data["id"]
    update_res = client.patch(
        f"/tweet/{tweet_id}",
        json={"body": "Updated Tweet!"},
        headers=headers,
    )
    assert update_res.status_code == 200

    update_data = update_res.json()
    assert update_data["id"] == tweet_id
    assert update_data["body"] == "Updated Tweet!"

def test_update_tweet_unauthenticated(client, login_user):
    _, headers = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Test Tweet 123"},
        headers=headers,
    )
    assert create_res.status_code == 201
    create_data = create_res.json()

    tweet_id = create_data["id"]
    update_res = client.patch(
        f"/tweet/{tweet_id}",
        json={"body": "Updated Tweet!"},
    )
    assert update_res.status_code == 401

def test_update_tweet_forbidden_for_non_owner(client, login_user):
    _, headers_owner = login_user()
    _, headers_other = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Test Tweet 123"},
        headers=headers_owner,
    )
    assert create_res.status_code == 201
    tweet_id = create_res.json()["id"]

    update_res = client.patch(
        f"/tweet/{tweet_id}",
        json={"body": "Updated Tweet!"},
        headers=headers_other,
    )
    assert update_res.status_code == 403


def test_delete_tweet_successful(client, login_user):
    _, headers = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Delete me"},
        headers=headers,
    )
    assert create_res.status_code == 201
    tweet_id = create_res.json()["id"]

    delete_res = client.delete(
        f"/tweet/{tweet_id}",
        headers=headers,
    )
    assert delete_res.status_code == 204

def test_delete_tweet_unauthenticated(client, login_user):
    _, headers = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Cannot delete without token"},
        headers=headers,
    )
    assert create_res.status_code == 201
    tweet_id = create_res.json()["id"]

    delete_res = client.delete(f"/tweet/{tweet_id}")
    assert delete_res.status_code == 401


def test_delete_tweet_forbidden_for_non_owner(client, login_user):
    _, headers_owner = login_user()
    _, headers_other = login_user()

    create_res = client.post(
        "/tweet",
        json={"body": "Test Tweet 123"},
        headers=headers_owner,
    )
    assert create_res.status_code == 201
    tweet_id = create_res.json()["id"]

    update_res = client.delete(
        f"/tweet/{tweet_id}",
        headers=headers_other
    )
    assert update_res.status_code == 403

def test_update_tweet_invalidate_cache_called(client, login_user, monkeypatch):
    import service.tweet as tweet_service

    _, headers = login_user()
    create_res = client.post(
        "/tweet",
        json={"body": "Cache me"},
        headers=headers,
    )
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    calls = []

    def fake_invalidate_cache_by_pattern(*, r, match: str):
        calls.append(match)
        return 1

    monkeypatch.setattr(tweet_service, "invalidate_cache_by_pattern", fake_invalidate_cache_by_pattern)

    update_res = client.patch(
        f"/tweet/{tweet_id}",
        json={"body": "Updated body"},
        headers=headers,
    )
    assert update_res.status_code == 200, update_res.text
    assert calls == [f"v1:tweet:{tweet_id}:viewer:*"]

def test_delete_tweet_invalidate_cache_called(client, login_user, monkeypatch):
    import service.tweet as tweet_service

    _, headers = login_user()
    create_res = client.post(
        "/tweet",
        json={"body": "Cache me delete"},
        headers=headers,
    )
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    calls = []

    def fake_invalidate_cache_by_pattern(*, r, match: str):
        calls.append(match)
        return 1

    monkeypatch.setattr(tweet_service, "invalidate_cache_by_pattern", fake_invalidate_cache_by_pattern)

    delete_res = client.delete(
        f"/tweet/{tweet_id}",
        headers=headers,
    )
    assert delete_res.status_code == 204, delete_res.text
    assert calls == [f"v1:tweet:{tweet_id}:viewer:*"]

def test_get_tweet_by_id_public_visible_anonymous(client, login_user):
    _, author_headers = login_user()

    create_res = client.post("/tweet", json={"body": "Public tweet"}, headers=author_headers)
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    res = client.get(f"/tweet/{tweet_id}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["id"] == tweet_id
    assert data["body"] == "Public tweet"


def test_get_tweet_by_id_private_hidden_anonymous(client, login_user):
    _, author_headers = login_user()

    priv_res = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv_res.status_code == 200, priv_res.text

    create_res = client.post("/tweet", json={"body": "Private tweet"}, headers=author_headers)
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    res = client.get(f"/tweet/{tweet_id}")
    assert res.status_code == 404, res.text


def test_get_tweet_by_id_private_visible_to_follower(client, login_user, create_user):
    author, author_headers = login_user()
    priv_res = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv_res.status_code == 200, priv_res.text

    create_res = client.post("/tweet", json={"body": "Private tweet 2"}, headers=author_headers)
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    follower_payload = create_user()
    _, follower_headers = login_user(follower_payload)

    follow_res = client.post(f"/user/{author['username']}/follow", headers=follower_headers)
    assert follow_res.status_code == 204, follow_res.text
    requester_id = _user_id_from_headers(follower_headers)
    accept_res = client.post(f"/user/follow-request/{requester_id}/accept", headers=author_headers)
    assert accept_res.status_code == 200, accept_res.text

    res = client.get(f"/tweet/{tweet_id}", headers=follower_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["id"] == tweet_id
    assert data["body"] == "Private tweet 2"

def test_list_tweets_anonymous_only_public(client, login_user):
    _, public_headers = login_user()
    pub_tweet_res = client.post("/tweet", json={"body": "Public tweet"}, headers=public_headers)
    assert pub_tweet_res.status_code == 201, pub_tweet_res.text
    public_tweet_id = pub_tweet_res.json()["id"]

    _, private_headers = login_user()
    priv_patch = client.patch("/user/me", json={"is_private": True}, headers=private_headers)
    assert priv_patch.status_code == 200, priv_patch.text

    priv_tweet_res = client.post("/tweet", json={"body": "Private tweet"}, headers=private_headers)
    assert priv_tweet_res.status_code == 201, priv_tweet_res.text
    private_tweet_id = priv_tweet_res.json()["id"]

    res = client.get("/tweet")
    assert res.status_code == 200, res.text
    data = res.json()

    ids = {t["id"] for t in data}
    assert public_tweet_id in ids
    assert private_tweet_id not in ids


def test_list_tweets_logged_in_non_follower_cannot_see_private(client, login_user):
    _, private_headers = login_user()
    priv_patch = client.patch("/user/me", json={"is_private": True}, headers=private_headers)
    assert priv_patch.status_code == 200, priv_patch.text

    priv_tweet_res = client.post("/tweet", json={"body": "Private tweet X"}, headers=private_headers)
    assert priv_tweet_res.status_code == 201, priv_tweet_res.text
    private_tweet_id = priv_tweet_res.json()["id"]

    _, viewer_headers = login_user()

    res = client.get("/tweet", headers=viewer_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    ids = {t["id"] for t in data}
    assert private_tweet_id not in ids


def test_list_tweets_logged_in_follower_can_see_private(client, login_user):
    author, author_headers = login_user()
    priv_patch = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv_patch.status_code == 200, priv_patch.text

    priv_tweet_res = client.post("/tweet", json={"body": "Private tweet Y"}, headers=author_headers)
    assert priv_tweet_res.status_code == 201, priv_tweet_res.text
    private_tweet_id = priv_tweet_res.json()["id"]

    _, viewer_headers = login_user()

    follow_res = client.post(f"/user/{author['username']}/follow", headers=viewer_headers)
    assert follow_res.status_code == 204, follow_res.text
    requester_id = _user_id_from_headers(viewer_headers)
    accept_res = client.post(f"/user/follow-request/{requester_id}/accept", headers=author_headers)
    assert accept_res.status_code == 200, accept_res.text

    res = client.get("/tweet", headers=viewer_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    ids = {t["id"] for t in data}
    assert private_tweet_id in ids
    
def test_user_tweets_public_visible_anonymous(client, login_user):
    author, author_headers = login_user()

    t1 = client.post("/tweet", json={"body": "A1"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    t2 = client.post("/tweet", json={"body": "A2"}, headers=author_headers)
    assert t2.status_code == 201, t2.text

    res = client.get(f"/user/{author['username']}/tweets")
    assert res.status_code == 200, res.text

    data = res.json()
    bodies = [t["body"] for t in data]
    assert "A1" in bodies
    assert "A2" in bodies


def test_user_tweets_private_hidden_anonymous(client, login_user):
    author, author_headers = login_user()

    priv = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv.status_code == 200, priv.text

    t1 = client.post("/tweet", json={"body": "Secret"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    res = client.get(f"/user/{author['username']}/tweets")
    assert res.status_code == 404, res.text


def test_user_tweets_private_visible_to_follower(client, login_user, create_user):
    author, author_headers = login_user()

    priv = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv.status_code == 200, priv.text

    t1 = client.post("/tweet", json={"body": "Secret2"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    follower_payload = create_user()
    _, follower_headers = login_user(follower_payload)

    follow_res = client.post(f"/user/{author['username']}/follow", headers=follower_headers)
    assert follow_res.status_code == 204, follow_res.text
    requester_id = _user_id_from_headers(follower_headers)
    accept_res = client.post(f"/user/follow-request/{requester_id}/accept", headers=author_headers)
    assert accept_res.status_code == 200, accept_res.text

    res = client.get(f"/user/{author['username']}/tweets", headers=follower_headers)
    assert res.status_code == 200, res.text

    data = res.json()
    bodies = [t["body"] for t in data]
    assert "Secret2" in bodies


def test_get_tweet_by_id_cache_hit_uses_cache(client, login_user, monkeypatch):
    import service.tweet as tweet_service
    import json

    _, author_headers = login_user()

    create_res = client.post("/tweet", json={"body": "DB body"}, headers=author_headers)
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    cached_payload = {
        "id": tweet_id,
        "body": "Cached body",
        "created_at": "2024-01-01T00:00:00",
        "parent_id": None,
        "user": {"username": "cached_user", "image": None},
    }
    expected_key = f"v1:tweet:{tweet_id}:viewer:anon"

    def fake_get(key: str):
        assert key == expected_key
        return json.dumps(cached_payload)

    def fake_setex(*_args, **_kwargs):
        raise AssertionError("setex should not be called on cache hit")

    monkeypatch.setattr(tweet_service.redis_client, "get", fake_get)
    monkeypatch.setattr(tweet_service.redis_client, "setex", fake_setex)

    res = client.get(f"/tweet/{tweet_id}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["body"] == "Cached body"


def test_get_tweet_by_id_cache_miss_sets_cache(client, login_user, monkeypatch):
    import service.tweet as tweet_service
    import json

    _, author_headers = login_user()

    create_res = client.post("/tweet", json={"body": "DB body"}, headers=author_headers)
    assert create_res.status_code == 201, create_res.text
    tweet_id = create_res.json()["id"]

    expected_key = f"v1:tweet:{tweet_id}:viewer:anon"
    captured = {}

    def fake_get(_key: str):
        return None

    def fake_setex(key: str, ttl: int, value: str):
        captured["key"] = key
        captured["ttl"] = ttl
        captured["value"] = value

    monkeypatch.setattr(tweet_service.redis_client, "get", fake_get)
    monkeypatch.setattr(tweet_service.redis_client, "setex", fake_setex)

    res = client.get(f"/tweet/{tweet_id}")
    assert res.status_code == 200, res.text

    assert captured["key"] == expected_key
    assert captured["ttl"] == tweet_service.TWEET_REDIS_TTL_SECONDS
    payload = json.loads(captured["value"])
    assert payload["id"] == tweet_id
    assert payload["body"] == "DB body"

