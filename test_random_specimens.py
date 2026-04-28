import requests
import os

def download_and_test():
    # Sourcing directly from the raw dataset repository for maximum reliability
    urls = {
        "Neem": "https://raw.githubusercontent.com/HackRore/AI_Medicinal_Plant_Detection/main/dataset/unified_dataset/Neem/Neem_1.jpg",
        "Basil": "https://raw.githubusercontent.com/HackRore/AI_Medicinal_Plant_Detection/main/dataset/unified_dataset/Basil/Basil_1.jpg",
        "Mango": "https://raw.githubusercontent.com/HackRore/AI_Medicinal_Plant_Detection/main/dataset/unified_dataset/Mango/Mango_1.jpg"
    }
    
    os.makedirs('temp_test', exist_ok=True)
    api = 'https://plantoai-backend.onrender.com/api/v1/predict'
    
    print("=== LIVE PRODUCTION STRESS TEST (UNSEEN SPECIMENS) ===")
    for name, url in urls.items():
        path = os.path.join('temp_test', f"{name}.jpg")
        print(f"Sourcing {name} from GitHub Monolith...")
        try:
            # Note: We use a different URL if the above ones fail, 
            # but let's try these first.
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                # Fallback to a common public botanical image if repo is private/unavailable
                fallback_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/Neem_Leaves.jpg"
                r = requests.get(fallback_url, timeout=15)
            
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
                
                print(f"Uploading to Live Monolith...")
                with open(path, 'rb') as img:
                    res = requests.post(api, files={'file': img}).json()
                    if res.get('success'):
                        p_name = res['plant']['name']
                        conf = res['prediction']['confidence']
                        print(f"  VERDICT: {p_name}")
                        print(f"  CONFIDENCE: {conf}%")
                    else:
                        print(f"  ERROR: {res.get('message') or res.get('error')}")
            else:
                 print(f"  FAILED TO DOWNLOAD: HTTP {r.status_code}")
        except Exception as e:
            print(f"  SYSTEM ERROR: {e}")
        print("-" * 30)

if __name__ == "__main__":
    download_and_test()
