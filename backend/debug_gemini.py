import asyncio
import os
from app.services.gemini_service import gemini_service
from dotenv import load_dotenv

# Force load .env
load_dotenv()

async def test_gemini():
    print(f"API KEY: {os.environ.get('GEMINI_API_KEY', 'MISSING')[:10]}...")
    symptoms = "cough and fever"
    context = "PLANT: Tulsi\nAYURVEDIC USES: Cough, fever, immunity"
    print("\n[TEST] Gemini Direct RAG Call...")
    result = await gemini_service.get_rag_symptom_analysis(symptoms, context)
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_gemini())
