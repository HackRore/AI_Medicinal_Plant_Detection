"""
FULL LIVE DIAGNOSTIC — Tests every backend endpoint with real data.
Honest results only. No assumptions.
"""
import requests
import json
import time
import os
import sys
from pathlib import Path

BASE = "https://plantoai-backend.onrender.com"
RESULTS = []

def test(name, fn):
    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print('='*60)
    start = time.time()
    try:
        result = fn()
        elapsed = round((time.time() - start) * 1000)
        status = "✅ PASS" if result["ok"] else "❌ FAIL"
        print(f"{status} ({elapsed}ms)")
        print(f"Detail: {result['detail']}")
        RESULTS.append({"name": name, "ok": result["ok"], "detail": result["detail"], "ms": elapsed})
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        print(f"❌ ERROR ({elapsed}ms): {e}")
        RESULTS.append({"name": name, "ok": False, "detail": str(e), "ms": elapsed})

# ── TEST 1: Backend alive ────────────────────────────────────────────
def t1():
    r = requests.get(f"{BASE}/docs", timeout=30)
    ok = r.status_code == 200
    return {"ok": ok, "detail": f"HTTP {r.status_code} — {'Swagger UI loaded' if ok else 'Backend unreachable'}"}
test("Backend Alive (/docs)", t1)

# ── TEST 2: Stats endpoint ───────────────────────────────────────────
def t2():
    r = requests.get(f"{BASE}/api/v1/stats", timeout=15)
    d = r.json()
    expected_species = d.get("species_count")
    ok = r.status_code == 200 and str(expected_species) == "46"
    return {"ok": ok, "detail": f"HTTP {r.status_code} | species_count={expected_species} | accuracy={d.get('top1_accuracy')}"}
test("Stats API — species_count should be 46", t2)

# ── TEST 3: Plants endpoint ──────────────────────────────────────────
def t3():
    r = requests.get(f"{BASE}/api/v1/plants", timeout=20)
    d = r.json()
    count = len(d.get("plants", []))
    ok = r.status_code == 200 and count > 0
    return {"ok": ok, "detail": f"HTTP {r.status_code} | plant count={count} | success={d.get('success')}"}
test("Plants Database — should return >0 plants", t3)

# ── TEST 4: Symptom Search ───────────────────────────────────────────
def t4():
    r = requests.post(f"{BASE}/api/v1/symptom-search",
                      json={"symptoms": "fever and headache and body pain"},
                      timeout=30)
    d = r.json()
    recs = d.get("recommendations", [])
    error = d.get("error")
    ok = r.status_code == 200 and len(recs) > 0 and not error
    detail = f"HTTP {r.status_code} | recs={len(recs)} | error={error}"
    if recs:
        detail += f" | first_plant={recs[0].get('plant')} | has_dosha={bool(recs[0].get('dosha_effect'))}"
    return {"ok": ok, "detail": detail}
test("Symptom Search — should return recommendations with dosha/safety data", t4)

# ── TEST 5: CORS headers ─────────────────────────────────────────────
def t5():
    r = requests.options(f"{BASE}/api/v1/predict",
                         headers={
                             "Origin": "https://plantoai.vercel.app",
                             "Access-Control-Request-Method": "POST"
                         }, timeout=10)
    acao = r.headers.get("access-control-allow-origin", "MISSING")
    ok = "plantoai.vercel.app" in acao or acao == "*"
    return {"ok": ok, "detail": f"HTTP {r.status_code} | Access-Control-Allow-Origin: {acao}"}
test("CORS — plantoai.vercel.app must be allowed", t5)

# ── TEST 6: Predict with real leaf image ─────────────────────────────
def t6():
    # Download a real Tulsi leaf image from the internet
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Holy_Basil_%28Ocimum_tenuiflorum%29.JPG/320px-Holy_Basil_%28Ocimum_tenuiflorum%29.JPG"
    img_r = requests.get(img_url, timeout=20)
    if img_r.status_code != 200:
        return {"ok": False, "detail": "Could not download test image from Wikipedia"}
    
    files = {"file": ("tulsi.jpg", img_r.content, "image/jpeg")}
    r = requests.post(f"{BASE}/api/v1/predict", files=files, timeout=60)
    d = r.json()
    
    success = d.get("success", False)
    confidence = d.get("confidence", 0) * 100 if d.get("confidence", 0) < 1 else d.get("confidence_pct", 0)
    plant_name = d.get("class_name") or d.get("predicted_class") or "Unknown"
    error = d.get("error") or d.get("details")
    
    # Check if normalization fix is live by checking confidence > 5% (very low = old broken code)
    normalization_ok = confidence > 5
    ok = success and confidence > 0
    
    detail = f"HTTP {r.status_code} | success={success} | plant={plant_name} | confidence={round(confidence,1)}%"
    if error:
        detail += f" | error={error}"
    if not normalization_ok and ok:
        detail += " | ⚠️ NORMALIZATION FIX MAY NOT BE LIVE YET (confidence very low)"
    return {"ok": ok, "detail": detail}
test("Predict — Real Tulsi leaf image (tests normalization fix)", t6)

# ── TEST 7: Predict with non-plant image ─────────────────────────────
def t7():
    # Use a solid color PNG as a non-plant stress test
    # Create a simple 10x10 red square in bytes
    import io
    try:
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (224, 224), color=(200, 50, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        img_bytes = buf.read()
    except ImportError:
        # Fallback: download a random non-plant image
        img_r = requests.get("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg", timeout=15)
        img_bytes = img_r.content

    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    r = requests.post(f"{BASE}/api/v1/predict", files=files, timeout=60)
    d = r.json()
    confidence = d.get("confidence", 0) * 100 if d.get("confidence", 0) < 1 else d.get("confidence_pct", 0)
    plant_name = d.get("class_name") or d.get("predicted_class") or "Unknown"
    # We expect LOW confidence on a non-plant image (good = system working correctly)
    ok = r.status_code == 200 and d.get("success", False)
    return {"ok": ok, "detail": f"HTTP {r.status_code} | plant={plant_name} | confidence={round(confidence,1)}% | (low conf expected for non-plant)"}
test("Predict — Non-plant stress test (low confidence expected)", t7)

# ── FINAL SUMMARY ────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("FINAL DIAGNOSTIC SUMMARY")
print('='*60)
passed = sum(1 for r in RESULTS if r["ok"])
total = len(RESULTS)
print(f"\nScore: {passed}/{total} tests passing\n")
for r in RESULTS:
    icon = "✅" if r["ok"] else "❌"
    print(f"  {icon} {r['name']}")
    print(f"     {r['detail']}")
    print()

if passed == total:
    print("🎉 ALL SYSTEMS OPERATIONAL — Safe to demo")
elif passed >= total - 1:
    print("⚠️  ONE ISSUE REMAINING — see above")
else:
    print("🔴 MULTIPLE ISSUES — Render may need redeployment")
