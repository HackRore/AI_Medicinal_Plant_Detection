import os
import sys
import time

# Mock environment
os.environ["DATABASE_URL"] = "postgresql://postgres:PlantoAi%405665@db.bcyiaopmtmpqrjijtygu.supabase.co:5432/postgres"
os.environ["GEMINI_API_KEY"] = "AIzaSyC9oP0Mn7p6L6UYdeFA5g5Z_pui2aPQdUE"

# Add parent dir to sys.path
sys.path.append(os.getcwd())

from app.services.ml_service import get_ml_service

def test():
    print("Initializing MLService...")
    start = time.time()
    ml = get_ml_service()
    ml.load_resources()
    print(f"Loaded in {time.time() - start:.2f}s")
    
    if not (ml.interpreter or hasattr(ml, 'model')):
        print("FAILED to load any model (TFLite or Keras)")
        return

    # Create dummy image
    import numpy as np
    from PIL import Image
    import io
    
    dummy_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(dummy_img)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    img_bytes = buf.getvalue()
    
    print("Performing prediction...")
    start = time.time()
    res = ml.predict(img_bytes)
    print(f"Prediction result: {res['predicted_class']} ({res['confidence']*100:.1f}%)")
    print(f"Inference time: {time.time() - start:.2f}s")
    
    print("Generating Grad-CAM...")
    start = time.time()
    gradcam = ml.generate_gradcam(img_bytes)
    print(f"Grad-CAM generated in {time.time() - start:.2f}s")
    if gradcam:
        print("Grad-CAM Success (Base64 length: " + str(len(gradcam)) + ")")
    else:
        print("Grad-CAM Failed")

if __name__ == "__main__":
    test()
