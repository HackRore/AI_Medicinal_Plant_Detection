import requests
import json

def test_symptom_search():
    url = "http://127.0.0.1:8000/api/v1/symptom-search"
    payload = {"symptoms": "persistent cough and sore throat for 3 days"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing API at {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_symptom_search()
