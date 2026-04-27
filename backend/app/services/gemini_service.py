import os
import json
import asyncio
import logging
import httpx
import base64
from typing import Optional, Dict
from app.utils.json_utils import safe_parse_gemini_json

logger = logging.getLogger(__name__)

class GeminiService:
    """Bulletproof REST-based AI Service for Botanical Reasoning and Symptom Analysis."""
    
    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

    def _get_api_key(self) -> str:
        return os.environ.get("GEMINI_API_KEY", "")

    async def _call_rest_api(self, payload: Dict) -> str:
        """Execute a direct REST call to Gemini bypasses library conflicts."""
        api_key = self._get_api_key()
        if not api_key:
            logger.error("Gemini API Key missing")
            return ""
        
        url = f"{self.base_url}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=20.0)
                if response.status_code != 200:
                    logger.error(f"Gemini REST Error {response.status_code}: {response.text}")
                    return ""
                
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Gemini Connection Failed: {e}")
            return ""

    async def get_plant_analysis(self, plant_name: str, confidence: float, image_bytes: Optional[bytes] = None) -> Dict:
        """Get sophisticated Ayurvedic analysis for identified specimens."""
        prompt = f"""You are a senior Ayurvedic Doctor (Vaidya). 
Identification: {plant_name} (Confidence: {confidence*100:.1f}%)

Provide a wise, authoritative analysis in JSON.
{{
  "confirmed_name": "{plant_name}",
  "scientific_name": "...",
  "ayurvedic_name": "...",
  "medicinal_uses": "Empathetic explanation",
  "preparation": "How to prepare",
  "dosage": "Standard dosage",
  "toxicity": "Safety info",
  "vision_note": "Scientific verdict."
}}"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        if image_bytes:
            # For simplicity in REST, we stick to text for now unless vision is critical
            # Vision requires inline_data base64
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            payload["contents"][0]["parts"].insert(0, {
                "inlineData": {"mimeType": "image/jpeg", "data": b64_img}
            })

        raw = await self._call_rest_api(payload)
        return safe_parse_gemini_json(raw) or {"error": "AI Insight Offline"}

    async def get_symptom_recommendations(self, symptoms: str) -> Dict:
        """Analyze natural language symptoms and recommend 3 Ayurvedic remedies."""
        prompt = f"""You are a wise Ayurvedic Physician (Vaidya). 
Patient description: "{symptoms}"

Understand the symptoms informally and provide an empathetic JSON response.
{{
  "doctor_note": "A warm opening address.",
  "diagnosis": "Dosha (Vata/Pitta/Kapha) perspective.",
  "recommendations": [
    {{
      "plant": "Name",
      "why": "Why this helps them specifically",
      "preparation": "Instructions",
      "safety": "Warnings"
    }}
  ],
  "lifestyle_advice": "Holistic tip",
  "warning": "Medical disclaimer"
}}"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        raw = await self._call_rest_api(payload)
        return safe_parse_gemini_json(raw) or {"error": "The Doctor is currently offline."}

gemini_service = GeminiService()
def get_gemini_service(): return gemini_service
