import requests
import base64
import os

API_URL = "http://127.0.0.1:8000/api/v1/predict"
IMAGE_PATH = "C:\\Users\\HackRore\\.gemini\\antigravity\\brain\\c3e8516f-278d-4185-aff3-7fce14bae301\\tulsi_leaf_sample_1774552936244.png"

def test_debate():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: image not found at {IMAGE_PATH}")
        return

    with open(IMAGE_PATH, "rb") as f:
        files = {"file": ("tulsi.png", f, "image/png")}
        print("Sending request to /predict (with AI Debate)...")
        response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- AI DEBATE RESULT ---")
            debate = data.get("ai_debate")
            if debate:
                print(f"CNN: {debate.get('cnn_prediction')} ({debate.get('cnn_confidence')}%)")
                print(f"Gemini: {debate.get('gemini_prediction')}")
                print(f"Agreement: {debate.get('agreement')}")
                print(f"Explanation: {debate.get('explanation')}")
            else:
                print("No ai_debate in response (Gemini might be disabled or uninitialized)")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    test_debate()
