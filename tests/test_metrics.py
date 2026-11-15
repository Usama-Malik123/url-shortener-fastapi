def test_metrics_exposes_prometheus_format(client):
    client.get("/health")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "http_requests_total" in response.text
