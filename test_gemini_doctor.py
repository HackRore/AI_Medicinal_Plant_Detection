import asyncio
import os
from app.services.gemini_service import gemini_service
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def test_doctor():
    print("🩺 Testing Ayurvedic Doctor Intelligence v2.0...")
    symptoms = "I have a high fever and my throat is very sore."
    
    # Verify the new key
    res = await gemini_service.get_symptom_recommendations(symptoms)
    
    if "error" in res:
        print(f"❌ Handshake Failed: {res['error']}")
    else:
        print("✅ Handshake Successful!")
        print("-" * 30)
        print(f"🏥 Doctor's Note: {res.get('doctor_note')}")
        print(f"⚖️ Diagnosis: {res.get('diagnosis')}")
        print(f"🌿 Recommendation: {res['recommendations'][0]['plant']} - {res['recommendations'][0]['why']}")
        print(f"🥗 Lifestyle Tip: {res['lifestyle_advice']}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_doctor())
