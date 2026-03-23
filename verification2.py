import requests

tests = [
    ("Home", "https://plantoai.vercel.app"),
    ("Backend", "https://plantoai-backend.onrender.com"),
    ("Plants API", "https://plantoai-backend.onrender.com/api/v1/plants"),
    ("Predict page", "https://plantoai.vercel.app/predict"),
    ("Plants page", "https://plantoai.vercel.app/plants"),
]

print("--- PLANTOAI LIVE VERIFICATION ---")
for name, url in tests:
    try:
        r = requests.get(url, timeout=30)
        data = r.json() if 'json' in r.headers.get('content-type', '') else {}
        count = len(data) if isinstance(data, list) else ''
        print(f"{name:15}: {r.status_code} {count}")
    except Exception as e:
        print(f"{name:15}: FAILED — {e}")
