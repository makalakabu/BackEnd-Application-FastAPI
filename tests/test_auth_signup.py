def test_signup_success(client):
    payload = {
        "username": "user1",
        "email": "user1@test.com",
        "password": "@Test1234-"
    }

    res = client.post("/auth/signup", json=payload)
    assert res.status_code == 201

    data = res.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"] 
    assert "password" not in data
    assert "password_hash" not in data



def test_signup_duplicate_email(client):
    payload1 = {
        "username": "user1",
        "email": "user1@test.com",
        "password": "@Test1234-"
    }

    payload2 = {
        "username": "user2",
        "email": "user1@test.com",
        "password": "@Test12345-"
    }

    res1 = client.post("/auth/signup", json = payload1)
    assert res1.status_code == 201

    res2 = client.post("/auth/signup", json = payload2)
    assert res2.status_code == 400




def test_signup_duplicate_username(client):
    payload1 = {
        "username": "user1",
        "email": "user1@test.com",
        "password": "@Test1234-"
    }

    payload2 = {
        "username": "user1",
        "email": "user2@test.com",
        "password": "@Test12345-"
    }

    res1 = client.post("/auth/signup", json = payload1)
    assert res1.status_code == 201

    res2 = client.post("/auth/signup", json = payload2)
    assert res2.status_code == 400

