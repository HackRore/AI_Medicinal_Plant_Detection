import os
import logging
from supabase import create_client, Client
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            logger.error("Supabase credentials missing")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def log_prediction(self, image_hash: str, predicted_species: str, confidence: float, gate_score: float, meta: Optional[Dict] = None) -> str:
        """Log a new prediction to the database."""
        if not self.client: return ""
        try:
            data = {
                "image_hash": image_hash,
                "predicted_species": predicted_species,
                "confidence": confidence,
                "gate_score": gate_score,
                "meta": meta or {}
            }
            result = self.client.table("predictions").insert(data).execute()
            if result.data:
                return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
        return ""

    def log_correction(self, prediction_id: str, correct_species: str) -> bool:
        """Log a user correction for a specific prediction."""
        if not self.client: return False
        try:
            data = {
                "prediction_id": prediction_id,
                "correct_species": correct_species
            }
            self.client.table("corrections").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to log correction: {e}")
        return False

    def get_correction_stats(self) -> List[Dict]:
        """Get stats on corrections per species for retraining focus."""
        if not self.client: return []
        try:
            # Simple aggregation via query
            result = self.client.table("corrections").select("correct_species").execute()
            if not result.data: return []
            
            stats = {}
            for row in result.data:
                species = row["correct_species"]
                stats[species] = stats.get(species, 0) + 1
            
            return [{"species": k, "corrections": v} for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True)]
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return []

feedback_service = FeedbackService()
