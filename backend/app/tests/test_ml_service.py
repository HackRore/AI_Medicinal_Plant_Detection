import pytest
import numpy as np
from PIL import Image
import io
from app.services.ml_service import MLService

@pytest.fixture
def ml_service():
    service = MLService()
    service.load_models() # This will likely fall back to mock since we are in test env or models missing
    return service

def test_ml_service_load(ml_service):
    assert ml_service.models_loaded is True
    assert len(ml_service.class_names) > 0

def test_preprocess_image(ml_service):
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    preprocessed = ml_service.preprocess_image(img_bytes)
    assert isinstance(preprocessed, np.ndarray)
    assert preprocessed.shape == (1, 3, 224, 224)

def test_prediction(ml_service):
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    result = ml_service.predict(img_bytes)
    assert "predicted_class" in result
    assert "confidence" in result
    assert len(result["top_predictions"]) > 0
