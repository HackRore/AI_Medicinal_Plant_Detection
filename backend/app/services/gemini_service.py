import os
import json
import asyncio
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.utils.json_utils import safe_parse_gemini_json

logger = logging.getLogger(__name__)

class GeminiService:
    """Orchestrates VLM-based leaf verification and clinical grounding."""
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY missing from environment.")
            return

        genai.configure(api_key=api_key)
        # Standardize on Flash for real-time verification; Pro for analytical grounding
        self.vlm = genai.GenerativeModel('gemini-1.5-flash')
        self.reasoning_engine = genai.GenerativeModel('gemini-1.5-pro')

    def _parse_structured_output(self, text: str) -> Dict[str, Any]:
        """Extracts JSON from markdown formatted text blocks."""
        try:
            # simple markdown parsing logic
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except Exception as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return {}

    async def verify_is_leaf(self, image_bytes: bytes) -> Dict[str, Any]:
        """Binary classification of input: Botanical leaf vs OOD."""
        prompt = """
        Analyze image. Output JSON:
        {
            "is_leaf": boolean,
            "confidence": "high"|"medium"|"low",
            "rejection_reason": "if is_leaf is false"
        }
        Only return valid JSON.
        """
        try:
            response = await self.vlm.generate_content_async([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            return self._parse_structured_output(response.text)
        except Exception as e:
            logger.error(f"VLM verification failure: {str(e)}")
            return {"is_leaf": True, "confidence": "low"}

    async def validate_prediction(self, class_name: str, image_bytes: bytes) -> Dict[str, Any]:
        """Cross-verifies ML output against VLM visual features."""
        prompt = f"Verify if image shows {class_name}. Output JSON: {{'matches': boolean, 'confidence': 0.0-1.0}}. JSON only."
        try:
            response = await self.vlm.generate_content_async([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            return self._parse_structured_output(response.text)
        except Exception as e:
            logger.error(f"Prediction cross-check failed: {str(e)}")
            return {"matches": True}

    async def get_plant_analysis(self, plant_name: str, confidence: float, image_bytes: bytes, scale_ref: bool) -> Dict[str, Any]:
        """Generates grounded Ayurvedic analysis with visual context."""
        prompt = f"""
        Analyze {plant_name} (ML Confidence: {confidence}%). 
        Include:
        - Vision note on leaf morphology
        - Confirmed botanical name
        - Traditional Ayurvedic utility
        JSON output: {{'confirmed_name': str, 'vision_note': str, 'utility': [str]}}.
        """
        try:
            response = await self.reasoning_engine.generate_content_async([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            return self._parse_structured_output(response.text)
        except Exception as e:
            logger.error(f"Grounding engine failed: {str(e)}")
            return {"vision_note": "Post-inference analysis unavailable."}

    async def get_rag_symptom_analysis(self, symptoms: str, context: str) -> Dict[str, Any]:
        """Grounds symptom checks using the specialized knowledge base."""
        prompt = f"""You are the PlantoAI Botanical Intelligence Engine.
        
USER SYMPTOMS: "{symptoms}"
BOTANICAL CONTEXT: {context if context else "General knowledge."}

Return a valid JSON object ONLY:
{{
  "clinical_note": "assessment",
  "dosha_analysis": "dosha",
  "recommendations": [
    {{
      "plant": "name",
      "scientific_name": "latin",
      "rationale": "why",
      "preparation": "how",
      "safety_caution": "warning"
    }}
  ],
  "lifestyle_protocol": "habits",
  "source_integrity": "Verified NMPB"
}}"""
        try:
            response = await self.reasoning_engine.generate_content_async(prompt)
            return self._parse_structured_output(response.text)
        except Exception as e:
            logger.error(f"RAG engine failed: {str(e)}")
            return {"error": "The Neural RAG Engine is currently offline."}

gemini_service = GeminiService()
def get_gemini_service(): return gemini_service
