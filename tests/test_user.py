from core.jwt import decode_access_token


def _user_id_from_headers(headers: dict) -> int:
    token = headers["Authorization"].split(" ", 1)[1]
    payload = decode_access_token(token)
    return int(payload["sub"])


def _make_private(client, headers):
    res = client.patch("/user/me", json={"is_private": True}, headers=headers)
    assert res.status_code == 200, res.text


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

def test_patch_me_unauthorized(client):
    res = client.patch("/user/me", json={"bio": "hello"})
    assert res.status_code == 401


def test_patch_me_update_bio_success(client, login_user):
    user, headers = login_user()

    res = client.patch("/user/me", json={"bio": "New bio"}, headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert data["username"] == user["username"]
    assert data["bio"] == "New bio"


def test_patch_me_update_image_success(client, login_user):
    user, headers = login_user()

    res = client.patch("/user/me", json={"image": "https://example.com/pic.png"}, headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert data["username"] == user["username"]
    assert data["image"] == "https://example.com/pic.png"


def test_patch_me_update_multiple_fields_success(client, login_user):
    user, headers = login_user()

    payload = {"bio": "Bio v2", "image": "https://example.com/new.png"}
    res = client.patch("/user/me", json=payload, headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert data["username"] == user["username"]
    assert data["bio"] == "Bio v2"
    assert data["image"] == "https://example.com/new.png"


def test_patch_me_empty_body_no_change(client, login_user):
    user, headers = login_user()

    res1 = client.patch("/user/me", json={"bio": "Keep me"}, headers=headers)
    assert res1.status_code == 200, res1.text

    res2 = client.patch("/user/me", json={}, headers=headers)
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert data["bio"] == "Keep me"


def test_patch_me_rejects_extra_fields(client, login_user):
    _, headers = login_user()

    res = client.patch("/user/me", json={"not_a_field": "x"}, headers=headers)
    assert res.status_code == 422

def test_get_user_profile_success_counts(client, create_user, login_user):
    target = create_user()

    _, follower_headers = login_user()

    res = client.post(f"/user/{target['username']}/follow", headers=follower_headers)
    assert res.status_code == 204, res.text

    res2 = client.get(f"/user/{target['username']}")
    assert res2.status_code == 200, res2.text

    data = res2.json()
    assert data["username"] == target["username"]
    assert data["email"] == target["email"]

    assert data["followers_count"] == 1
    assert data["following_count"] == 0


def test_get_user_profile_not_found(client):
    res = client.get("/user/not_a_real_user_123456")
    assert res.status_code == 404


def test_follow_private_user_creates_request_and_listed(client, login_user):
    target, target_headers = login_user()
    _make_private(client, target_headers)

    requester, requester_headers = login_user()

    res = client.post(f"/user/{target['username']}/follow", headers=requester_headers)
    assert res.status_code == 204, res.text

    list_res = client.get("/user/follow-request", headers=target_headers)
    assert list_res.status_code == 200, list_res.text
    data = list_res.json()
    assert isinstance(data, list)
    assert any(u["username"] == requester["username"] for u in data)

    followers_res = client.get(f"/user/{target['username']}/followers")
    assert followers_res.status_code == 200, followers_res.text
    followers = followers_res.json()
    assert all(u["username"] != requester["username"] for u in followers)


def test_accept_follow_request_creates_follow_and_clears_request(client, login_user):
    target, target_headers = login_user()
    _make_private(client, target_headers)

    requester, requester_headers = login_user()
    requester_id = _user_id_from_headers(requester_headers)

    res = client.post(f"/user/{target['username']}/follow", headers=requester_headers)
    assert res.status_code == 204, res.text

    accept_res = client.post(f"/user/follow-request/{requester_id}/accept", headers=target_headers)
    assert accept_res.status_code == 200, accept_res.text

    followers_res = client.get(f"/user/{target['username']}/followers")
    assert followers_res.status_code == 200, followers_res.text
    followers = followers_res.json()
    assert any(u["username"] == requester["username"] for u in followers)

    list_res = client.get("/user/follow-request", headers=target_headers)
    assert list_res.status_code == 200, list_res.text
    data = list_res.json()
    assert all(u["username"] != requester["username"] for u in data)


def test_reject_follow_request_removes_request_only(client, login_user):
    target, target_headers = login_user()
    _make_private(client, target_headers)

    requester, requester_headers = login_user()
    requester_id = _user_id_from_headers(requester_headers)

    res = client.post(f"/user/{target['username']}/follow", headers=requester_headers)
    assert res.status_code == 204, res.text

    reject_res = client.post(f"/user/follow-request/{requester_id}/reject", headers=target_headers)
    assert reject_res.status_code == 200, reject_res.text

    list_res = client.get("/user/follow-request", headers=target_headers)
    assert list_res.status_code == 200, list_res.text
    data = list_res.json()
    assert all(u["username"] != requester["username"] for u in data)

    followers_res = client.get(f"/user/{target['username']}/followers")
    assert followers_res.status_code == 200, followers_res.text
    followers = followers_res.json()
    assert all(u["username"] != requester["username"] for u in followers)


def test_follow_request_duplicate_rejected(client, login_user):
    target, target_headers = login_user()
    _make_private(client, target_headers)

    _, requester_headers = login_user()

    res1 = client.post(f"/user/{target['username']}/follow", headers=requester_headers)
    assert res1.status_code == 204, res1.text

    res2 = client.post(f"/user/{target['username']}/follow", headers=requester_headers)
    assert res2.status_code == 400, res2.text


def test_follow_request_list_unauthorized(client):
    res = client.get("/user/follow-request")
    assert res.status_code == 401
