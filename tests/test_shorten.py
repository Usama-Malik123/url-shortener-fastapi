from app.models import Url


def test_shorten_valid_url(client, db_session):
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200

    body = response.json()
    assert len(body["code"]) == 7
    assert body["target_url"] == "https://example.com/"
    assert body["short_url"].endswith(body["code"])

    stored = db_session.query(Url).filter(Url.code == body["code"]).first()
    assert stored is not None
    assert stored.target_url == "https://example.com/"


def test_shorten_invalid_url(client):
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422
