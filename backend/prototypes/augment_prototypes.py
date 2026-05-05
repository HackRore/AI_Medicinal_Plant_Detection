import os
import torch
import open_clip
import numpy as np
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
MODEL_SAVE_DIR = r"d:\PROJECT FINAL\backend\ml_models"
PROTOTYPE_PATH = os.path.join(MODEL_SAVE_DIR, "prototypes.npy")
INDEX_PATH = os.path.join(MODEL_SAVE_DIR, "species_index.json")
CLASS_NAMES_V2 = os.path.join(MODEL_SAVE_DIR, "class_names_v2.json")

def augment_prototypes():
    logger.info("Augmenting Prototypes with Zero-Shot Text Embeddings...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load existing prototypes
    prototypes = np.load(PROTOTYPE_PATH, allow_pickle=True).item()
    
    # Load full class list
    with open(CLASS_NAMES_V2, 'r') as f:
        all_classes = json.load(f)
    
    # Initialize BioCLIP
    model, _, _ = open_clip.create_model_and_transforms('hf-hub:imageomics/bioclip-2')
    model = model.to(device)
    tokenizer = open_clip.get_tokenizer('hf-hub:imageomics/bioclip-2')
    model.eval()
    
    missing_classes = [c for c in all_classes if c not in prototypes]
    logger.info(f"Detected {len(missing_classes)} missing classes. Generating text prototypes...")
    
    with torch.no_grad():
        for species in missing_classes:
            # Construct a botanical prompt
            prompt = f"a close-up photo of a {species} leaf, botanical specimen"
            text_tokens = tokenizer([prompt]).to(device)
            text_features = model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            prototypes[species] = text_features.cpu().numpy()[0]
    
    # Rebuild species_index
    new_index = {idx: name for idx, name in enumerate(sorted(prototypes.keys()))}
    
    # Save results
    np.save(PROTOTYPE_PATH, prototypes)
    with open(INDEX_PATH, 'w') as f:
        json.dump(new_index, f, indent=2)
    
    logger.info(f"Final prototype store size: {len(prototypes)}")
    logger.info("Augmentation COMPLETE.")

if __name__ == "__main__":
    augment_prototypes()
