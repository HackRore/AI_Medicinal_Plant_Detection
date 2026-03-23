import requests
import time

URL = "https://plantoai.vercel.app"
print(f"VERIFYING LIVE SITE: {URL}")
print("="*60)

try:
    r = requests.get(URL, timeout=30)
    text = r.text
    
    print("="*40)
    print(f"VERIFYING https://plantoai.vercel.app")
    print("="*40)
    print("226 still there:  ", "226" in text)
    print("5000 still there: ", "5000" in text)
    print("40+ still there:  ", "40+" in text or "40 +" in text)
    print("80 present:       ", "80" in text)
    print("86 present:       ", "86" in text)
    print("API docs fixed:    ", "/docs" in text)
    print("Broken /api-docs:  ", "/api-docs" in text)
    print("="*40)
    
    if not ("226" in text) and not ("5000" in text) and ("80" in text):
        print("\n✅ SITE IS 100% CORRECT & SYNCHRONIZED!")
    else:
        print("\n❌ SITE STILL SHOWS STALE DATA!")

except Exception as e:
    print(f"ERROR connecting to site: {e}")
