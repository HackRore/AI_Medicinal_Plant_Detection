import requests

def final_verify():
    url = 'https://plantoai-backend.onrender.com/api/v1/predict'
    files = {
        'file': ('guava.png', open('screenshots/whatsapp_guava.png', 'rb'), 'image/png')
    }
    
    print("=== FINAL PRODUCTION VERIFICATION ===")
    try:
        r = requests.post(url, files=files, timeout=30)
        res = r.json()
        if res.get('success'):
            print(f"STATUS: SUCCESS")
            print(f"PLANT: {res['plant']['name']}")
            print(f"CONFIDENCE: {res['prediction']['confidence']}%")
            print(f"METHOD: {res['gradcam']['method']}")
        else:
            print(f"STATUS: FAILED")
            print(f"ERROR: {res.get('message') or res.get('error')}")
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    final_verify()
