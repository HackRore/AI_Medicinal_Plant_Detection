import open_clip
import torch
print("Starting download for BioCLIP 2...")
try:
    model, _, preprocess = open_clip.create_model_and_transforms('hf-hub:imageomics/bioclip-2')
    print("Download Complete!")
except Exception as e:
    print(f"Error during download: {e}")
