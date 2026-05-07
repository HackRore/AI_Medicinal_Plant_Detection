from PIL import Image
import numpy as np
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configurable thresholds
LEAF_GATE_THRESHOLD = 0.30
OOD_REJECTION_MESSAGE = "Invalid Bio-Signature Detected — Please upload a clear photo of a single medicinal leaf"

class BotanicalGate:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotanicalGate, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing CLIP-base Gatekeeper...")
        try:
            import torch
            import open_clip
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                'hf-hub:openai/clip-vit-base-patch32'
            )
            self.tokenizer = open_clip.get_tokenizer('hf-hub:openai/clip-vit-base-patch32')
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # More specific positive prompts
            self.positive_prompts = [
                "a macro photo of a medicinal plant leaf", 
                "a close-up of a green botanical specimen", 
                "detailed leaf venation and margins"
            ]
            # Much stronger negative prompts to repel non-biological data
            self.negative_prompts = [
                "random static noise and pixels", 
                "a solid flat color block", 
                "a photograph of a person",
                "a vehicle or car",
                "an indoor room with furniture",
                "a computer screen or electronics"
            ]
            
            with torch.no_grad():
                self.pos_tokens = self.tokenizer(self.positive_prompts).to(self.device)
                self.neg_tokens = self.tokenizer(self.negative_prompts).to(self.device)
                self.pos_features = self.model.encode_text(self.pos_tokens)
                self.neg_features = self.model.encode_text(self.neg_tokens)
                self.pos_features /= self.pos_features.norm(dim=-1, keepdim=True)
                self.neg_features /= self.neg_features.norm(dim=-1, keepdim=True)
            
            self._initialized = True
            logger.info("CLIP-base Gatekeeper: ONLINE")
        except Exception as e:
            logger.error(f"CLIP-base Initialization Failed: {e}")
            self.model = None
            self._initialized = False

    def verify(self, image_path: str) -> dict:
        if not self._initialized or self.model is None:
            return {"is_leaf": True, "botanical_confidence": 1.0, "note": "Gatekeeper offline"}

        try:
            import torch
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                # Compute cosine similarities
                pos_sims = (image_features @ self.pos_features.T).cpu().numpy()[0]
                neg_sims = (image_features @ self.neg_features.T).cpu().numpy()[0]

                pos_avg = np.mean(pos_sims)
                neg_avg = np.mean(neg_sims)

                # Robustness logic:
                # 1. Must be above absolute threshold
                # 2. Must be significantly better than negative prompts
                is_leaf = pos_avg > LEAF_GATE_THRESHOLD and pos_avg > (neg_avg + 0.02)
                confidence = float(pos_avg)

                logger.info(f"Gatekeeper Scores: POS={pos_avg:.4f} NEG={neg_avg:.4f}")

                if not is_leaf:
                    logger.warning(f"[GATE REJECTED] pos={pos_avg:.4f} neg={neg_avg:.4f} timestamp={datetime.now()}")
                    return {
                        "is_leaf": False, 
                        "reason": OOD_REJECTION_MESSAGE, 
                        "confidence": confidence,
                        "botanical_confidence": round(confidence * 100, 2)
                    }

                return {
                    "is_leaf": True, 
                    "botanical_confidence": round(confidence * 100, 2)
                }

        except Exception as e:
            logger.error(f"Gate Verification Error: {e}")
            return {"is_leaf": True, "botanical_confidence": 0.5, "error": str(e)}

    def get_bioclip_embedding(self, image_path: str) -> np.ndarray:
        if not self._initialized or self.model is None:
            return np.zeros(512) # clip-base has 512 embedding dim, not 768 like bioclip

        try:
            import torch
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                return image_features.cpu().numpy()[0]
        except Exception as e:
            logger.error(f"Embedding Extraction Error: {e}")
            return np.zeros(512)

_gate = None
def get_gate():
    global _gate
    if _gate is None:
        _gate = BotanicalGate()
    return _gate
