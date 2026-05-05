import numpy as np
import json
import os
import logging

logger = logging.getLogger(__name__)

class PrototypicalClassifier:
    def __init__(self, prototypes_path: str, index_path: str):
        self.prototypes_path = prototypes_path
        self.index_path = index_path
        self.prototypes = {}
        self.species_index = {}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.prototypes_path):
                self.prototypes = np.load(self.prototypes_path, allow_pickle=True).item()
                logger.info(f"Loaded {len(self.prototypes)} species prototypes.")
            
            if os.path.exists(self.index_path):
                with open(self.index_path, 'r') as f:
                    self.species_index = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load prototypical store: {e}")

    def predict(self, query_embedding: np.ndarray) -> dict:
        """
        Compute cosine similarity between query and all prototypes.
        """
        if not self.prototypes:
            return {"error": "Prototypes not loaded"}

        results = []
        for name, proto in self.prototypes.items():
            # Cosine similarity (both are already normalized)
            sim = np.dot(query_embedding, proto)
            results.append({"species": name, "confidence": float(sim)})

        # Sort by similarity descending
        results = sorted(results, key=lambda x: x["confidence"], reverse=True)
        top3 = results[:3]

        for i, res in enumerate(top3):
            res["rank"] = i + 1

        top1 = top3[0]
        top2 = top3[1] if len(top3) > 1 else None

        # Confidence Tiers
        conf = top1["confidence"]
        if conf >= 0.88:
            tier = "HIGH — Confident identification"
            color = "green"
        elif conf >= 0.70:
            tier = "MODERATE — Verify visually"
            color = "amber"
        else:
            tier = "LOW — Manual verification recommended"
            color = "red"

        # Ambiguity Check
        ambiguous = False
        if top2 and (top1["confidence"] - top2["confidence"]) < 0.05:
            ambiguous = True

        return {
            "top1_species": top1["species"],
            "top1_confidence": top1["confidence"],
            "confidence_tier": tier,
            "confidence_color": color,
            "top3": top3,
            "ambiguous": ambiguous,
            "note": "Two species are visually similar — compare both results" if ambiguous else None
        }
