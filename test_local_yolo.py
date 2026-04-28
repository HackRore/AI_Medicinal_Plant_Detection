import sys
import os

# Set up environment to test local
os.environ["DATABASE_URL"] = "sqlite:///plantoai.db"
os.environ["GEMINI_API_KEY"] = "mock"

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ml_service import ml_service

image_path = r"C:\Users\HackRore\OneDrive\Desktop\Temp testing Leaf Images\WhatsApp Image 2026-04-27 at 00.09.18.jpeg"

if not os.path.exists(image_path):
    print("Cannot find image, testing abort.")
else:
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    
    print("Running local inference...")
    result = ml_service.predict(img_bytes)
    print("Success:", result.get("success"))
    print("Plant:", result.get("plant_name") or result.get("predicted_class"))
    print("Explanation:", result.get("gradcam", {}).get("explanation"))
    print("Confidence:", result.get("confidence_pct"))
