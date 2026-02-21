import numpy as np
import cv2
from typing import List, Dict, Any, Tuple
from core.exceptions import MaskAlignmentError
from core.logger import logger

class MaskBuilder:
    """
    Utility for building binary masks (0/255) for inpainting.
    Ensures alignment and proper dilation.
    """
    @staticmethod
    def build(image_or_shape: Any, boxes: List[Dict[str, Any]], dilation: int = 0, padding: int = 20, **kwargs) -> np.ndarray:
        """
        Senior CV Implementation: Solid Bounding Boxes.
        Engulfs text and its anti-aliasing using aggressive padding.
        """
        if isinstance(image_or_shape, np.ndarray):
            h, w = image_or_shape.shape[:2]
        else:
            h, w = image_or_shape[:2]
            
        mask = np.zeros((h, w), dtype=np.uint8)
        
        for box_item in boxes:
            # Boxes come as poly points from EasyOCR
            poly = np.array(box_item["box"], dtype=np.int32)
            
            # Use Axis-Aligned Bounding Box (AABB) for maximum coverage
            x, y, wb, hb = cv2.boundingRect(poly)
            
            x_min = max(0, x - padding)
            y_min = max(0, y - padding)
            x_max = min(w, x + wb + padding)
            y_max = min(h, y + hb + padding)
            
            # Draw SOLID WHITE RECTANGLE
            cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
            
        return mask

    @staticmethod
    def validate_alignment(image: np.ndarray, mask: np.ndarray):
        """Ensures image and mask are compatible."""
        if image.shape[:2] != mask.shape[:2]:
            raise MaskAlignmentError(
                f"Image shape {image.shape[:2]} mismatch with mask shape {mask.shape[:2]}"
            )
        if mask.dtype != np.uint8:
            raise MaskAlignmentError(f"Mask must be uint8, got {mask.dtype}")
