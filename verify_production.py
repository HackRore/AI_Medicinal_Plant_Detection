import requests
import time

URL = "https://plantoai.vercel.app"
print(f"VERIFYING LIVE SITE: {URL}")
print("="*60)

try:
    r = requests.get(URL, timeout=30)
    text = r.text
    
    # Check for 226 (OLD)
    has_226 = "226" in text
    # Check for 5000 (OLD)
    has_5000 = "5000" in text
    # Check for 40+ (OLD)
    has_40plus = "40+" in text or "40 +" in text
    
    # Check for 80 (FINAL VALUE)
    has_80_final = ">80<" in text or "80 Medicinal Species" in text
    
    # Check for /api-docs (OLD)
    has_old_docs = "/api-docs" in text
    
    # Check for /docs (NEW)
    has_new_docs = "/docs" in text

    print(f"Still shows 226   : {has_226} — {'FAIL' if has_226 else 'PASS'}")
    print(f"Still shows 5000+ : {has_5000} — {'FAIL' if has_5000 else 'PASS'}")
    print(f"Still shows 40+   : {has_40plus} — {'FAIL' if has_40plus else 'PASS'}")
    print(f"Shows 80 Species  : {has_80_final} — {'PASS' if has_80_final else 'FAIL'}")
    print(f"Broken /api-docs : {has_old_docs} — {'FAIL' if has_old_docs else 'PASS'}")
    print(f"Shows /docs       : {has_new_docs} — {'PASS' if has_new_docs else 'FAIL'}")
    
    if not has_226 and not has_5000 and has_80:
        print("\n✅ ALL PRODUCTION CHECKS PASSED!")
    else:
        print("\n❌ SOME CHECKS FAILED. Deployment may not have propagated yet.")

except Exception as e:
    print(f"ERROR connecting to site: {e}")
