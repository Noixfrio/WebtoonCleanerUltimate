import cv2
import numpy as np
from core.advanced_inpaint import get_lama_engine

class FrequencySeparation:
    """Refinamento de frequência pós-inpainting."""
    def __init__(self, blur_kernel: int = 21, texture_strength: float = 1.2, feather_radius: int = 5):
        self.blur_kernel = blur_kernel if blur_kernel % 2 != 0 else blur_kernel + 1
        self.texture_strength = texture_strength
        self.feather_radius = feather_radius if feather_radius % 2 != 0 else feather_radius + 1

    def process_roi(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        y_indices, x_indices = np.where(mask > 0)
        if len(y_indices) == 0: return image
        y_min, y_max, x_min, x_max = np.min(y_indices), np.max(y_indices), np.min(x_indices), np.max(x_indices)
        padding = 15
        H, W = image.shape[:2]
        y_min, y_max = max(0, y_min - padding), min(H, y_max + padding)
        x_min, x_max = max(0, x_min - padding), min(W, x_max + padding)
        
        roi_img = image[y_min:y_max, x_min:x_max].copy().astype(np.float32)
        roi_mask = mask[y_min:y_max, x_min:x_max]
        
        low_freq = cv2.GaussianBlur(roi_img, (self.blur_kernel, self.blur_kernel), 0)
        high_freq = roi_img - low_freq
        refined_roi = low_freq + (high_freq * self.texture_strength)
        refined_roi = np.clip(refined_roi, 0, 255).astype(np.uint8)
        
        feather_mask = cv2.GaussianBlur(roi_mask, (self.feather_radius, self.feather_radius), 0).astype(np.float32) / 255.0
        if len(feather_mask.shape) == 2: feather_mask = np.expand_dims(feather_mask, axis=-1)
        
        blended_roi = (refined_roi * feather_mask + roi_img.astype(np.uint8) * (1.0 - feather_mask))
        result = image.copy()
        result[y_min:y_max, x_min:x_max] = blended_roi.astype(np.uint8)
        return result

class InpaintEngine:
    """Core engine for inpainting with Hybrid (LaMa + Frequency) support."""
    def inpaint_native_ns(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        image = np.ascontiguousarray(image, dtype=np.uint8)
        mask = np.ascontiguousarray(mask, dtype=np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_refined = cv2.dilate(mask, kernel, iterations=1)
        cleaned = cv2.inpaint(image, mask_refined, 5, cv2.INPAINT_TELEA)
        return np.where(mask_refined[..., None] > 0, cleaned, image)

    def hybrid_clean(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Pipeline Ultra Quality: LaMa + Frequency Refinement."""
        lama = get_lama_engine()
        if not lama or not lama.is_available():
            return self.inpaint_native_ns(image, mask)
            
        # Passo 1: LaMa DL Inpaint
        dl_result = lama.process(image, mask)
        
        # Passo 2: Frequency Refinement
        freq = FrequencySeparation()
        final_result = freq.process_roi(dl_result, mask)
        
        return final_result

    def process(self, image: np.ndarray, mask: np.ndarray, mode: str = "standard") -> np.ndarray:
        """Pipeline entry point."""
        if mode == "ultra":
            return self.hybrid_clean(image, mask)
        return self.inpaint_native_ns(image, mask)
