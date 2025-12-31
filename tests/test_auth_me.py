def test_successfull_me(client, create_user):
    user = create_user()

    login_res = client.post(
        "/auth/login",
        json = {
            "email": user["email"],
            "password": user["password"]
        }
    )
    assert login_res.status_code == 200

    access_token = login_res.json()["access_token"]
    token_type = login_res.json()["token_type"]

    res = client.get(
        "/auth/me",
        headers={
            "Authorization": f"{token_type} {access_token}"
            }
    )
    assert res.status_code == 200

    data = res.json()
    assert data["email"] == user["email"]
    assert data["username"] == user["username"]

def test_unsuccessfull_me(client):
    res = client.get("/auth/me")
    assert res.status_code == 401

def test_invalid_token_me(client):
    res = client.get(
        "/auth/me", 
        headers = {
            "Authorization": "Bearer Invalid-Token"
        } 
    )
    assert res.status_code == 401
