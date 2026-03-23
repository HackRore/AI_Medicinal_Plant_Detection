import requests

print("CHECKING BOTH URLS")
print("="*50)

for url in [
    "https://plantoai.vercel.app",
    "https://frontend-pi-ten-88.vercel.app"
]:
    try:
        r = requests.get(url, timeout=30)
        has_226 = "226" in r.text
        has_80 = ">80<" in r.text or "80 " in r.text
        has_demo = "demo mode" in r.text.lower()
        print(f"\nURL: {url}")
        print(f"  Still shows 226  : {has_226}")
        print(f"  Shows 80 species : {has_80}")
        print(f"  Demo banner      : {has_demo}")
        print(f"  Status           : {r.status_code}")
    except Exception as e:
        print(f"URL Failed: {e}")
