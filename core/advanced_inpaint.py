import os
import cv2
import numpy as np
import logging
import onnxruntime as ort
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)

class FrequencySeparation:
    """Original Refinement from tools/ultra_cleaner/frequency_refinement.py"""
    def __init__(self, blur_kernel: int = 21, texture_strength: float = 1.2, feather_radius: int = 5, padding: int = 15):
        self.blur_kernel = blur_kernel if blur_kernel % 2 != 0 else blur_kernel + 1
        self.texture_strength = texture_strength
        self.feather_radius = feather_radius if feather_radius % 2 != 0 else feather_radius + 1
        self.padding = padding

    def process_roi(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        if len(mask.shape) == 3: mask_2d = mask[:, :, 0]
        else: mask_2d = mask
            
        y_indices, x_indices = np.where(mask_2d > 0)
        if len(y_indices) == 0: return image.copy()
            
        y_min, y_max = np.min(y_indices), np.max(y_indices)
        x_min, x_max = np.min(x_indices), np.max(x_indices)
        
        H, W = image.shape[:2]
        y_min, y_max = max(0, y_min - self.padding), min(H, y_max + self.padding)
        x_min, x_max = max(0, x_min - self.padding), min(W, x_max + self.padding)
        
        roi_image = image[y_min:y_max, x_min:x_max].copy().astype(np.float32)
        roi_mask = mask_2d[y_min:y_max, x_min:x_max]
        
        low_freq = cv2.GaussianBlur(roi_image, (self.blur_kernel, self.blur_kernel), 0)
        high_freq = roi_image - low_freq
        refined_roi = low_freq + (high_freq * self.texture_strength)
        refined_roi = np.clip(refined_roi, 0, 255).astype(np.uint8)
        
        feather_mask = cv2.GaussianBlur(roi_mask, (self.feather_radius, self.feather_radius), 0).astype(np.float32) / 255.0
        if len(feather_mask.shape) == 2: feather_mask = np.expand_dims(feather_mask, axis=-1)
            
        roi_image_uint8 = roi_image.astype(np.uint8)
        blended_roi = (refined_roi * feather_mask + roi_image_uint8 * (1.0 - feather_mask))
        
        result = image.copy()
        result[y_min:y_max, x_min:x_max] = blended_roi.astype(np.uint8)
        return result

class LaMaInpainter:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LaMaInpainter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Priority: assets/lama.onnx (standalone) -> models/lama_512.onnx
        path1 = os.path.join(self.base_dir, "assets", "lama.onnx")
        path2 = os.path.join(self.base_dir, "models", "lama_512.onnx")
        self.model_path = path1 if os.path.exists(path1) else path2
        self._load_model()
        self._initialized = True

    def _load_model(self):
        try:
            if not os.path.exists(self.model_path):
                logger.info("Downloading LaMa model...")
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                downloaded = hf_hub_download(repo_id="Carve/LaMa-ONNX", filename="lama.onnx")
                import shutil
                shutil.copy(downloaded, self.model_path)
            
            self._session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            logger.info(f"LaMa loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading LaMa: {e}")

    def is_available(self): return self._session is not None

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        if not self.is_available(): return image
        
        # Exact logic from tools/ultra_cleaner/lama_wrapper.py
        if len(mask.shape) >= 3: mask = mask[:, :, 0]
        y_indices, x_indices = np.where(mask > 0)
        if len(y_indices) == 0: return image.copy()
        
        y_min, y_max, x_min, x_max = np.min(y_indices), np.max(y_indices), np.min(x_indices), np.max(x_indices)
        H, W = image.shape[:2]
        padding_h, padding_w = int((y_max-y_min)*0.3)+20, int((x_max-x_min)*0.3)+20
        
        ry1, ry2 = max(0, y_min-padding_h), min(H, y_max+padding_h)
        rx1, rx2 = max(0, x_min-padding_w), min(W, x_max+padding_w)
        
        roi_img = image[ry1:ry2, rx1:rx2].copy()
        roi_mask = mask[ry1:ry2, rx1:rx2].copy()
        
        # Resize for model
        roi_rgb = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)
        roi_res = cv2.resize(roi_rgb, (512, 512), interpolation=cv2.INTER_AREA)
        mask_res = cv2.resize(roi_mask, (512, 512), interpolation=cv2.INTER_NEAREST)
        
        # Tensors [0, 1]
        img_t = (roi_res.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        mask_t = (mask_res.astype(np.float32) / 255.0)[None, None]
        
        # Run
        inputs = {self._session.get_inputs()[0].name: img_t, self._session.get_inputs()[1].name: mask_t}
        out = self._session.run(None, inputs)[0][0]
        
        # Post
        out_roi = np.clip(out.transpose(1, 2, 0), 0, 255).astype(np.uint8)
        out_final = cv2.resize(out_roi, (roi_img.shape[1], roi_img.shape[0]), interpolation=cv2.INTER_CUBIC)
        out_bgr = cv2.cvtColor(out_final, cv2.COLOR_RGB2BGR)
        
        res = image.copy()
        res[ry1:ry2, rx1:rx2] = out_bgr
        return res

def get_lama_engine():
    global _lama_engine
    if '_lama_engine' not in globals() or _lama_engine is None:
        globals()['_lama_engine'] = LaMaInpainter()
    return globals()['_lama_engine']

def ultra_inpaint_area(image: np.ndarray, mask: np.ndarray, use_frequency_separation: bool = True) -> np.ndarray:
    """The 'From Scratch' Pipeline: LaMa + Frequency Refinement"""
    lama = get_lama_engine()
    step1 = lama.process(image, mask)
    
    if use_frequency_separation:
        freq = FrequencySeparation()
        return freq.process_roi(step1, mask)
    return step1
