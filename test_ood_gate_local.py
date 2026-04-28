"""
Quick local test: creates a synthetic "not a leaf" image and 
a synthetic "leaf-colored" image to verify OOD gate logic locally.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import numpy as np
from io import BytesIO
from PIL import Image

# Patch environment
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("GEMINI_API_KEY", "test")

from app.services.ml_service import ml_service

def make_test_image(color=(200, 100, 50), size=(224, 224)) -> bytes:
    """Create a solid-color synthetic test image."""
    img = Image.fromarray(np.full((*size, 3), color, dtype=np.uint8))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

print("=" * 60)
print("Local OOD Gate Test")
print("=" * 60)

# Test 1: Solid red image (should be rejected as OOD/unknown)
print("\nTest 1: Solid red noise (not a plant)")
red_img = make_test_image(color=(220, 50, 50))
r1 = ml_service.predict(red_img)
print(f"  Prediction: {r1.get('class_name', 'N/A')}")
print(f"  Confidence: {r1.get('confidence_pct', 0):.1f}%")
print(f"  Quality Passed: {r1.get('quality_passed', True)}")

# Test 2: Solid green image (might look leaf-like to model)
print("\nTest 2: Solid green noise (might trigger leaf class)")
green_img = make_test_image(color=(50, 180, 80))
r2 = ml_service.predict(green_img)
print(f"  Prediction: {r2.get('class_name', 'N/A')}")
print(f"  Confidence: {r2.get('confidence_pct', 0):.1f}%")
print(f"  Quality Passed: {r2.get('quality_passed', True)}")

# Test 3: Real leaf image if available
leaf_imgs = [f for f in os.listdir('screenshots') if f.endswith('.png') or f.endswith('.jpg')]
if leaf_imgs:
    print(f"\nTest 3: Real image ({leaf_imgs[0]})")
    with open(f"screenshots/{leaf_imgs[0]}", "rb") as f:
        real_img = f.read()
    r3 = ml_service.predict(real_img)
    print(f"  Prediction: {r3.get('class_name', 'N/A')}")
    print(f"  Confidence: {r3.get('confidence_pct', 0):.1f}%")
    print(f"  Label: {r3.get('confidence_label', 'N/A')}")
    print(f"  Quality Passed: {r3.get('quality_passed', True)}")

print("\nOOD Gate thresholds: entropy > 3.8 AND conf < 0.12")
print("Inference engine: ONNX EfficientNetV2-S + 7-pass TTA")
print("=" * 60)
