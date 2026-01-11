@echo off
echo 🌿 AI Medicinal Plant System - Model Deployment
echo ------------------------------------------------

echo 📦 Installing Dependencies...
python -m pip install onnx onnxscript
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo 🧠 Training MobileNetV2 on your dataset...
cd ..
set PYTHONPATH=%CD%
python scripts/train_model.py

if exist "ml_models/mobilenetv2_best.onnx" (
    echo ✅ Model generated successfully!
    echo 🚀 The system is now fully functional with YOUR data.
) else (
    echo ❌ Model training failed. Check logs.
)

pause
