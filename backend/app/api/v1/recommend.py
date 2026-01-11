"""
Recommendation API Routes
Plant recommendations based on various criteria
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.recommendation_service import get_recommendation_service

router = APIRouter()


@router.get("/similar/{plant_id}")
async def get_similar_plants(
    plant_id: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get plants similar to the specified plant based on medicinal properties
    
    - **plant_id**: Plant ID
    - **limit**: Number of recommendations
    """
    try:
        recommendation_service = get_recommendation_service()
        recommendations = recommendation_service.get_similar_plants(
            plant_id=plant_id,
            db=db,
            limit=limit
        )
        
        return {
            "plant_id": plant_id,
            "count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/ailment")
async def get_plants_for_ailment(
    ailment: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """
    Get plants that can treat a specific ailment
    
    - **ailment**: Ailment or condition
    """
    try:
        recommendation_service = get_recommendation_service()
        plants = recommendation_service.get_plants_for_ailment(
            ailment=ailment,
            db=db,
            limit=10
        )
        
        return {
            "ailment": ailment,
            "count": len(plants),
            "plants": plants
        }
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get plants for ailment: {str(e)}")


@router.get("/location")
async def get_location_based_recommendations(
    lat: float,
    lng: float,
    db: Session = Depends(get_db)
):
    """
    Get plant recommendations based on geographic location
    
    - **lat**: Latitude
    - **lng**: Longitude
    """
    try:
        recommendation_service = get_recommendation_service()
        recommendations = recommendation_service.get_geolocation_recommendations(
            latitude=lat,
            longitude=lng,
            db=db,
            limit=10
        )
        
        return {
            "location": {"lat": lat, "lng": lng},
            "count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get location-based recommendations: {str(e)}")
