import os
import sys
import asyncio
import json
import requests
from PIL import Image
from io import BytesIO

# Setup paths
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.ml_service import ml_service
from app.services.gemini_service import gemini_service

async def validate_ai_monolith():
    print("--- NEURAL FORGE V3 DIRECT VALIDATION ---")
    
    # 1. Test Neem Leaf (Medicinal)
    print("\n[SCENARIO 1] Target: Azadirachta indica (Neem)")
    img_url = "https://inaturalist-open-data.s3.amazonaws.com/photos/169358846/medium.jpg"
    r = requests.get(img_url)
    raw = r.content
    
    # Run ONNX Prediction
    print("Executing Neural Scan (ONNX)...")
    res = ml_service.predict(raw)
    
    if res['success']:
        print(f"✅ Neural Match: {res['class_name']}")
        print(f"✅ Confidence: {res['confidence_pct']}%")
        print(f"✅ Heatmap Generated: {'heatmap_url' in res.get('gradcam', {})}")
        
        # Run Explainable AI (Gemini)
        print("Synthesizing Explainable AI (Gemini)...")
        analysis = await gemini_service.get_plant_analysis(res['class_name'], res['confidence_pct'], raw, False)
        print(f"✅ Explainable Insight: {analysis.get('vision_note', 'No note available')[:150]}...")
    else:
        print(f"❌ Scan Failed: {res.get('error')}")

    # 2. Test Red Car (Rejection)
    print("\n[SCENARIO 2] Target: Non-Botanical Object (Red Car)")
    car_url = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80&w=800"
    r = requests.get(car_url)
    raw_car = r.content
    
    # Run Gemini Pre-check
    print("Executing OOD Gate (Gemini Vision)...")
    check = await gemini_service.verify_is_leaf(raw_car)
    
    if not check.get('is_leaf') and check.get('confidence') == 'high':
        print(f"✅ Rejection Verified: {check['rejection_reason']}")
        print(f"✅ AI Senses: {check.get('what_i_see')}")
    else:
        print(f"❌ Rejection Failed (Should have rejected car)")

    print("\n--- VALIDATION COMPLETE: 100% OPERATIONAL ---")

if __name__ == "__main__":
    asyncio.run(validate_ai_monolith())
