"""
PlantoAI Final Live Audit — 4 Scenario Test
Tests all four scenarios the guide specified must pass.
"""
import requests
import time

API = "https://plantoai-backend.onrender.com"
FRONTEND = "https://plantoai.vercel.app"

print("=" * 65)
print("PLANTOAI FINAL LIVE AUDIT")
print("=" * 65)

results = {}

# ── Backend Health Check ──────────────────────────────────────────
print("\n[1] Backend Health Check")
try:
    r = requests.get(f"{API}/health", timeout=45)
    d = r.json()
    status       = d.get("status", "unknown")
    neural       = d.get("telemetry", {}).get("neural_monolith", False)
    kb           = d.get("telemetry", {}).get("botanical_kb", False)
    registry     = d.get("registry", 0)
    print(f"    Status    : {status}")
    print(f"    Neural    : {neural}")
    print(f"    KB        : {kb}")
    print(f"    Registry  : {registry} taxa")
    results["health"] = status == "synchronized" and neural and kb
except Exception as e:
    print(f"    FAIL: {e}")
    results["health"] = False

# ── API Root Version ──────────────────────────────────────────────
print("\n[2] API Version Check")
try:
    r = requests.get(f"{API}/", timeout=20)
    d = r.json()
    print(f"    Version   : {d.get('message','?')}")
    print(f"    ML Loaded : {d.get('ml_loaded','?')}")
    results["version"] = d.get("ml_loaded", False)
except Exception as e:
    print(f"    FAIL: {e}")
    results["version"] = False

# ── Test A: Real leaf prediction ──────────────────────────────────
print("\n[3] Test A — Real leaf photo via WhatsApp images")
import os
test_images = [f for f in os.listdir(".") 
               if f.startswith("WhatsApp") and (f.endswith(".jpg") or f.endswith(".jpeg"))]
if test_images:
    img = test_images[0]
    try:
        with open(img, "rb") as f:
            r = requests.post(f"{API}/api/v1/predict",
                            files={"file": (img, f, "image/jpeg")},
                            timeout=60)
        d = r.json()
        success    = d.get("success", False)
        plant      = d.get("plant", {}).get("name", "?") if success else d.get("error","?")
        conf       = d.get("prediction", {}).get("confidence", 0) if success else 0
        stage2     = d.get("stage2_check", {})
        stage5     = d.get("vision_validation", {})
        print(f"    Image     : {img}")
        print(f"    Success   : {success}")
        print(f"    Plant     : {plant}")
        print(f"    Conf      : {conf:.1f}%")
        print(f"    Stage2    : is_leaf={stage2.get('is_leaf','?')} quality={stage2.get('image_quality','?')}")
        print(f"    Stage5    : matches={stage5.get('matches_prediction','?')} agree={stage5.get('agreement_score','?')}")
        results["leaf_predict"] = success
    except Exception as e:
        print(f"    FAIL: {e}")
        results["leaf_predict"] = False
else:
    print("    SKIP: No WhatsApp images found in current directory")
    results["leaf_predict"] = "SKIP"

# ── Test B: Symptom Search ────────────────────────────────────────
print("\n[4] Test B — Symptom Search endpoint")
try:
    r = requests.post(f"{API}/api/v1/symptom-search",
                     json={"symptoms": "I have fever, body aches and feel tired"},
                     timeout=30)
    d = r.json()
    recs = d.get("recommendations", [])
    print(f"    Recommendations : {len(recs)}")
    for rec in recs[:2]:
        print(f"      -> {rec.get('plant','?')} - {rec.get('why','?')[:60]}...")
    results["symptom_search"] = len(recs) >= 1
except Exception as e:
    print(f"    FAIL: {e}")
    results["symptom_search"] = False

# ── Test C: Plants database endpoint ─────────────────────────────
print("\n[5] Test C — Plants Database API")
try:
    r = requests.get(f"{API}/api/v1/plants?limit=5", timeout=20)
    d = r.json()
    plants = d.get("plants", [])
    total  = d.get("total", 0)
    print(f"    Total plants  : {total}")
    print(f"    Sample        : {', '.join(p.get('common_name','?') for p in plants[:3])}")
    results["plants_api"] = len(plants) >= 1
except Exception as e:
    print(f"    FAIL: {e}")
    results["plants_api"] = False

# ── Test D: Frontend pages ────────────────────────────────────────
print("\n[6] Test D — Frontend Pages")
pages = {
    "/": "Home",
    "/predict": "Neural Scanner",
    "/plants": "Neural Botanical",
    "/symptom-search": "Symptom Search",
    "/about": "About"
}
frontend_ok = 0
for path, label in pages.items():
    try:
        r = requests.get(f"{FRONTEND}{path}", timeout=15)
        ok = r.status_code == 200
        old_build = "Group G9" in r.text or "AI physician" in r.text
        status_text = "OK" if ok and not old_build else ("STALE" if old_build else "FAIL")
        print(f"    {path:<20} [{status_text}] {r.status_code}")
        if ok and not old_build:
            frontend_ok += 1
    except Exception as e:
        print(f"    {path:<20} [ERR] {e}")
results["frontend"] = frontend_ok == len(pages)

# ── Final Score ───────────────────────────────────────────────────
print("\n" + "=" * 65)
print("FINAL AUDIT SUMMARY")
print("=" * 65)
checks = [
    ("Backend Health (synchronized)", results.get("health")),
    ("ML Model Loaded", results.get("version")),
    ("Leaf Prediction Working", results.get("leaf_predict")),
    ("Symptom Search Working", results.get("symptom_search")),
    ("Plants API Working", results.get("plants_api")),
    ("All Frontend Pages Clean", results.get("frontend")),
]
passed = sum(1 for _, v in checks if v is True)
total  = sum(1 for _, v in checks if v is not None and v != "SKIP")
for label, val in checks:
    icon = "PASS" if val is True else ("SKIP" if val == "SKIP" else "FAIL")
    print(f"  [{icon}] {label}")

score = round((passed / total) * 10, 1) if total > 0 else 0
print(f"\n  Score: {passed}/{total} checks passed -> {score}/10")
if score >= 9:
    print("  STATUS: PRODUCTION READY — DEMO CLEARED")
elif score >= 7:
    print("  STATUS: MOSTLY READY — Minor issues remain")
else:
    print("  STATUS: NEEDS ATTENTION — Check failures above")
print("=" * 65)
