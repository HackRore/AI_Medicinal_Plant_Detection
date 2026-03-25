import requests
import base64
import json

API_URL = "https://plantoai-backend.onrender.com/api/v1/predict/"
TEST_IMAGE_URL = "https://raw.githubusercontent.com/HackRore/AI_Medicinal_Plant_Detection/main/backend/tests/test_image.jpg"

def run_deep_audit():
    print("🚀 Starting Deep Production Audit...")
    
    # Get a test image
    img_data = requests.get(TEST_IMAGE_URL).content
    
    # Run prediction
    print("📤 Sending prediction request...")
    files = {"file": ("test.jpg", img_data, "image/jpeg")}
    response = requests.post(API_URL, files=files)
    
    if response.status_code != 200:
        print(f"❌ API Error: HTTP {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print("📥 Response received. Auditing fields...")

    # Audit logic similar to deep-tester.html
    audit = {
        "Plant Name": "predicted_class" in data,
        "Confidence Score": "confidence" in data,
        "Scientific Name": "plant_details" in data and "species_name" in data.get("plant_details", {}),
        "Toxicity Flag": "is_toxic" in data,
        "Ayurvedic Info": "medicinal_info" in data or "plant_details" in data,
        "Grad-CAM Data": "gradcam_base64" in data,
        "Top-5 Alternatives": "top_predictions" in data,
        "Model Version": "model_version" in data
    }

    print("\n--- AUDIT RESULTS ---")
    all_pass = True
    for field, passed in audit.items():
        status = "✅ PASS" if passed else "❌ MISSING"
        print(f"{field:20} : {status}")
        if not passed: all_pass = False
    
    print(f"\nLatency: {response.elapsed.total_seconds():.2f}s")
    
    if all_pass:
        print("\n✨ FINAL VERDICT: PRODUCTION API IS FULLY FEATURE-COMPLETE")
    else:
        print("\n⚠️ FINAL VERDICT: PRODUCTION API HAS MISSING FIELDS")

if __name__ == "__main__":
    run_deep_audit()
