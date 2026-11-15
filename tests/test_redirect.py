def test_redirect_to_target(client, redis_client):
    created = client.post("/shorten", json={"url": "https://example.com"}).json()
    code = created["code"]

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/"
    assert redis_client.get(f"url:{code}") == "https://example.com/"


def test_redirect_unknown_code(client):
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404
