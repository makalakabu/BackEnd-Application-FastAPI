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

    res = client.get("/tweet", headers=viewer_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    ids = {t["id"] for t in data}
    assert private_tweet_id in ids
    
def test_user_tweets_public_visible_anonymous(client, login_user):
    # Author (public by default)
    author, author_headers = login_user()

    t1 = client.post("/tweet", json={"body": "A1"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    t2 = client.post("/tweet", json={"body": "A2"}, headers=author_headers)
    assert t2.status_code == 201, t2.text

    # Anonymous can view public user's timeline
    res = client.get(f"/user/{author['username']}/tweets")
    assert res.status_code == 200, res.text

    data = res.json()
    bodies = [t["body"] for t in data]
    assert "A1" in bodies
    assert "A2" in bodies


def test_user_tweets_private_hidden_anonymous(client, login_user):
    # Author becomes private
    author, author_headers = login_user()

    priv = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv.status_code == 200, priv.text

    t1 = client.post("/tweet", json={"body": "Secret"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    # Anonymous should not be able to view private timeline (hide as 404)
    res = client.get(f"/user/{author['username']}/tweets")
    assert res.status_code == 404, res.text


def test_user_tweets_private_visible_to_follower(client, login_user, create_user):
    # Private author
    author, author_headers = login_user()

    priv = client.patch("/user/me", json={"is_private": True}, headers=author_headers)
    assert priv.status_code == 200, priv.text

    t1 = client.post("/tweet", json={"body": "Secret2"}, headers=author_headers)
    assert t1.status_code == 201, t1.text

    # Create follower and login
    follower_payload = create_user()
    _, follower_headers = login_user(follower_payload)

    # Follow the private author
    follow_res = client.post(f"/user/{author['username']}/follow", headers=follower_headers)
    assert follow_res.status_code == 204, follow_res.text

    # Now follower can view timeline
    res = client.get(f"/user/{author['username']}/tweets", headers=follower_headers)
    assert res.status_code == 200, res.text

    data = res.json()
    bodies = [t["body"] for t in data]
    assert "Secret2" in bodies







