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
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = None
        
        if url and key:
            try:
                self.client = create_client(url, key)
            except Exception as e:
                logger.error(f"Supabase connection failed: {str(e)}")
        
        # Local persistence for scheduled model fine-tuning
        self.local_log = "backend/data/corrections_active_learning.jsonl"
        os.makedirs(os.path.dirname(self.local_log), exist_ok=True)

    async def log_correction(self, feedback_payload: Dict[str, Any]):
        """Persists user-provided corrections to Supabase and local active-learning buffer."""
        try:
            entry = {
                "prediction_id": feedback_payload.get("prediction_id"),
                "observed_species": feedback_payload.get("correct_species"),
                "predicted_species": feedback_payload.get("predicted_species"),
                "confidence_score": feedback_payload.get("confidence"),
                "user_note": feedback_payload.get("note"),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Remote persistence for real-time monitoring
            if self.client:
                self.client.table("prediction_corrections").insert(entry).execute()

            # Local persistence
            with open(self.local_log, "a") as f:
                f.write(json.dumps(entry) + "\n")

            logger.info(f"Correction logged: {feedback_payload.get('prediction_id')}")

        except Exception as e:
            logger.error(f"Feedback persistence failed: {str(e)}")

feedback_service = FeedbackService()
