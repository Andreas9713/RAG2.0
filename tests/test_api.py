import os

from fastapi.testclient import TestClient

os.environ["API_TOKEN"] = "test-token"

from backend.app import app  # noqa: E402


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_requires_token():
    response = client.post("/ingest", json={"paths": []})
    assert response.status_code == 401
