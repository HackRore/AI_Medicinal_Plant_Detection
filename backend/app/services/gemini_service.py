import os
import logging
import re
import json
import asyncio
import hashlib
from typing import Dict, Optional, Any
from app.config import settings
from app.database import SessionLocal
from app.models.cache import GeminiCache

logger = logging.getLogger(__name__)

# Try to import Gemini SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google GenAI SDK not available. Install with: pip install google-genai")


class GeminiService:
    """Service for Gemini API interactions using the modern google-genai SDK"""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.model_id = "gemini-2.0-flash"
        
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.initialized = True
                logger.info("Gemini service (google-genai) initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.initialized = False
        else:
            logger.warning("Gemini API key not configured. Using mock responses.")

    def safe_parse_gemini(self, text: str) -> dict:
        if not text:
            return {}
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"gemini_note": "AI enrichment unavailable", "raw_preview": text[:100]}

    async def _call_gemini_api(self, image_bytes: bytes, plant_name: str = None, confidence: float = None) -> str:
        """Internal method to perform the actual SDK call"""
        if not self.initialized:
            return "{}"

        if plant_name:
            prompt = f"""
            You are a master botanist. I have identified this plant as '{plant_name}' with {confidence*100:.1f}% confidence.
            Verify this identification. If correct, provide medicinal details. If incorrect, suggest the right plant.
            
            Return ONLY a JSON object with:
            {{
                "verified_name": "string",
                "is_correct": boolean,
                "medicinal_properties": ["prop1", "prop2", "prop3"],
                "confidence_of_expert": "0-100%",
                "safety_notes": "string"
            }}
            CRITICAL: Return ONLY raw JSON. No markdown. No backticks. No explanation. If uncertain, still return JSON with your best assessment.
            """
        else:
            prompt = """
            You are a master botanist and Ayurvedic/Medicinal plant expert. 
            Analyze this leaf/plant image and:
            1. Identify the common and scientific name.
            2. List 3 key medicinal properties.
            3. Provide a 'Confidence Score' from 0-100%.
            4. State if it is safe for common use.
            
            Return ONLY a valid JSON object.
            CRITICAL: Return ONLY raw JSON. No markdown. No backticks. No explanation. If uncertain, still return JSON with your best assessment.
            """

        try:
            # Use asyncio.to_thread because the genai client is synchronous
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    prompt
                ]
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return "{}"

    async def generate_text(self, prompt: str, model_id: str = None) -> str:
        """Generic text generation"""
        if not self.initialized:
            return ""
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_id or self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            return ""

    async def get_ai_debate(self, image_bytes: bytes, cnn_prediction: str, cnn_confidence: float) -> dict:
        """
        Independent verification for AI Debate System (CNN vs Gemini)
        """
        if not self.initialized:
            return {
                "cnn_prediction": cnn_prediction,
                "cnn_confidence": round(cnn_confidence * 100, 1),
                "gemini_prediction": "Expert AI Offline",
                "agreement": True,
                "explanation": "Expert verification skip: service not initialized."
            }

        prompt = f"""
        You are an independent botanical auditor.
        I (the CNN model) have identified this plant as '{cnn_prediction}' with {cnn_confidence*100:.1f}% confidence.
        
        Analyze the image independently and decide if you agree.
        
        Return ONLY a JSON object:
        {{
            "cnn_prediction": "{cnn_prediction}",
            "cnn_confidence": {round(cnn_confidence * 100, 1)},
            "gemini_prediction": "Common Name",
            "agreement": boolean,
            "explanation": "1-2 sentence technical reason for agreement or disagreement based on leaf morphology."
        }}
        CRITICAL: Return ONLY raw JSON. No markdown.
        """
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_id,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                        prompt
                    ]
                ),
                timeout=12.0
            )
            return self.safe_parse_gemini(response.text)
        except Exception as e:
            logger.error(f"AI Debate logic failure: {e}")
            return {
                "cnn_prediction": cnn_prediction,
                "cnn_confidence": round(cnn_confidence * 100, 1),
                "gemini_prediction": "Analysis Error",
                "agreement": True,
                "explanation": f"Expert audit failed to provide a timely response: {str(e)[:40]}"
            }

    async def get_gemini_analysis_safe(self, image_bytes: bytes, plant_name: str, confidence: float) -> dict:
        try:
            raw = await asyncio.wait_for(
                self._call_gemini_api(image_bytes, plant_name, confidence),
                timeout=12.0
            )
            return self.safe_parse_gemini(raw)
        except asyncio.TimeoutError:
            return {"gemini_note": "Expert AI timed out — showing model result only"}
        except Exception as e:
            return {"gemini_note": f"AI enrichment unavailable: {str(e)[:60]}"}

    async def identify_plant_from_image(
        self, 
        image_bytes: bytes,
        language: str = "en"
    ) -> Dict:
        """
        Identify medicinal plant directly from image using Gemini Vision
        """
        if not self.initialized:
            return {
                "identified": False,
                "error": "Gemini not initialized",
                "source": "Gemini AI"
            }
        
        try:
            # --- CACHE CHECK ---
            image_hash = hashlib.sha256(image_bytes).hexdigest()
            db = SessionLocal()
            try:
                cached = db.query(GeminiCache).filter(GeminiCache.image_hash == image_hash).first()
                if cached:
                    logger.info(f"🚀 Cache Hit: Gemini result for hash {image_hash[:10]}...")
                    return {
                        **cached.response_json,
                        "source": "Gemini AI (Cached)",
                        "status": "success"
                    }
            finally:
                db.close()

            parsed_result = await self.get_gemini_analysis_safe(image_bytes, None, 0.0)
            
            result = {
                "identification_details": parsed_result,
                "language": language,
                "source": "Gemini AI Expert",
                "status": "success"
            }

            # --- STORE IN CACHE ---
            db = SessionLocal()
            try:
                new_cache = GeminiCache(
                    image_hash=image_hash,
                    response_json=result
                )
                db.add(new_cache)
                db.commit()
                logger.info(f"💾 Cache Store: Saved Gemini result for hash {image_hash[:10]}...")
            except Exception as cache_err:
                logger.warning(f"Failed to store Gemini cache: {cache_err}")
                db.rollback()
            finally:
                db.close()

            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini identification: {e}")
            return {
                "identified": False,
                "error": str(e),
                "source": "Gemini AI"
            }

    async def get_plant_description(
        self, 
        plant_name: str, 
        language: str = "en"
    ) -> Dict:
        """
        Get natural language description of a plant
        """
        if not self.initialized:
            return self._get_mock_description(plant_name, language)
        
        try:
            prompts = {
                "en": f"Provide a detailed description of the medicinal plant '{plant_name}'. Include its appearance, medicinal properties, traditional uses, and any precautions. Keep it concise (3-4 paragraphs).",
                "hi": f"औषधीय पौधे '{plant_name}' का विस्तृत विवरण प्रदान करें। इसकी उपस्थिति, औषधीय गुण, पारंपरिक उपयोग और सावधानियां शामिल करें।",
                "ta": f"மருத்துவ தாவரம் '{plant_name}' பற்றிய விரிவான விளக்கத்தை வழங்கவும். அதன் தோற்றம், மருத்துவ பண்புகள், பாரம்பரிய பயன்பாடுகள் மற்றும் எச்சரிக்கைகளை சேர்க்கவும்.",
                "te": f"ఔషధ మొక్క '{plant_name}' గురించి వివరణాత్మక వివరణ అందించండి. దాని రూపం, ఔషధ లక్షణాలు, సాంప్రదాయ ఉపయోగాలు మరియు జాగ్రత్తలు చేర్చండి.",
                "bn": f"ঔষধি উদ্ভিদ '{plant_name}' এর বিস্তারিত বর্ণনা প্রদান করুন। এর চেহারা, ঔষধি গুণাবলী, ঐতিহ্যবাহী ব্যবহার এবং সতর্কতা অন্তর্ভুক্ত করুন।"
            }
            
            prompt = prompts.get(language, prompts["en"])
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt
            )
            
            return {
                "description": response.text,
                "language": language,
                "source": "Gemini AI",
                "plant_name": plant_name
            }
            
        except Exception as e:
            logger.error(f"Error getting Gemini description: {e}")
            return self._get_mock_description(plant_name, language)
    
    async def chat_about_plant(
        self, 
        plant_name: str, 
        question: str,
        language: str = "en"
    ) -> Dict:
        """
        Interactive chat about a specific plant
        """
        if not self.initialized:
            return self._get_mock_chat_response(plant_name, question, language)
        
        try:
            prompt = f"You are an expert in medicinal plants. Answer this question about {plant_name}: {question}"
            
            if language != "en":
                prompt += f" Please respond in {self._get_language_name(language)}."
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt
            )
            
            return {
                "answer": response.text,
                "plant_name": plant_name,
                "question": question,
                "language": language,
                "source": "Gemini AI"
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return self._get_mock_chat_response(plant_name, question, language)
    
    def _get_language_name(self, code: str) -> str:
        """Get full language name from code"""
        languages = {
            "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali"
        }
        return languages.get(code, "English")
    
    def _get_mock_description(self, plant_name: str, language: str) -> Dict:
        """Generate mock description when Gemini is not available"""
        descriptions = {
            "en": f"{plant_name} is a medicinal plant with significant therapeutic properties. It has been used in traditional medicine for centuries to treat various ailments.",
            "hi": f"{plant_name} एक औषधीय पौधा है जिसमें महत्वपूर्ण चिकित्सीय गुण हैं।",
            "ta": f"{plant_name} குறிப்பிடத்தக்க சிகிச்சை பண்புகளைக் கொண்ட ஒரு மருத்துவ தாவரம்.",
            "te": f"{plant_name} ముఖ్యమైన చికిత్సా లక్షణాలతో కూడిన ఔషధ మొక్క.",
            "bn": f"{plant_name} একটি ঔষধি উদ্ভিদ যার উল্লেখযোগ্য চিকিৎসা বৈশিষ্ট্য রয়েছে।"
        }
        
        return {
            "description": descriptions.get(language, descriptions["en"]),
            "language": language,
            "source": "Mock Data (Gemini not configured)",
            "plant_name": plant_name
        }
    
    def _get_mock_chat_response(self, plant_name: str, question: str, language: str) -> Dict:
        """Generate mock chat response"""
        return {
            "answer": f"This is a mock response about {plant_name}. To get real AI-powered answers, please configure the Gemini API key in your environment settings.",
            "plant_name": plant_name,
            "question": question,
            "language": language,
            "source": "Mock Data (Gemini not configured)"
        }


# Global instance
gemini_service = GeminiService()


def get_gemini_service() -> GeminiService:
    """Get Gemini service instance"""
    return gemini_service


async def get_plant_analysis(plant_name: str, confidence: float, image_bytes: bytes) -> Dict:
    """Compatibility wrapper for predict.py"""
    service = get_gemini_service()
    result = await service.get_gemini_analysis_safe(image_bytes, plant_name, confidence)
    return result
