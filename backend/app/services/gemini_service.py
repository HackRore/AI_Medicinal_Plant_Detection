"""
Gemini Service
Google Gemini Vision API integration for natural language plant descriptions
"""

import os
import logging
from typing import Dict, Optional
from app.config import settings

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
                self.model = genai.GenerativeModel('gemini-pro')
                self.initialized = True
                logger.info("Gemini service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.initialized = False
        else:
            logger.warning("Gemini API key not configured. Using mock responses.")
    
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
