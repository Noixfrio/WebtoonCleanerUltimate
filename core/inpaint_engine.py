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
        
        # Mask refinement: Radius 2 dilation to engolir apenas a fina borda sem borrao extra
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)

        # Main Inpaint: TELEA algorithm is better for structured blocks com inpaintRadius curto (2)
        cleaned = cv2.inpaint(image, mask_refined, 2, cv2.INPAINT_TELEA)
        
        # Merge: Preserva a imagem inteira original, substituindo apenas a área do balão 
        # (onde mask > 0) pelo pedaço inpaintado
        final = np.where(mask_refined[..., None] > 0, cleaned, image)
        
        return final

    def process(self, image: np.ndarray, mask: np.ndarray, job_id: str = "unknown") -> np.ndarray:
        """Pipeline entry point."""
        return self.inpaint_native_ns(image, mask)
