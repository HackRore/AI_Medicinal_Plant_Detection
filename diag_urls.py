import requests

def check_url(url):
    print(f"Checking: {url}")
    try:
        r = requests.get(url, timeout=30)
        text = r.text
        has_40 = "40+" in text or "40 +" in text
        has_80 = "80" in text
        print(f"  Has 40+: {has_40}")
        print(f"  Has 80 : {has_80}")
        if has_40 and not has_80:
            print("  STATUS: STALE")
        elif has_80 and not has_40:
             print("  STATUS: UPDATED")
        else:
             print("  STATUS: MIXED or UNKNOWN")
    except Exception as e:
        print(f"  ERROR: {e}")

urls = [
    "https://plantoai.vercel.app",
    "https://frontend-pi-ten-88.vercel.app"
]

for url in urls:
    check_url(url)
