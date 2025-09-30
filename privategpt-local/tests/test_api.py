import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import app


def setup_module(module):
    os.environ["API_TOKEN"] = "test-token"


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_ingest_endpoint():
    client = TestClient(app)
    with patch("backend.app.ingest_paths", return_value=3) as mock_ingest:
        response = client.post(
            "/ingest",
            json={"paths": ["/data"]},
            headers={"Authorization": "Bearer test-token"},
        )
    assert response.status_code == 200
    assert response.json() == {"indexed": 3}
    mock_ingest.assert_called_once_with(["/data"])


def test_query_endpoint():
    client = TestClient(app)
    with patch("backend.app.ask", return_value=("Answer", ["doc1"])) as mock_ask:
        response = client.post(
            "/query",
            json={"question": "Hello?", "top_k": 2},
            headers={"Authorization": "test-token"},
        )
    assert response.status_code == 200
    assert response.json() == {"answer": "Answer", "sources": ["doc1"]}
    mock_ask.assert_called_once_with("Hello?", 2)
