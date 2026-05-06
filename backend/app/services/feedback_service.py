import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class FeedbackService:
    """Manages prediction corrections and user feedback persistence."""
    def __init__(self):
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
