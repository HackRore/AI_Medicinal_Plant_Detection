"""
Recommendation Service
Content-based filtering for plant recommendations
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models.plant import Plant, MedicinalProperty

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating plant recommendations"""
    
    def __init__(self):
        self.vectorizer = None
        self.plant_vectors = None
        self.plant_ids = []
    
    def get_similar_plants(
        self,
        plant_id: int,
        db: Session,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get plants similar to the given plant based on medicinal properties
        
        Args:
            plant_id: ID of the reference plant
            db: Database session
            limit: Maximum number of recommendations
            
        Returns:
            List of similar plants with similarity scores
        """
        try:
            # Get the reference plant
            reference_plant = db.query(Plant).filter(Plant.id == plant_id).first()
            if not reference_plant:
                return []
            
            # Get all plants with their medicinal properties
            plants = db.query(Plant).all()
            
            if len(plants) < 2:
                return []
            
            # Build feature vectors
            plant_features = []
            plant_data = []
            
            for plant in plants:
                # Combine medicinal properties into a text feature
                properties = db.query(MedicinalProperty).filter(
                    MedicinalProperty.plant_id == plant.id
                ).all()
                
                feature_text = " ".join([
                    f"{prop.ailment} {prop.usage_description or ''}"
                    for prop in properties
                ])
                
                if not feature_text.strip():
                    feature_text = plant.description or plant.species_name
                
                plant_features.append(feature_text)
                plant_data.append({
                    "id": plant.id,
                    "species_name": plant.species_name,
                    "common_name": plant.common_name_en,
                    "description": plant.description
                })
            
            # Calculate TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(plant_features)
            
            # Find the reference plant index
            ref_idx = next(
                (i for i, p in enumerate(plant_data) if p["id"] == plant_id),
                None
            )
            
            if ref_idx is None:
                return []
            
            # Calculate cosine similarity
            similarities = cosine_similarity(
                tfidf_matrix[ref_idx:ref_idx+1],
                tfidf_matrix
            )[0]
            
            # Get top similar plants (excluding the reference plant itself)
            similar_indices = np.argsort(similarities)[::-1]
            similar_indices = [i for i in similar_indices if i != ref_idx][:limit]
            
            recommendations = []
            for idx in similar_indices:
                recommendations.append({
                    **plant_data[idx],
                    "similarity_score": float(similarities[idx]),
                    "reason": "Similar medicinal properties"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting similar plants: {e}")
            return []
    
    def get_plants_for_ailment(
        self,
        ailment: str,
        db: Session,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get plants that can treat a specific ailment
        
        Args:
            ailment: The ailment/condition to search for
            db: Database session
            limit: Maximum number of results
            
        Returns:
            List of plants that can treat the ailment
        """
        try:
            # Search for medicinal properties matching the ailment
            properties = db.query(MedicinalProperty).filter(
                MedicinalProperty.ailment.ilike(f"%{ailment}%")
            ).limit(limit).all()
            
            results = []
            seen_plant_ids = set()
            
            for prop in properties:
                if prop.plant_id in seen_plant_ids:
                    continue
                
                plant = db.query(Plant).filter(Plant.id == prop.plant_id).first()
                if plant:
                    results.append({
                        "id": plant.id,
                        "species_name": plant.species_name,
                        "common_name": plant.common_name_en,
                        "ailment": prop.ailment,
                        "usage": prop.usage_description,
                        "preparation": prop.preparation_method,
                        "dosage": prop.dosage,
                        "precautions": prop.precautions,
                        "efficacy_rating": prop.efficacy_rating
                    })
                    seen_plant_ids.add(prop.plant_id)
            
            # Sort by efficacy rating if available
            results.sort(
                key=lambda x: x.get("efficacy_rating", 0) or 0,
                reverse=True
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting plants for ailment: {e}")
            return []
    
    def get_geolocation_recommendations(
        self,
        latitude: float,
        longitude: float,
        db: Session,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get plant recommendations based on user's location
        (Currently returns all plants, can be enhanced with regional data)
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            db: Database session
            limit: Maximum number of results
            
        Returns:
            List of regionally relevant plants
        """
        try:
            # For now, return popular plants
            # In production, this would filter by regional availability
            plants = db.query(Plant).limit(limit).all()
            
            results = []
            for plant in plants:
                results.append({
                    "id": plant.id,
                    "species_name": plant.species_name,
                    "common_name": plant.common_name_en,
                    "description": plant.description,
                    "regional_note": "Commonly found in this region"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting geolocation recommendations: {e}")
            return []


# Global instance
recommendation_service = RecommendationService()


def get_recommendation_service() -> RecommendationService:
    """Get recommendation service instance"""
    return recommendation_service
