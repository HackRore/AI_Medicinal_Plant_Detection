import requests

try:
    headers = {"Origin": "http://127.0.0.1:3001"}
    response = requests.get("http://127.0.0.1:8000/health", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
