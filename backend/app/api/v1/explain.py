"""
Explainability API Routes
Grad-CAM, LIME, and SHAP visualizations
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.explainability_service import get_explainability_service
from app.services.ml_service import get_ml_service

router = APIRouter()


@router.post("/gradcam")
async def generate_gradcam_visualization(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Generate Grad-CAM heatmap for uploaded image
    
    - **file**: Leaf image file
    - Returns: Grad-CAM visualization showing model attention
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_bytes = await file.read()
        
        # Get prediction first
        ml_service = get_ml_service()
        prediction_result = ml_service.predict(image_bytes)
        
        # Generate Grad-CAM
        explainability_service = get_explainability_service()
        gradcam_result = explainability_service.generate_gradcam(
            image_bytes, 
            prediction_result
        )
        
        return {
            "prediction": {
                "predicted_class": prediction_result["predicted_class"],
                "confidence": prediction_result["confidence"]
            },
            **gradcam_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grad-CAM generation failed: {str(e)}")


@router.post("/lime")
async def generate_lime_explanation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Generate LIME explanation for prediction
    
    - **file**: Leaf image file
    - Returns: LIME explanation with feature importance
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_bytes = await file.read()
        
        # Get prediction first
        ml_service = get_ml_service()
        prediction_result = ml_service.predict(image_bytes)
        
        # Generate LIME explanation
        explainability_service = get_explainability_service()
        lime_result = explainability_service.generate_lime_explanation(
            image_bytes,
            prediction_result
        )
        
        return {
            "prediction": {
                "predicted_class": prediction_result["predicted_class"],
                "confidence": prediction_result["confidence"]
            },
            **lime_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LIME explanation failed: {str(e)}")


@router.post("/combined")
async def generate_combined_explanation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Generate both Grad-CAM and LIME explanations
    
    - **file**: Leaf image file
    - Returns: Combined explanations
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_bytes = await file.read()
        
        # Get prediction
        ml_service = get_ml_service()
        prediction_result = ml_service.predict(image_bytes)
        
        # Generate both explanations
        explainability_service = get_explainability_service()
        gradcam_result = explainability_service.generate_gradcam(
            image_bytes,
            prediction_result
        )
        lime_result = explainability_service.generate_lime_explanation(
            image_bytes,
            prediction_result
        )
        
        return {
            "prediction": {
                "predicted_class": prediction_result["predicted_class"],
                "confidence": prediction_result["confidence"],
                "top_predictions": prediction_result["top_predictions"]
            },
            "gradcam": gradcam_result,
            "lime": lime_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combined explanation failed: {str(e)}")

