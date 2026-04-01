import torch
import torch.nn as nn
from torchvision import models

def convert_to_onnx():
    model_path = "d:/PROJECT STAGE 1/backend/ml_models/model_v3.pth"
    onnx_path = "d:/PROJECT STAGE 1/backend/ml_models/model_v3.onnx"
    
    print(f"🔄 CONVERTING {model_path} TO ONNX...")
    
    # Recreate the model architecture (MobileNetV2)
    model = models.mobilenet_v2(weights=None)
    # Match the verified v3 head: Linear(1280, 512) -> ELU -> Linear(512, 5)
    model.classifier[1] = nn.Sequential(
        nn.Linear(1280, 512),
        nn.ELU(),
        nn.Linear(512, 5)
    )
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    
    # Export
    dummy_input = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        input_names=['input'], 
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"✅ EXPORTED TO {onnx_path}")

if __name__ == "__main__":
    convert_to_onnx()
