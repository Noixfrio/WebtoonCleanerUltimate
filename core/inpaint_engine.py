# core/inpaint_engine.py
import cv2
import numpy as np

class InpaintEngine:
    """
    Core engine for local, offline inpainting.
    Hardened for Senior CV standards: Navier-Stokes + Noise Injection.
    """
    def inpaint_native_ns(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Senior CV Implementation: Navier-Stokes (NS).
        Paranoid about memory safety and type casting.
        """
        # CRITICAL: Force alignment and type
        image = np.ascontiguousarray(image, dtype=np.uint8)
        mask = np.ascontiguousarray(mask, dtype=np.uint8)
        
        # Mask refinement: Radius 3 dilation to ensure we cover edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)

        # Main Inpaint: NS algorithm with Radius 3 for maximum sharpness
        cleaned = cv2.inpaint(image, mask_refined, 3, cv2.INPAINT_NS)
        
        # Noise Injection (15-sigma): Avoids unnatural 'plastic' look
        # Done in float space to prevent overflow issues
        noise = np.random.normal(0, 15, cleaned.shape).astype(np.float32)
        blended_noise = cv2.add(cleaned.astype(np.float32), noise)
        img_com_ruido = np.clip(blended_noise, 0, 255).astype(np.uint8)
        
        # Merge: Only apply noise + inpaint to the masked region
        # result = np.where(mask_refined[..., None] > 0, img_com_ruido, cleaned)
        # Optimized merge:
        mask_inv = cv2.bitwise_not(mask_refined)
        background = cv2.bitwise_and(cleaned, cleaned, mask=mask_inv)
        foreground = cv2.bitwise_and(img_com_ruido, img_com_ruido, mask=mask_refined)
        
        return cv2.add(background, foreground)

    def process(self, image: np.ndarray, mask: np.ndarray, job_id: str = "unknown") -> np.ndarray:
        """Pipeline entry point."""
        return self.inpaint_native_ns(image, mask)
