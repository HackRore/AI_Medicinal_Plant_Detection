"""
Quality Check API Routes
Image quality validation before ML inference
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict
import logging

from ml_pipeline.models.quality_gatekeeper import quality_check

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def check_image_quality(
    file: UploadFile = File(...)
) -> Dict:
    """
    Check image quality before sending to ML model
    
    Validates:
    - Blur/sharpness (Laplacian variance)
    - Brightness levels
    - Image composition (object size/position)
    
    Args:
        file: Image file (JPEG/PNG)
        
    Returns:
        Quality assessment with:
        - is_valid: bool (passed all checks)
        - scores: Dict of quality metrics
        - reasons: List of issues (if any)
        - recommendations: List of improvements
        - image_shape: Image dimensions
        - image_size_mb: File size in MB
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Perform quality check
        quality_result = quality_check(image_bytes, strict=False)
        
        # Add file metadata
        quality_result["filename"] = file.filename
        quality_result["content_type"] = file.content_type
        
        return quality_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality check error: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking image quality: {str(e)}")


@router.post("/strict")
async def check_image_quality_strict(
    file: UploadFile = File(...)
) -> Dict:
    """
    Strict quality check with higher thresholds
    
    More restrictive for production use
    """
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_bytes = await file.read()
        quality_result = quality_check(image_bytes, strict=True)
        
        quality_result["filename"] = file.filename
        quality_result["content_type"] = file.content_type
        quality_result["mode"] = "strict"
        
        return quality_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strict quality check error: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking image quality: {str(e)}")
