def test_reply_create_successful(client, login_user):
    _, headers = login_user()

    parent_res = client.post(
        "/tweet",
        json={"body": "Parent tweet"},
        headers=headers,
    )
    assert parent_res.status_code == 201, parent_res.text
    parent_id = parent_res.json()["id"]

    reply_res = client.post(
        "/tweet",
        json={"body": "Reply tweet", "parent_id": parent_id},
        headers=headers,
    )
    assert reply_res.status_code == 201, reply_res.text
    data = reply_res.json()
    assert data["body"] == "Reply tweet"
    assert data["parent_id"] == parent_id


def test_reply_create_parent_not_found(client, login_user):
    _, headers = login_user()

    res = client.post(
        "/tweet",
        json={"body": "Reply invalid parent", "parent_id": 999999},
        headers=headers,
    )
    assert res.status_code == 400, res.text


def test_list_replies_only_direct_replies(client, login_user):
    _, headers = login_user()

    parent_res = client.post("/tweet", json={"body": "Parent"}, headers=headers)
    assert parent_res.status_code == 201, parent_res.text
    parent_id = parent_res.json()["id"]

    reply1 = client.post(
        "/tweet",
        json={"body": "Reply 1", "parent_id": parent_id},
        headers=headers,
    )
    reply2 = client.post(
        "/tweet",
        json={"body": "Reply 2", "parent_id": parent_id},
        headers=headers,
    )
    other = client.post("/tweet", json={"body": "Other tweet"}, headers=headers)

    assert reply1.status_code == 201, reply1.text
    assert reply2.status_code == 201, reply2.text
    assert other.status_code == 201, other.text

    res = client.get(f"/tweet/{parent_id}/replies")
    assert res.status_code == 200, res.text
    data = res.json()

    ids = {t["id"] for t in data}
    assert reply1.json()["id"] in ids
    assert reply2.json()["id"] in ids
    assert parent_id not in ids
    assert other.json()["id"] not in ids


def test_list_replies_private_reply_hidden_anonymous(client, login_user):
    _, public_headers = login_user()

    parent_res = client.post("/tweet", json={"body": "Parent public"}, headers=public_headers)
    assert parent_res.status_code == 201, parent_res.text
    parent_id = parent_res.json()["id"]

    _, private_headers = login_user()
    priv = client.patch("/user/me", json={"is_private": True}, headers=private_headers)
    assert priv.status_code == 200, priv.text

    private_reply = client.post(
        "/tweet",
        json={"body": "Private reply", "parent_id": parent_id},
        headers=private_headers,
    )
    assert private_reply.status_code == 201, private_reply.text
    private_reply_id = private_reply.json()["id"]

    res = client.get(f"/tweet/{parent_id}/replies")
    assert res.status_code == 200, res.text
    data = res.json()
    ids = {t["id"] for t in data}
    assert private_reply_id not in ids
