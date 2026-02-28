def _register_and_get_token(client, email="user@example.com"):
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "nativeLanguage": "en"},
    )
    assert reg.status_code == 201
    return reg.get_json()["token"]


def test_list_categories_public(client, seed_categories):
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.get_json()
    assert any(c["slug"] == "reading" for c in data)
    # each category should have at least one level
    for c in data:
        assert "levels" in c


def test_reading_submit_creates_feedback(client, seed_reading_content):
    token = _register_and_get_token(client, email="reading@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    level_id = seed_reading_content["level"].id
    text_id = seed_reading_content["text"].id
    q = seed_reading_content["question"]

    texts = client.get(f"/api/reading/levels/{level_id}/texts", headers=headers)
    assert texts.status_code == 200

    submit = client.post(
        f"/api/reading/texts/{text_id}/submit",
        headers=headers,
        json={"answers": {q.id: "A sample"}},
    )
    assert submit.status_code == 201
    submit_data = submit.get_json()
    assert submit_data["score"] == 100
    assert submit_data["total"] >= 1
    assert "feedback" in submit_data

    fb = client.get("/api/feedback?type=reading", headers=headers)
    assert fb.status_code == 200
    fb_list = fb.get_json()
    assert len(fb_list) >= 1

