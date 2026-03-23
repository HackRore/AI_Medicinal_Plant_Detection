import requests
import json

def check_live():
    url = "https://plantoai-backend.onrender.com/api/v1/plants/"
    try:
        r = requests.get(url, timeout=30)
        data = r.json()
        print(f"Total Plants: {data.get('total', 0)}")
        if data.get('total', 0) > 0:
            print("SAMPLE PLANT:", data.get('plants', [])[0]['species_name'])
        
        # Test a prediction to confirm Grad-CAM is now 'PRESENT'
        API = "https://plantoai-backend.onrender.com/api/v1/predict/"
        DATASET = r'd:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset\Aloevera\10.jpg'
        
        with open(DATASET, 'rb') as f:
            resp = requests.post(API, files={'file': ('test.jpg', f, 'image/jpeg')}, timeout=60)
        
        if resp.status_code == 200:
            res = resp.json()
            print(f"Prediction: {res.get('predicted_class')}")
            print(f"GradCAM is present? {'YES' if res.get('gradcam_base64') else 'NO'}")
        else:
            print(f"Prediction failed: {resp.status_code}")
            
    except Exception as e:
        print(f"Error checking live: {e}")

if __name__ == "__main__":
    check_live()
