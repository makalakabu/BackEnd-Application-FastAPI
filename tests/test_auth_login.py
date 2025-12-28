def test_login_succesful(client, create_user):
    user = create_user()

    res = client.post(
        "/auth/login", 
        json={
            "email": user["email"],
            "password": user["password"]
            }
        )
    assert res.status_code == 200

    data = res.json()
    assert "access_token" in data
    assert isinstance(data["access_token"],str)
    assert data["access_token"] != ""
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user["email"]
    assert data["user"]["username"] == user["username"]

def test_login_wrong_password_returns_401(client, create_user):
    user = create_user()

    res = client.post(
        "/auth/login",
        json={
            "email": user["email"],
            "password": "@Wrong1234-",  # wrong password
        },
    )

    assert res.status_code == 401

def test_login_user_not_found_returns_401(client):
    res = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@test.com",
            "password": "@Test1234-",
        },
    )

    assert res.status_code == 401
