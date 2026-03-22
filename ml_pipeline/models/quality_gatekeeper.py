"""
Quality Gatekeeper Module
Validates image quality before ML inference
- Blur detection (Laplacian variance)
- Brightness analysis
- Composition scoring (object size/position)
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class QualityGatekeeper:
    """Image Quality Validator for medicinal plant leaf images"""
    
    def __init__(
        self,
        blur_threshold: float = 100.0,
        brightness_min: float = 30.0,
        brightness_max: float = 225.0,
        min_object_size: float = 0.15,  # 15% of image
        max_object_size: float = 0.90,  # 90% of image
    ):
        """
        Initialize quality thresholds
        
        Args:
            blur_threshold: Laplacian variance threshold (higher = sharper). Default 100
            brightness_min: Minimum brightness level (0-255). Default 30
            brightness_max: Maximum brightness level (0-255). Default 225
            min_object_size: Minimum object size ratio. Default 0.15
            max_object_size: Maximum object size ratio. Default 0.90
        """
        self.blur_threshold = blur_threshold
        self.brightness_min = brightness_min
        self.brightness_max = brightness_max
        self.min_object_size = min_object_size
        self.max_object_size = max_object_size
    
    def check_quality(self, image_bytes: bytes) -> Dict:
        """
        Comprehensive image quality assessment
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dict with keys:
                - is_valid: bool (passed all checks)
                - scores: Dict of individual scores
                - reasons: List of failure reasons (if any)
                - recommendations: List of improvement suggestions
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "is_valid": False,
                    "scores": {},
                    "reasons": ["Failed to decode image"],
                    "recommendations": ["Ensure image is in JPEG or PNG format"]
                }
            
            # Run all checks
            blur_score = self._check_blur(image)
            brightness_score = self._check_brightness(image)
            composition_score = self._check_composition(image)
            
            reasons = []
            recommendations = []
            
            # Evaluate blur
            if blur_score < self.blur_threshold:
                reasons.append(f"Image is too blurry (score: {blur_score:.1f})")
                recommendations.append("Take a clearer, sharper photo of the leaf")
            
            # Evaluate brightness
            brightness_valid, brightness_msg, brightness_rec = brightness_score
            if not brightness_valid:
                reasons.append(brightness_msg)
                recommendations.append(brightness_rec)
            
            # Evaluate composition
            composition_valid, composition_msg, composition_rec = composition_score
            if not composition_valid:
                reasons.append(composition_msg)
                recommendations.append(composition_rec)
            
            is_valid = len(reasons) == 0
            
            return {
                "is_valid": is_valid,
                "scores": {
                    "blur": round(blur_score, 2),
                    "blur_threshold": self.blur_threshold,
                    "blur_passed": blur_score >= self.blur_threshold,
                    "brightness": brightness_score[0],
                    "composition": composition_score[0]
                },
                "reasons": reasons,
                "recommendations": recommendations,
                "image_shape": image.shape,
                "image_size_mb": len(image_bytes) / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Quality check error: {e}")
            return {
                "is_valid": False,
                "scores": {},
                "reasons": [f"Error analyzing image: {str(e)}"],
                "recommendations": ["Try uploading a different image"]
            }
    
    def _check_blur(self, image: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance
        Higher variance = sharper image
        
        Args:
            image: OpenCV image (BGR)
            
        Returns:
            Laplacian variance score
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    def _check_brightness(self, image: np.ndarray) -> Tuple[bool, str, str]:
        """
        Evaluate image brightness
        
        Args:
            image: OpenCV image (BGR)
            
        Returns:
            Tuple: (is_valid, message, recommendation)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = gray.mean()
        
        if mean_brightness < self.brightness_min:
            return (
                False,
                f"Image too dark (brightness: {mean_brightness:.1f})",
                "Increase lighting or take photo in brighter conditions"
            )
        elif mean_brightness > self.brightness_max:
            return (
                False,
                f"Image too bright/overexposed (brightness: {mean_brightness:.1f})",
                "Reduce glare or take photo in less bright conditions"
            )
        else:
            return (
                True,
                f"Brightness acceptable ({mean_brightness:.1f})",
                ""
            )
    
    def _check_composition(self, image: np.ndarray) -> Tuple[bool, str, str]:
        """
        Evaluate image composition (object size and positioning)
        
        Args:
            image: OpenCV image (BGR)
            
        Returns:
            Tuple: (is_valid, message, recommendation)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Convert to binary (find dark objects on light background)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Calculate object coverage
        object_pixels = np.count_nonzero(binary)
        total_pixels = binary.size
        object_ratio = object_pixels / total_pixels
        
        if object_ratio < self.min_object_size:
            return (
                False,
                f"Leaf too small in frame ({object_ratio*100:.1f}%)",
                "Zoom in or move leaf closer to camera"
            )
        elif object_ratio > self.max_object_size:
            return (
                False,
                f"Leaf takes up too much of frame ({object_ratio*100:.1f}%)",
                "Back away from leaf or adjust framing"
            )
        else:
            return (
                True,
                f"Composition good ({object_ratio*100:.1f}% coverage)",
                ""
            )


def quality_check(image_bytes: bytes, strict: bool = False) -> Dict:
    """
    Quick quality check function
    
    Args:
        image_bytes: Image data
        strict: If True, use stricter thresholds
        
    Returns:
        Quality assessment dict
    """
    if strict:
        gatekeeper = QualityGatekeeper(
            blur_threshold=150.0,
            brightness_min=50.0,
            brightness_max=200.0,
            min_object_size=0.20,
            max_object_size=0.85
        )
    else:
        gatekeeper = QualityGatekeeper()
    
    return gatekeeper.check_quality(image_bytes)
