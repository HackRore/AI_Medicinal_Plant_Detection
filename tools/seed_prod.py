import urllib.request
import json

PROD_URL = "https://plantoai-backend.onrender.com/api/v1/plants/admin/seed"

def seed_prod():
    print(f"🌱 Triggering Production Seeding at {PROD_URL}...")
    try:
        req = urllib.request.Request(PROD_URL, method='POST')
        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ Seeding Successful!")
                print(json.dumps(data, indent=2))
            else:
                print(f"❌ Seeding Failed: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    seed_prod()
