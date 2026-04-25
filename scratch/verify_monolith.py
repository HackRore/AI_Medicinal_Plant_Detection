import requests
import json
import os
import time

TEST_IMAGES = [
    {"name": "Aloe Vera", "url": "https://images.unsplash.com/photo-1596541223130-5d31a73fb6c6?auto=format&fit=crop&w=800&q=80"},
    {"name": "Tulsi", "url": "https://images.unsplash.com/photo-1615485240384-58aa1b1399ff?auto=format&fit=crop&w=800&q=80"},
    {"name": "Neem", "url": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=800&q=80"},
    {"name": "Mint", "url": "https://images.unsplash.com/photo-1594481073320-33433e721696?auto=format&fit=crop&w=800&q=80"},
    {"name": "Mango", "url": "https://images.unsplash.com/photo-1553334820-552ee6c4663b?auto=format&fit=crop&w=800&q=80"},
    {"name": "Lemon", "url": "https://images.unsplash.com/photo-1590505677187-f9605fe2f8e7?auto=format&fit=crop&w=800&q=80"},
    {"name": "Hibiscus", "url": "https://images.unsplash.com/photo-1525310212502-a45392ee2f15?auto=format&fit=crop&w=800&q=80"},
    {"name": "Turmeric", "url": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=800&q=80"},
    {"name": "Ginger", "url": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=800&q=80"},
    {"name": "Amla", "url": "https://images.unsplash.com/photo-1628102476625-59274246114e?auto=format&fit=crop&w=800&q=80"}
]

API_URL = "http://localhost:8080/predict"

def verify():
    results = []
    print(f"Starting Neural Monolith Verification (10 Species)...")
    
    for item in TEST_IMAGES:
        print(f"Testing {item['name']}...")
        try:
            # Download image
            img_res = requests.get(item['url'], timeout=10)
            if img_res.status_code != 200:
                print(f"Download failed: {img_res.status_code}")
                results.append({"target": item['name'], "status": f"FAIL (DL {img_res.status_code})"})
                continue
            
            # Predict
            files = {'file': ('test.jpg', img_res.content, 'image/jpeg')}
            res = requests.post(API_URL, files=files, timeout=30)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    name = data.get("plant", {}).get("name", "Unknown")
                    conf = data.get("prediction", {}).get("confidence", 0)
                    results.append({
                        "target": item['name'],
                        "detected": name,
                        "confidence": f"{conf}%",
                        "status": "PASS"
                    })
                else:
                    results.append({"target": item['name'], "status": f"FAIL ({data.get('error')})"})
            else:
                results.append({"target": item['name'], "status": f"ERROR {res.status_code}"})
        except Exception as e:
            results.append({"target": item['name'], "status": f"EXCEPTION: {e}"})
        
        time.sleep(0.5)

    # Document in Markdown
    report = "# Neural Monolith Verification Report\n\n"
    report += "| Species | Detected | Confidence | Status |\n"
    report += "|---------|----------|------------|--------|\n"
    for r in results:
        report += f"| {r.get('target')} | {r.get('detected', 'N/A')} | {r.get('confidence', 'N/A')} | {r.get('status')} |\n"
    
    with open("TEST_RESULTS.md", "w") as f:
        f.write(report)
    
    print("Verification complete. Results saved to TEST_RESULTS.md")

if __name__ == "__main__":
    verify()
