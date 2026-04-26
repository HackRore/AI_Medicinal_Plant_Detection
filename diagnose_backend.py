import requests
import json

BASE = "https://plantoai-backend.onrender.com"

print("=== BACKEND LIVE DIAGNOSTIC ===\n")

# Test 1: Stats
print("1. /api/v1/stats")
r = requests.get(f"{BASE}/api/v1/stats")
print(f"   Status: {r.status_code}")
print(f"   Data: {r.text[:120]}\n")

# Test 2: Plants list
print("2. /api/v1/plants")
r = requests.get(f"{BASE}/api/v1/plants")
print(f"   Status: {r.status_code}")
print(f"   Data: {r.text[:200]}\n")

# Test 3: Symptom search
print("3. POST /api/v1/symptom-search")
r = requests.post(f"{BASE}/api/v1/symptom-search", json={"symptoms": "fever and headache"}, timeout=30)
print(f"   Status: {r.status_code}")
print(f"   Data: {r.text[:300]}\n")

# Test 4: CORS headers on predict
print("4. CORS check on /api/v1/predict (OPTIONS)")
r = requests.options(f"{BASE}/api/v1/predict", headers={
    "Origin": "https://plantoai.vercel.app",
    "Access-Control-Request-Method": "POST"
})
print(f"   Status: {r.status_code}")
print(f"   Access-Control-Allow-Origin: {r.headers.get('access-control-allow-origin', 'MISSING')}")
print(f"   Access-Control-Allow-Methods: {r.headers.get('access-control-allow-methods', 'MISSING')}\n")

print("=== DIAGNOSTIC COMPLETE ===")
