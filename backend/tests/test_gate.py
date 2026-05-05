import sys
import os
import torch
import numpy as np
from PIL import Image
import unittest

# Add parent dir to path to import botanical_gate
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from botanical_gate import gate

class TestBotanicalGate(unittest.TestCase):
    def setUp(self):
        self.leaf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "frontend", "public", "samples", "neem.jpg")
        self.red_path = "test_red.jpg"
        self.noise_path = "test_noise.jpg"

        # Create red image
        red_img = Image.new("RGB", (224, 224), (255, 0, 0))
        red_img.save(self.red_path)

        # Create noise image
        noise_arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise_arr)
        noise_img.save(self.noise_path)

    def tearDown(self):
        if os.path.exists(self.red_path): os.remove(self.red_path)
        if os.path.exists(self.noise_path): os.remove(self.noise_path)

    def test_real_leaf(self):
        print("\nTesting Real Leaf...")
        result = gate.verify(self.leaf_path)
        print(f"Result: {result}")
        self.assertTrue(result["is_leaf"], "Real leaf should pass the gate")
        self.assertGreater(result["botanical_confidence"], 0.5, "Leaf confidence should be high")

    def test_red_image(self):
        print("\nTesting Solid Red Image...")
        result = gate.verify(self.red_path)
        print(f"Result: {result}")
        self.assertFalse(result["is_leaf"], "Solid red image should fail the gate")

    def test_noise_image(self):
        print("\nTesting White Noise Image...")
        result = gate.verify(self.noise_path)
        print(f"Result: {result}")
        self.assertFalse(result["is_leaf"], "White noise image should fail the gate")

    def test_embedding_extraction(self):
        print("\nTesting Embedding Extraction...")
        embedding = gate.get_bioclip_embedding(self.leaf_path)
        print(f"Embedding shape: {embedding.shape}")
        self.assertEqual(embedding.shape, (768,), "Embedding should be 768-dimensional")
        self.assertNotEqual(np.sum(embedding), 0, "Embedding should not be all zeros")

if __name__ == "__main__":
    unittest.main()
