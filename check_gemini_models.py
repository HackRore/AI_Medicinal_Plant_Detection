import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

print("🔍 Scanning available Gemini models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
except Exception as e:
    print(f"❌ Scan Failed: {e}")
