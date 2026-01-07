def test_follow_user_successful(client, login_user, create_user):
    _, headers = login_user()
    target = create_user()

    res = client.post(f"/user/{target['username']}/follow", headers=headers)
    assert res.status_code == 204, res.text


def test_follow_user_username_not_found(client, login_user):
    _, headers = login_user()

    res = client.post("/user/target/follow", headers=headers)
    assert res.status_code == 404


def test_follow_user_to_itself(client, login_user):
    user, headers = login_user()

    res = client.post(f"/user/{user['username']}/follow", headers=headers)
    assert res.status_code == 400


def test_follow_user_twice(client, login_user, create_user):
    _, headers = login_user()
    target = create_user()

    res1 = client.post(f"/user/{target['username']}/follow", headers=headers)
    assert res1.status_code == 204

    res2 = client.post(f"/user/{target['username']}/follow", headers=headers)
    assert res2.status_code == 400


def test_follow_user_endpoint_unauthorized(client, create_user):
    target = create_user()

    res = client.post(f"/user/{target['username']}/follow")
    assert res.status_code == 401


def test_unfollow_user_successful(client, login_user, create_user):
    _, headers = login_user()
    target = create_user()


    res1 = client.post(f"/user/{target['username']}/follow", headers=headers)
    assert res1.status_code == 204, res1.text

    res2 = client.delete(f"/user/{target['username']}/follow", headers=headers)
    assert res2.status_code == 204, res2.text


def test_unfollow_user_username_not_found(client, login_user):
    _, headers = login_user()

    res = client.delete("/user/target/follow", headers=headers)
    assert res.status_code == 404


def test_unfollow_user_to_itself(client, login_user):
    user, headers = login_user()

    res = client.delete(f"/user/{user['username']}/follow", headers=headers)
    assert res.status_code == 400


def test_unfollow_user_not_following(client, login_user, create_user):
    _, headers = login_user()
    target = create_user()

    res = client.delete(f"/user/{target['username']}/follow", headers=headers)
    assert res.status_code == 400


def test_unfollow_user_endpoint_unauthorized(client, create_user, login_user):
    _, headers = login_user()
    target = create_user()


    res1 = client.post(f"/user/{target['username']}/follow", headers=headers)
    assert res1.status_code == 204, res1.text

    res2 = client.delete(f"/user/{target['username']}/follow")
    assert res2.status_code == 401, res2.text

def test_get_followers_success(client, login_user, create_user):
    follower_user, follower_headers = login_user()   
    target_user = create_user()                      

    res = client.post(f"/user/{target_user['username']}/follow", headers=follower_headers)
    assert res.status_code == 204, res.text

    res2 = client.get(f"/user/{target_user['username']}/followers")
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert isinstance(data, list)
    assert any(u["username"] == follower_user["username"] for u in data)


def test_get_followers_user_not_found(client):
    res = client.get("/user/not_a_real_user/followers")
    assert res.status_code == 404


def test_get_following_success(client, login_user, create_user):
    user_a, headers_a = login_user()   
    user_b = create_user()             

    res = client.post(f"/user/{user_b['username']}/follow", headers=headers_a)
    assert res.status_code == 204, res.text

    res2 = client.get(f"/user/{user_a['username']}/following")
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert isinstance(data, list)
    assert any(u["username"] == user_b["username"] for u in data)


def test_get_following_user_not_found(client):
    res = client.get("/user/not_a_real_user/following")
    assert res.status_code == 404
