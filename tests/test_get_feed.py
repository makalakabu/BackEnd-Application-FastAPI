def test_feed_unauthorized(client):
    res = client.get("/tweet/feed")
    assert res.status_code == 401


def test_feed_includes_own_tweets(client, login_user):
    _, headers = login_user()

    create = client.post("/tweet", json={"body": "My tweet"}, headers=headers)
    assert create.status_code == 201, create.text
    my_tweet_id = create.json()["id"]

    res = client.get("/tweet/feed", headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert isinstance(data, list)
    assert any(t["id"] == my_tweet_id for t in data)


def test_feed_includes_following_tweets(client, login_user, create_user):
    _, headers_me = login_user()

    target = create_user()

    login_target = client.post(
        "/auth/login",
        json={"email": target["email"], "password": target["password"]},
    )
    assert login_target.status_code == 200, login_target.text
    target_token = login_target.json()["access_token"]
    headers_target = {"Authorization": f"Bearer {target_token}"}

    tw = client.post("/tweet", json={"body": "Target tweet"}, headers=headers_target)
    assert tw.status_code == 201, tw.text
    target_tweet_id = tw.json()["id"]

    f = client.post(f"/user/{target['username']}/follow", headers=headers_me)
    assert f.status_code == 204, f.text

    res = client.get("/tweet/feed", headers=headers_me)
    assert res.status_code == 200, res.text
    data = res.json()
    assert any(t["id"] == target_tweet_id for t in data)


def test_feed_excludes_unfollowed_users_tweets(client, login_user, create_user):
    _, headers_me = login_user()

    other = create_user()

    login_other = client.post(
        "/auth/login",
        json={"email": other["email"], "password": other["password"]},
    )
    assert login_other.status_code == 200, login_other.text
    other_token = login_other.json()["access_token"]
    headers_other = {"Authorization": f"Bearer {other_token}"}

    tw = client.post("/tweet", json={"body": "Other tweet"}, headers=headers_other)
    assert tw.status_code == 201, tw.text
    other_tweet_id = tw.json()["id"]

    res = client.get("/tweet/feed", headers=headers_me)
    assert res.status_code == 200, res.text
    data = res.json()

    assert all(t["id"] != other_tweet_id for t in data)
