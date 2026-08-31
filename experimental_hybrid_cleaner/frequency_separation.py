import cv2
import numpy as np

class FrequencySeparationPlugin:
    """
    Frequency Separation Plugin for image cleaning.
    Splits an image Region of Interest (ROI) into high and low frequencies.
    Optimized for low-end machines by processing only the masked bounding box.
    """
    def __init__(self, blur_kernel: int = 51, texture_strength: float = 1.0, 
                 feather_radius: int = 5, padding: int = 20):
        # Validate blur_kernel: must be odd and >= 3
        if blur_kernel < 3:
            blur_kernel = 3
        elif blur_kernel % 2 == 0:
            blur_kernel += 1
            
        self.blur_kernel = blur_kernel
        self.texture_strength = max(0.0, min(2.0, float(texture_strength)))
        self.feather_radius = max(1, int(feather_radius))
        self.padding = max(0, int(padding))

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Process the image within the mask bounding box using Frequency Separation.
        Returns the full image with the processed ROI inserted.
        """
        # If mask is empty, return original image immediately
        if not np.any(mask):
            return image

        # Detect bounding box
        y_indices, x_indices = np.where(mask > 0)
        y_min, y_max = y_indices.min(), y_indices.max()
        x_min, x_max = x_indices.min(), x_indices.max()

        # Expand bounding box using padding (clamped to image size)
        h, w = image.shape[:2]
        y_min = max(0, y_min - self.padding)
        y_max = min(h, y_max + self.padding + 1)
        x_min = max(0, x_min - self.padding)
        x_max = min(w, x_max + self.padding + 1)

        # Extract ROI only (never process full image)
        roi_img = image[y_min:y_max, x_min:x_max].copy()
        
        # Ensure mask is single channel and extract ROI mask
        if len(mask.shape) == 3:
            mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        else:
            mask_gray = mask
            
        roi_mask = mask_gray[y_min:y_max, x_min:x_max].copy()

        # Convert ROI to float32
        roi_float = roi_img.astype(np.float32)

        # Compute low and high frequencies
        low_freq = cv2.GaussianBlur(roi_float, (self.blur_kernel, self.blur_kernel), 0)
        high_freq = roi_float - low_freq

        # Feather mask using GaussianBlur
        feather_ksize = self.feather_radius * 2 + 1
        mask_float = roi_mask.astype(np.float32) / 255.0
        feathered_mask = cv2.GaussianBlur(mask_float, (feather_ksize, feather_ksize), 0)
        
        # Expand feathered mask dimensions for multi-channel operations
        if len(image.shape) == 3:
            feathered_mask = np.expand_dims(feathered_mask, axis=2)

        # Reconstruct region
        reconstructed = (1 - feathered_mask) * roi_float + feathered_mask * low_freq
        result = reconstructed + (high_freq * self.texture_strength * feathered_mask)

        # Clip to 0-255 and format back to uint8
        result_clipped = np.clip(result, 0, 255).astype(np.uint8)

        # Replace only ROI in a copy of the original image
        output_image = image.copy()
        output_image[y_min:y_max, x_min:x_max] = result_clipped

        return output_image
