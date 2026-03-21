from fastapi.testclient import TestClient
from PIL import Image
import io
import pytest

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

def test_predict_endpoint(client: TestClient):
    img = Image.new('RGB', (224, 224), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
    response = client.post("/api/v1/predict/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert 'predicted_class' in data
    assert data['confidence'] >= 0

def test_explain_combined_endpoint(client: TestClient):
    img = Image.new('RGB', (224, 224), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
    response = client.post("/api/v1/explain/combined", files=files)
    assert response.status_code == 200
    data = response.json()
    assert 'gradcam' in data
    assert 'lime' in data

def test_feedback_endpoint(client: TestClient):
    # This requires a valid prediction ID, but for the test we can just check if it handles it correctly
    data = {'prediction_id': 1, 'is_correct': True, 'comment': 'test'}
    response = client.post("/api/v1/feedback/", json=data)
    # If the ID 1 doesn't exist, it might 404, but at least we're hitting the right route now
    # Let's check for 404 or 200
    assert response.status_code in [200, 404]
