"""
Gemini Vision API Routes
Integration with Google Gemini for natural language descriptions
"""

from fastapi import APIRouter, File, UploadFile, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.gemini_service import get_gemini_service
from app.models.plant import Plant

router = APIRouter()


@router.post("/describe")
async def describe_plant_image(
    file: UploadFile = File(...),
    language: str = "en",
    db: Session = Depends(get_db)
):
    """
    Generate natural language description of plant using Gemini Vision
    
    - **file**: Leaf image file
    - **language**: Target language (en, hi, ta, te, bn)
    """
    try:
        from fastapi import HTTPException
        from app.services.ml_service import get_ml_service
        
        ml_service = get_ml_service()
        gemini_service = get_gemini_service()
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Use ML model to identify the plant first
        prediction = ml_service.predict(image_bytes)
        plant_name = prediction["predicted_class"]
        
        # Now get botanical description for THIS specific plant
        description = gemini_service.get_plant_description(
            plant_name=plant_name,
            language=language
        )
        
        return description
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")


@router.post("/chat")
async def chat_about_plant(
    plant_id: int,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Ask questions about a plant using Gemini
    
    - **plant_id**: Plant ID
    - **question**: User question
    """
    try:
        from fastapi import HTTPException
        
        # Get plant information
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        gemini_service = get_gemini_service()
        response = gemini_service.chat_about_plant(
            plant_name=plant.species_name,
            question=question,
            language="en"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/translate")
async def translate_plant_info(
    text: str = Body(..., embed=True),
    target_language: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Translate plant information to regional language
    
    - **text**: Text to translate
    - **target_language**: Target language code (hi, ta, te, bn)
    """
    try:
        from fastapi import HTTPException
        
        gemini_service = get_gemini_service()
        
        # Use Gemini to translate
        # For now, return a simple response
        return {
            "original_text": text,
            "translated_text": f"[Translation to {target_language}]: {text}",
            "target_language": target_language,
            "note": "Translation feature requires Gemini API configuration"
        }
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
