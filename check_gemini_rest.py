import httpx
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.environ.get("GEMINI_API_KEY")

print("🔍 Searching for correct Gemini model name via REST...")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    r = httpx.get(url)
    if r.status_code == 200:
        models = r.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"  - {m['name']}")
    else:
        print(f"❌ Error {r.status_code}: {r.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
