def test_security_headers(client):
	response = client.get("/health")
	assert response.headers["x-content-type-options"] == "nosniff"
	assert response.headers["x-frame-options"] == "DENY"
	assert response.headers["referrer-policy"] == "no-referrer"
	assert response.headers["cache-control"] == "no-store"
