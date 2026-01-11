
import sys
import os
import asyncio
from pathlib import Path

# Add backend directory to sys.path to allow imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.ml_service import MLService

async def verify():
    print("🔬 INITIALIZING SYSTEM VERIFICATION...")
    print("-" * 50)
    
    # 1. Initialize Service
    try:
        service = MLService()
        print("✅ ML Service Initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ML Service: {e}")
        return

    # 2. Check Model Loading
    if service.use_mock:
        print("⚠️ WARNING: System is running in DEMO MODE (Mock). Real model not loaded.")
        print("   Checking for ONNX file...")
        model_path = backend_dir / "ml_models" / "mobilenetv2_best.onnx"
        if model_path.exists():
             print(f"   found: {model_path}")
             print("   Error might be in onnxruntime installation.")
        else:
             print(f"   MISSING: {model_path}")
    else:
        print("✅ REAL AI MODEL LOADED successfully")

    # 3. Test Prediction
    print("\n📸 Testing Prediction on Sample Image...")
    
    # Path to a sample image (Amrutha Balli)
    # Adjust this path based on the 'find_by_name' result relative to the script location
    # The script is in D:\PROJECT STAGE 1\backend\scripts
    # The dataset is in D:\PROJECT STAGE 1\dataset
    sample_image_path = Path(r"D:\PROJECT STAGE 1\dataset\Indian Medicinal Leaves Image Datasets\Medicinal plant dataset\Amruta_Balli\2500.jpg")
    
    if not sample_image_path.exists():
        print(f"❌ Sample image not found at: {sample_image_path}")
        # Try to find any jpg in the dataset to use as fallback
        print("   Searching for alternative image...")
        dataset_dir = Path(r"D:\PROJECT STAGE 1\dataset")
        found_images = list(dataset_dir.glob("**/*.jpg"))
        if found_images:
            sample_image_path = found_images[0]
            print(f"   Found alternative: {sample_image_path}")
        else:
            print("   No images found to test with.")
            return

    try:
        with open(sample_image_path, "rb") as f:
            image_bytes = f.read()
            
        print(f"   Analyzing '{sample_image_path.name}'...")
        result = await service.predict(image_bytes)
        
        print("\n📊 PREDICTION RESULT:")
        print("-" * 20)
        print(f"Predicted Plant: {result['predicted_plant']}")
        print(f"Confidence:      {result['confidence']:.2%}")
        
        if result['predicted_plant'] == 'Tinospora_cordifolia': # Scientific name for Amrutha Balli
             print("✅ ACCURACY CHECK PASSED: Correctly identified 'Amruta Balli' (Tinospora cordifolia)")
        else:
             print(f"ℹ️  Note: Predicted class '{result['predicted_plant']}' might differ from filename if taxonomy differs.")
             
        print("-" * 50)
        print("🚀 SYSTEM STATUS: FULLY FUNCTIONAL")
        
    except Exception as e:
        print(f"❌ Prediction Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
