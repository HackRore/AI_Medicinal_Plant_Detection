import sys
sys.path.append(r"d:\PROJECT STAGE 1\backend")
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from app.services.ml_service import ml_service
import traceback

print("Testing direct load_models call...")
try:
    ml_service.load_models()
    print("--- STATUS ---")
    print(f"h5_model_type: {ml_service.h5_model_type}")
    print(f"use_mock: {ml_service.use_mock}")
    print(f"models_loaded: {ml_service.models_loaded}")
    if ml_service.h5_model:
        print(f"TensorFlow Model Input: {ml_service.h5_model.input_shape}")
except Exception as e:
    print("EXCEPTION CAUGHT:")
    traceback.print_exc()
