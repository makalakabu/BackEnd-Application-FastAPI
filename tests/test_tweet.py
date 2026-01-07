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





