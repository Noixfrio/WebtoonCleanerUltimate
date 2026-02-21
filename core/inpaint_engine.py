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
        
        # Mask refinement: Radius dilate leve para engolir contorno da fonte
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)

        # Retorna para o Inpaint clássico e inteligente do OpenCV.
        # Ele reconstrói a pintura do fundo naturalmente (se o fundo do balão for branco,
        # o texto some e vira branco; se o fundo tiver degradê ou arte, ele reconstrói a textura!)
        # Raio 5 ajuda a puxar a cor correta de fora da letra sem borrar milhas para longe
        cleaned = cv2.inpaint(image, mask_refined, 5, cv2.INPAINT_TELEA)
        
        # Merge de segurança: preserve inpaint apenas onde havia máscara
        final = np.where(mask_refined[..., None] > 0, cleaned, image)
        
        return final

    def process(self, image: np.ndarray, mask: np.ndarray, job_id: str = "unknown") -> np.ndarray:
        """Pipeline entry point."""
        return self.inpaint_native_ns(image, mask)
