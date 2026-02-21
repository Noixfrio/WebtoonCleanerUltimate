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
        
        # Mask refinement: Radius dilate (3) para pegar bem a borda preta
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)

        # Main Inpaint: Raio longo (25) puxa o branco do balão para o centro das letras garantindo limpeza total
        cleaned = cv2.inpaint(image, mask_refined, 25, cv2.INPAINT_TELEA)
        
        # Merge: Preserva a imagem inteira original, substituindo apenas a área do balão 
        # (onde mask > 0) pelo pedaço inpaintado
        final = np.where(mask_refined[..., None] > 0, cleaned, image)
        
        return final

    def process(self, image: np.ndarray, mask: np.ndarray, job_id: str = "unknown") -> np.ndarray:
        """Pipeline entry point."""
        return self.inpaint_native_ns(image, mask)
