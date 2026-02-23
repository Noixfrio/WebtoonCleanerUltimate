import cv2
import numpy as np

class FrequencySeparationPlugin:
    """
    Refinamento de frequência pós-inpainting operando apenas na ROI da máscara.
    Roda apenas na CPU usando processamento matricial NumPy/OpenCV.
    """
    
    def __init__(self, blur_kernel: int = 21, texture_strength: float = 1.2, feather_radius: int = 5, padding: int = 15):
        self.blur_kernel = blur_kernel if blur_kernel % 2 != 0 else blur_kernel + 1
        self.texture_strength = texture_strength
        self.feather_radius = feather_radius if feather_radius % 2 != 0 else feather_radius + 1
        self.padding = padding

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        image: Imagem base pós inpaint (H, W, 3) (uint8)
        mask: Máscara original com as áreas que foram consertadas (255 denotando a região a consertar)
        """
        # Checar se a máscara possui região a processar
        if len(mask.shape) == 3:
            mask_2d = mask[:, :, 0]
        else:
            mask_2d = mask
            
        y_indices, x_indices = np.where(mask_2d > 0)
        if len(y_indices) == 0:
            return image.copy()
            
        y_min, y_max = np.min(y_indices), np.max(y_indices)
        x_min, x_max = np.min(x_indices), np.max(x_indices)
        
        # Bounding box com padding
        H, W = image.shape[:2]
        y_min = max(0, y_min - self.padding)
        y_max = min(H, y_max + self.padding)
        x_min = max(0, x_min - self.padding)
        x_max = min(W, x_max + self.padding)
        
        # Extrair ROI e converter p/ float32
        roi_image = image[y_min:y_max, x_min:x_max].copy().astype(np.float32)
        roi_mask = mask_2d[y_min:y_max, x_min:x_max]
        
        # Gaussian blur para baixa frequência
        low_freq = cv2.GaussianBlur(roi_image, (self.blur_kernel, self.blur_kernel), 0)
        
        # Extração de alta frequência
        high_freq = roi_image - low_freq
        
        # Adicionar força (strength) das texturas na reconstrução
        refined_roi = low_freq + (high_freq * self.texture_strength)
        refined_roi = np.clip(refined_roi, 0, 255).astype(np.uint8)
        
        # Feather suave da máscara para suavização nas bordas da ROI
        feather_mask = cv2.GaussianBlur(roi_mask, (self.feather_radius, self.feather_radius), 0)
        feather_mask = feather_mask.astype(np.float32) / 255.0
        
        if len(feather_mask.shape) == 2:
            feather_mask = np.expand_dims(feather_mask, axis=-1)
            
        roi_image_uint8 = roi_image.astype(np.uint8)
        
        # Blend usando a mascara com feather
        blended_roi = (refined_roi * feather_mask + roi_image_uint8 * (1.0 - feather_mask))
        blended_roi = np.clip(blended_roi, 0, 255).astype(np.uint8)
        
        # Substituir ROI final na imagem base
        result_image = image.copy()
        result_image[y_min:y_max, x_min:x_max] = blended_roi
        
        return result_image
