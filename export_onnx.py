"""
Export best.pt (trained PyTorch model) to ONNX format.
Replaces the broken plantoai_model.onnx with the real trained weights.
"""
import torch
import torch.nn as nn
import json
import os
import sys

print("=== PlantoAI ONNX Export Tool ===")

# Paths
PT_PATH   = "backend/ml_models/best.pt"
ONNX_OUT  = "backend/ml_models/plantoai_model.onnx"
CLASS_PATH = "backend/app/data/class_names.json"

# Load class names to determine number of classes
with open(CLASS_PATH) as f:
    class_names = json.load(f)
num_classes = len(class_names)
print(f"Classes: {num_classes}")

# Load checkpoint
print(f"Loading: {PT_PATH}")
ckpt = torch.load(PT_PATH, map_location="cpu")

# Determine what is in the checkpoint
if isinstance(ckpt, dict):
    print(f"Checkpoint keys: {list(ckpt.keys())}")
    state_dict = ckpt.get("model_state_dict") or ckpt.get("model") or ckpt.get("state_dict") or ckpt
else:
    state_dict = ckpt

# Build the model architecture (must match training)
try:
    from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
    model = efficientnet_v2_s(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print(f"Model loaded: EfficientNetV2-S with {num_classes} classes")
except Exception as e:
    print(f"torchvision load failed: {e}")
    try:
        import timm
        model = timm.create_model('tf_efficientnetv2_s', pretrained=False, num_classes=num_classes)
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        print(f"Model loaded via timm: EfficientNetV2-S with {num_classes} classes")
    except Exception as e2:
        print(f"timm load also failed: {e2}")
        sys.exit(1)

# Export to ONNX (single file, no external data)
dummy = torch.randn(1, 3, 224, 224)
print(f"Exporting to ONNX: {ONNX_OUT}")

# Remove old split files if they exist
for f in [ONNX_OUT, ONNX_OUT + ".data"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"  Removed old: {f}")

torch.onnx.export(
    model, dummy, ONNX_OUT,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17,
    # Force single-file output (no external data splitting)
)

size_mb = os.path.getsize(ONNX_OUT) / 1024 / 1024
print(f"\nExport complete!")
print(f"Output: {ONNX_OUT}")
print(f"Size: {size_mb:.1f} MB")

# Quick sanity check
import onnxruntime as ort
import numpy as np
sess = ort.InferenceSession(ONNX_OUT, providers=["CPUExecutionProvider"])
dummy_np = np.random.randn(1, 3, 224, 224).astype(np.float32)
out = sess.run(None, {"input": dummy_np})[0]
predicted_class = int(np.argmax(out[0]))
confidence = float(np.max(out[0]))
print(f"\nSanity check: predicted class {predicted_class} ({class_names[predicted_class] if predicted_class < len(class_names) else '?'}) raw logit={confidence:.2f}")
print("ONNX model is functional and ready for deployment!")
