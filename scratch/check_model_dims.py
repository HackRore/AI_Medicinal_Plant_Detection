import onnxruntime as ort
import os

MODEL_PATH = 'backend/ml_models/plantoai_model.onnx'

def check_dims():
    sess = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    output_name = sess.get_outputs()[0].name
    output_shape = sess.get_outputs()[0].shape
    print(f"Output name: {output_name}")
    print(f"Output shape: {output_shape}")

if __name__ == "__main__":
    check_dims()
