from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Medicinal Plant Detection API" in response.json()["message"]

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_docs_accessible(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200
