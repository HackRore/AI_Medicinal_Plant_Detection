import os
import logging
import re
import json
import asyncio
from typing import Dict, Optional, Any
from app.config import settings
import hashlib
from app.database import SessionLocal
from app.models.cache import GeminiCache

logger = logging.getLogger(__name__)

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not available. Install with: pip install google-generativeai")


class GeminiService:
    """Service for Gemini Vision API interactions"""
    
    def __init__(self):
        self.initialized = False
        self.model = None
        
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.initialized = True
                logger.info("Gemini service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.initialized = False
        else:
            logger.warning("Gemini API key not configured. Using mock responses.")

    def safe_parse_gemini(self, text: str) -> dict:
        """Never crashes. Handles markdown fences, partial JSON, extra text."""
        if not text:
            return {}
        # Strip markdown fences
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
        # Try direct parse
        try:
            return json.loads(cleaned)
        except Exception:
            pass
        # Extract first JSON object from anywhere in the text
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        # Safe fallback — never crash
        return {"gemini_note": "AI enrichment unavailable", "raw_preview": text[:100]}

    async def _call_gemini_api(self, image_bytes: bytes, plant_name: str = None, confidence: float = None) -> str:
        """Internal method to perform the actual SDK call"""
        if not self.initialized:
            return "{}"

        image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
        
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
            CRITICAL: Always return valid JSON even if uncertain. Never return plain text. Never wrap in markdown.
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
            CRITICAL: Always return valid JSON even if uncertain. Never return plain text. Never wrap in markdown.
            """

        response = self.model.generate_content([prompt, image_parts[0]])
        return response.text

    async def get_gemini_analysis(self, image_bytes: bytes, plant_name: str, confidence: float) -> dict:
        """Public method for plant enrichment with 12s timeout"""
        try:
            raw = await asyncio.wait_for(
                self._call_gemini_api(image_bytes, plant_name, confidence),
                timeout=12.0
            )
            return self.safe_parse_gemini(raw)
        except asyncio.TimeoutError:
            return {"gemini_note": "Expert AI timed out — showing model result only"}
        except Exception as e:
            return {"gemini_note": f"AI enrichment error: {str(e)[:60]}"}

    async def identify_plant_from_image(
        self, 
        image_bytes: bytes,
        language: str = "en"
    ) -> Dict:
        """
        Identify medicinal plant directly from image using Gemini Vision
        
        Args:
            image_bytes: Raw image bytes
            language: Language code
            
        Returns:
            Dictionary with identification result
        """
        if not self.initialized:
            return {
                "identified": False,
                "error": "Gemini not initialized",
                "source": "Gemini AI"
            }
        
        try:
            # --- CACHE CHECK: Identify by image hash ---
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

            # Prepare image for Gemini
            raw_response = await asyncio.wait_for(
                self._call_gemini_api(image_bytes),
                timeout=12.0
            )
            
            # Use robust parsing
            parsed_result = self.safe_parse_gemini(raw_response)
            
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

    def get_plant_description(
        self, 
        plant_name: str, 
        language: str = "en"
    ) -> Dict:
        """
        Get natural language description of a plant
        
        Args:
            plant_name: Scientific or common name of the plant
            language: Language code (en, hi, ta, te, bn)
            
        Returns:
            Dictionary with plant description
        """
        if not self.initialized:
            return self._get_mock_description(plant_name, language)
        
        try:
            # Create prompt based on language
            prompts = {
                "en": f"Provide a detailed description of the medicinal plant '{plant_name}'. Include its appearance, medicinal properties, traditional uses, and any precautions. Keep it concise (3-4 paragraphs).",
                "hi": f"औषधीय पौधे '{plant_name}' का विस्तृत विवरण प्रदान करें। इसकी उपस्थिति, औषधीय गुण, पारंपरिक उपयोग और सावधानियां शामिल करें।",
                "ta": f"மருத்துவ தாவரம் '{plant_name}' பற்றிய விரிவான விளக்கத்தை வழங்கவும். அதன் தோற்றம், மருத்துவ பண்புகள், பாரம்பரிய பயன்பாடுகள் மற்றும் எச்சரிக்கைகளை சேர்க்கவும்.",
                "te": f"ఔషధ మొక్క '{plant_name}' గురించి వివరణాత్మక వివరణ అందించండి. దాని రూపం, ఔషధ లక్షణాలు, సాంప్రదాయ ఉపయోగాలు మరియు జాగ్రత్తలు చేర్చండి.",
                "bn": f"ঔষধি উদ্ভিদ '{plant_name}' এর বিস্তারিত বর্ণনা প্রদান করুন। এর চেহারা, ঔষধি গুণাবলী, ঐতিহ্যবাহী ব্যবহার এবং সতর্কতা অন্তর্ভুক্ত করুন।"
            }
            
            prompt = prompts.get(language, prompts["en"])
            
            response = self.model.generate_content(prompt)
            
            return {
                "description": response.text,
                "language": language,
                "source": "Gemini AI",
                "plant_name": plant_name
            }
            
        except Exception as e:
            logger.error(f"Error getting Gemini description: {e}")
            return self._get_mock_description(plant_name, language)
    
    def chat_about_plant(
        self, 
        plant_name: str, 
        question: str,
        language: str = "en"
    ) -> Dict:
        """
        Interactive chat about a specific plant
        
        Args:
            plant_name: Name of the plant
            question: User's question
            language: Language code
            
        Returns:
            Dictionary with answer
        """
        if not self.initialized:
            return self._get_mock_chat_response(plant_name, question, language)
        
        try:
            prompt = f"You are an expert in medicinal plants. Answer this question about {plant_name}: {question}"
            
            if language != "en":
                prompt += f" Please respond in {self._get_language_name(language)}."
            
            response = self.model.generate_content(prompt)
            
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
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali"
        }
        return languages.get(code, "English")
    
    def _get_mock_description(self, plant_name: str, language: str) -> Dict:
        """Generate mock description when Gemini is not available"""
        descriptions = {
            "en": f"{plant_name} is a medicinal plant with significant therapeutic properties. It has been used in traditional medicine for centuries to treat various ailments. The plant contains bioactive compounds that contribute to its medicinal effects. Common uses include treating digestive issues, skin conditions, and boosting immunity. Always consult a healthcare professional before use.",
            "hi": f"{plant_name} एक औषधीय पौधा है जिसमें महत्वपूर्ण चिकित्सीय गुण हैं। इसका उपयोग सदियों से पारंपरिक चिकित्सा में विभिन्न बीमारियों के इलाज के लिए किया जाता रहा है।",
            "ta": f"{plant_name} குறிப்பிடத்தக்க சிகிச்சை பண்புகளைக் கொண்ட ஒரு மருத்துவ தாவரம். பல்வேறு நோய்களுக்கு சிகிச்சையளிக்க பாரம்பரிய மருத்துவத்தில் பல நூற்றாண்டுகளாக இது பயன்படுத்தப்படுகிறது.",
            "te": f"{plant_name} ముఖ్యమైన చికిత్సా లక్షణాలతో కూడిన ఔషధ మొక్క. వివిధ వ్యాధులకు చికిత్స చేయడానికి శతాబ్దాలుగా సాంప్రదాయ వైద్యంలో ఇది ఉపయోగించబడుతోంది.",
            "bn": f"{plant_name} একটি ঔষধি উদ্ভিদ যার উল্লেখযোগ্য চিকিৎসা বৈশিষ্ট্য রয়েছে। বিভিন্ন রোগের চিকিৎসার জন্য শতাব্দী ধরে ঐতিহ্যবাহী চিকিৎসায় এটি ব্যবহৃত হয়ে আসছে।"
        }
        
        return {
            "description": descriptions.get(language, descriptions["en"]),
            "language": language,
            "source": "Mock Data (Gemini not configured)",
            "plant_name": plant_name
        }
    
    def _get_mock_chat_response(
        self, 
        plant_name: str, 
        question: str, 
        language: str
    ) -> Dict:
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
