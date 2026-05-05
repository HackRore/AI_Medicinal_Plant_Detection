import os
import torch
import open_clip
import numpy as np
from PIL import Image
import json
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = r"d:\PROJECT FINAL\dataset\master_dataset"
MODEL_SAVE_DIR = r"d:\PROJECT FINAL\backend\ml_models"
PROTOTYPE_PATH = os.path.join(MODEL_SAVE_DIR, "prototypes.npy")
INDEX_PATH = os.path.join(MODEL_SAVE_DIR, "species_index.json")

def build_prototypes():
    logger.info("Initializing BioCLIP 2 for Prototype Generation...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Use base BioCLIP 2 as the feature extractor
    model, _, preprocess = open_clip.create_model_and_transforms('hf-hub:imageomics/bioclip-2')
    model = model.to(device)
    model.eval()
    
    species_list = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    prototypes = {}
    species_index = {}
    
    logger.info(f"Building prototypes for {len(species_list)} species...")
    
    with torch.no_grad():
        for idx, species in enumerate(tqdm(species_list)):
            species_dir = os.path.join(DATA_DIR, species)
            image_files = [f for f in os.listdir(species_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            # Limit to 15 images per species for efficiency and stability
            image_files = image_files[:15]
            
            embeddings = []
            for img_file in image_files:
                try:
                    img_path = os.path.join(species_dir, img_file)
                    image = Image.open(img_path).convert("RGB")
                    image_input = preprocess(image).unsqueeze(0).to(device)
                    
                    embedding = model.encode_image(image_input)
                    embedding /= embedding.norm(dim=-1, keepdim=True)
                    embeddings.append(embedding.cpu().numpy()[0])
                except Exception as e:
                    logger.warning(f"Error processing {img_file}: {e}")
            
            if embeddings:
                # MEAN embedding is the prototype
                prototypes[species] = np.mean(embeddings, axis=0)
                species_index[idx] = species
    
    # Save results
    np.save(PROTOTYPE_PATH, prototypes)
    with open(INDEX_PATH, 'w') as f:
        json.dump(species_index, f, indent=2)
    
    logger.info(f"Prototypes saved to {PROTOTYPE_PATH}")
    logger.info(f"Species index saved to {INDEX_PATH}")

if __name__ == "__main__":
    if not os.path.exists(MODEL_SAVE_DIR):
        os.makedirs(MODEL_SAVE_DIR)
    build_prototypes()
