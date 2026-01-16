import asyncio
import os
import httpx
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/api/v1/predict"
DATASET_DIR = Path("d:/PROJECT STAGE 1/dataset/Indian Medicinal Leaves Image Datasets/Medicinal Leaf dataset")

async def test_prediction(image_path: Path, description: str):
    logger.info(f"--- Testing {description} ---")
    logger.info(f"Image: {image_path}")
    
    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        return

    async with httpx.AsyncClient() as client:
        try:
            files = {'file': (image_path.name, open(image_path, 'rb'), "image/jpeg")}
            response = await client.post(API_URL + "/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Prediction: {result['predicted_plant']}")
                logger.info(f"Confidence: {result['confidence']:.4f}")
                
                if "plant_details" in result and result['plant_details']:
                    logger.info("Plant Details: Found ✅")
                else:
                    logger.info("Plant Details: None (Expected for Unknown) ⚠️")
                    
                logger.info("Raw Result: " + str(result))
            else:
                logger.error(f"Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error: {str(e)}")

async def main():
    logger.info("Starting Confidence Verification...")
    
    # 1. Test Known Leaf (Neem)
    neem_path = DATASET_DIR / "Neem" / "1000.jpg" 
    # Adjust filename if needed, trying a likely one or listing dir
    if not neem_path.exists():
        # Find first jpg in Azadirachta_indica
        neem_dir = DATASET_DIR / "Azadirachta_indica"
        if neem_dir.exists():
            files = list(neem_dir.glob("*.jpg"))
            if files:
                neem_path = files[0]
    
    if neem_path.exists():
        await test_prediction(neem_path, "Known Leaf (Neem)")
    else:
        logger.warning("Could not find a Neem leaf to test!")

    # 2. Test Non-Leaf (Random file renamed to .jpg or using a known non-leaf image)
    # For this test, valid jpeg structure is needed. We can use a dummy 1x1 pixel image or just a random file that is an image.
    # Let's try to use a dummy image created by python
    import io
    from PIL import Image
    
    dummy_img = Image.new('RGB', (224, 224), color = (73, 109, 137))
    dummy_path = Path("dummy_non_leaf.jpg")
    dummy_img.save(dummy_path)
    
    await test_prediction(dummy_path, "Synthetic Non-Leaf Image")
    
    # Clean up
    if dummy_path.exists():
        os.remove(dummy_path)
        
    logger.info("Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
