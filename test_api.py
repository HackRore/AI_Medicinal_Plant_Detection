import requests
from io import BytesIO
from PIL import Image

print("--- TESTING API ENDPOINT ---")
img = Image.new('RGB', (224, 224), color = 'green')
img_byte_arr = BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr.seek(0)

try:
    res = requests.post("http://127.0.0.1:8000/api/v1/predict/", files={"file": ("test.jpg", img_byte_arr, "image/jpeg")})
    data = res.json()
    print("API Response Keys:", data.keys())
    print("Predicted Class:", data.get('predicted_class'))
    print("Confidence:", data.get('confidence'))
    print("Is Toxic:", data.get('is_toxic'))
    print("Has Grad-CAM:", 'gradcam_base64' in data and data['gradcam_base64'] is not None)
    print("Medicinal Info:", data.get('medicinal_info'))
    if 'alternatives' in data:
        print(f"Alternatives provided: {len(data['alternatives'])}")
except Exception as e:
    print("API Test Failed:", e)
