import os
import cv2
import numpy as np
import logging

try:
    import onnxruntime
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

logger = logging.getLogger(__name__)

class LaMaInpainter:
    def __init__(self, model_path=None):
        if not HAS_ONNX:
            raise ImportError("onnxruntime is not installed. Deep Learning inpainting is unavailable.")
        
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "models", "lama.onnx")
            
        self.model_path = model_path
        self._session = None
        
        if os.path.exists(self.model_path):
            self._init_session()
        else:
            logger.warning(f"LaMa model not found at {self.model_path}. Advanced inpainting will fallback to standard methods.")

    def _init_session(self):
        try:
            # Explicitly define providers to prefer CPU if GPU isn't cleanly available for the user
            providers = ['CPUExecutionProvider']
            self._session = onnxruntime.InferenceSession(self.model_path, providers=providers)
            logger.info("LaMa ONNX model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load LaMa model: {e}")
            self._session = None

    def is_available(self):
        return self._session is not None

    def _pad_tensor(self, tensor, mod=8):
        """Pad tensor to be divisible by mod (required by LaMa architecture)."""
        b, c, h, w = tensor.shape
        pad_h = (mod - h % mod) % mod
        pad_w = (mod - w % mod) % mod
        if pad_h == 0 and pad_w == 0:
            return tensor, 0, 0
        return np.pad(tensor, ((0, 0), (0, 0), (0, pad_h), (0, pad_w)), mode='reflect'), pad_h, pad_w

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Inpaint regions using LaMa with ROI (Region of Interest) optimization.
        image: BGR uint8 [H, W, 3]
        mask: grayscale uint8 [H, W]
        """
        if not self.is_available():
            return image
        
        if not np.any(mask):
            return image

        orig_h, orig_w = image.shape[:2]

        # Identify Bounding Box for ROI
        y_indices, x_indices = np.where(mask > 0)
        y_min, y_max = np.min(y_indices), np.max(y_indices)
        x_min, x_max = np.min(x_indices), np.max(x_indices)
        
        # Padding for context (30% + 20px)
        h_mask, w_mask = y_max - y_min, x_max - x_min
        pad_h = int(h_mask * 0.3) + 20
        pad_w = int(w_mask * 0.3) + 20
        
        roi_y_min = max(0, y_min - pad_h)
        roi_y_max = min(orig_h, y_max + pad_h)
        roi_x_min = max(0, x_min - pad_w)
        roi_x_max = min(orig_w, x_max + pad_w)
        
        # Extract ROI
        roi_img = image[roi_y_min:roi_y_max, roi_x_min:roi_x_max].copy()
        roi_mask = mask[roi_y_min:roi_y_max, roi_x_min:roi_x_max].copy()
        H_roi, W_roi = roi_img.shape[:2]

        # Convert ROI to RGB and Resize for LaMa (Fixed 512x512)
        target_size = 512
        roi_rgb = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)
        roi_resized = cv2.resize(roi_rgb, (target_size, target_size), interpolation=cv2.INTER_AREA)
        mask_resized = cv2.resize(roi_mask, (target_size, target_size), interpolation=cv2.INTER_NEAREST)

        # Build tensors
        img_norm = roi_resized.astype(np.float32) / 255.0
        mask_norm = mask_resized.astype(np.float32) / 255.0
        
        img_tensor = np.transpose(img_norm, (2, 0, 1))
        img_tensor = np.expand_dims(img_tensor, axis=0) # [1, 3, 512, 512]
        
        mask_tensor = np.expand_dims(mask_norm, axis=0)
        mask_tensor = np.expand_dims(mask_tensor, axis=0) # [1, 1, 512, 512]

        try:
            inputs = {
                self._session.get_inputs()[0].name: img_tensor,
                self._session.get_inputs()[1].name: mask_tensor
            }
            
            outputs = self._session.run(None, inputs)
            output_tensor = outputs[0]
            
            # Post-process: LaMa returns [1, 3, 512, 512] with values ~ [0, 255]
            out_roi = output_tensor[0]
            out_roi = np.transpose(out_roi, (1, 2, 0))
            out_roi = np.clip(out_roi, 0, 255).astype(np.uint8)
            
            # Resize ROI back to original crop size
            out_roi_res = cv2.resize(out_roi, (W_roi, H_roi), interpolation=cv2.INTER_CUBIC)
            out_roi_bgr = cv2.cvtColor(out_roi_res, cv2.COLOR_RGB2BGR)

            # Integrate back into full image
            final_result = image.copy()
            final_result[roi_y_min:roi_y_max, roi_x_min:roi_x_max] = out_roi_bgr
            
            return final_result
            
        except Exception as e:
            logger.error(f"Inference failed during LaMa ROI execution: {e}")
            return image

# Singleton instance for pipeline
lama_engine = None

def get_lama_engine():
    global lama_engine
    if lama_engine is None:
        try:
            lama_engine = LaMaInpainter()
        except ImportError:
            pass
    return lama_engine
