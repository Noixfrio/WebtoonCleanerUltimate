import cv2
import numpy as np

class InpaintEngine:
    """Core engine for inpainting text/balloons."""
    def inpaint_native_ns(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Original Telea Inpainting."""
        image = np.ascontiguousarray(image, dtype=np.uint8)
        mask = np.ascontiguousarray(mask, dtype=np.uint8)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)
        
        cleaned = cv2.inpaint(image, mask_refined, 3, cv2.INPAINT_TELEA)
        return np.where(mask_refined[..., None] > 0, cleaned, image)

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Standard inpainting process."""
        return self.inpaint_native_ns(image, mask)
