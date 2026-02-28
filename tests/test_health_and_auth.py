def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_register_login_me(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
            "nativeLanguage": "en",
            "learningLanguage": "es",
        },
    )
    assert reg.status_code == 201
    reg_data = reg.get_json()
    assert "token" in reg_data
    token = reg_data["token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    me_data = me.get_json()
    assert me_data["email"] == "test@example.com"

    login = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert login.status_code == 200
    login_data = login.get_json()
    assert "token" in login_data

