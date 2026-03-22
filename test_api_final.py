import requests
import json
import base64

image_path = r"C:\Users\HackRore\.gemini\antigravity\brain\b6042ab1-780d-4f1b-a1f9-47c8381f2324\tulsi_leaf_generated_1774200281361.png"

print("Uploading generated leaf image to PlantoAI API...")
url = "http://127.0.0.1:8000/api/v1/predict/"
try:
    with open(image_path, "rb") as f:
        response = requests.post(url, files={"file": ("tulsi_leaf.png", f, "image/png")})
    
    if response.status_code == 200:
        data = response.json()
        print("\n[SUCCESS]")
        print(f"Predicted Class: {data.get('predicted_class')}")
        print(f"Confidence: {data.get('confidence')}%")
        print(f"Is Toxic: {data.get('is_toxic')}")
        print(f"Caution: {data.get('caution')}")
        print(f"Medicinal Info Included: {bool(data.get('medicinal_info'))}")
        
        gradcam = data.get('gradcam_base64')
        if gradcam:
            print(f"Grad-CAM Heatmap Generated: YES (Base64 String Length: {len(gradcam)})")
        else:
            print("Grad-CAM Heatmap Generated: NO")
            
        alts = data.get('alternatives', [])
        print(f"Alternatives Found: {len(alts)}")
        for i, alt in enumerate(alts[:3]):
            print(f"  {i+1}. {alt['class_name']} ({alt['confidence']}%)")
            
    else:
        print(f"\n[Error] API Error: HTTP {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("\n[Error] Connection Refused. Uvicorn server is not running on port 8000.")
