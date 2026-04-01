import torch
import torch.nn as nn
from torchvision import models

def debug_pth():
    model_path = "d:/PROJECT STAGE 1/backend/ml_models/model_v3.pth"
    state_dict = torch.load(model_path, map_location='cpu')
    print("🔍 PTH KEYS:")
    for k in state_dict.keys():
        if "classifier" in k:
            print(f"  {k}: {state_dict[k].shape}")

if __name__ == "__main__":
    debug_pth()
