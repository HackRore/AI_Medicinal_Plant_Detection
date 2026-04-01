import torch

def debug_pth_deep():
    model_path = "d:/PROJECT STAGE 1/backend/ml_models/model_v3.pth"
    state_dict = torch.load(model_path, map_location='cpu')
    print("🔍 PTH DEEP KEYS:")
    # Check first conv layer
    first_key = list(state_dict.keys())[0]
    print(f"  First Key: {first_key} -> {state_dict[first_key].shape}")
    # Check classifier keys
    for k in state_dict.keys():
        if "classifier" in k:
            print(f"  {k}: {state_dict[k].shape}")

if __name__ == "__main__":
    debug_pth_deep()
