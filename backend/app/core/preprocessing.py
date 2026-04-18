"""
G9 Preprocessing Pipe - v14.0 Optimized
Centralized image pipeline to ensure 100% parity between training and inference.
"""
import numpy as np
from PIL import Image

class G9Preprocessor:
    def __init__(self, size=224):
        self.size = size
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def preprocess(self, img: Image.Image) -> np.ndarray:
        """
        Implements parity with:
        transforms.Resize((224,224))
        transforms.ToTensor()
        transforms.Normalize(mean, std)
        """
        # 1. Resize (Stretch) - Matches transforms.Resize
        img = img.convert("RGB").resize((self.size, self.size), Image.BILINEAR)
        
        # 2. ToTensor (0-1 Scaling + Typecast)
        arr = np.array(img).astype(np.float32) / 255.0
        
        # 3. Normalize (Broadcasting HWC)
        arr = (arr - self.mean) / self.std
        
        # 4. Transpose to CHW (NCHW batching handled in service)
        return arr.transpose(2, 0, 1)

# Singleton Instance
g9_pipe = G9Preprocessor()
