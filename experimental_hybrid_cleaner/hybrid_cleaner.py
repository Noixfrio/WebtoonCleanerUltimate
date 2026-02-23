import cv2
import numpy as np
import os
import sys

# Ensure local directory is in path for direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from frequency_separation import FrequencySeparationPlugin

class HybridCleaner:
    """
    Hybrid Cleaner module integrating Inpaint and Frequency Separation.
    Pure functional processing, clean separation of responsibilities, no global variables.
    """
    def __init__(self, inpaint_radius: int = 5, blur_kernel: int = 51, 
                 texture_strength: float = 1.0, feather_radius: int = 5, padding: int = 20):
        self.inpaint_radius = max(1, int(inpaint_radius))
        
        # FrequencySeparationPlugin instantiated internally
        self.freq_sep_plugin = FrequencySeparationPlugin(
            blur_kernel=blur_kernel,
            texture_strength=texture_strength,
            feather_radius=feather_radius,
            padding=padding
        )

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Executes the hybrid cleaning pipeline: Inpaint (Telea) -> Frequency Refinement.
        """
        if not np.any(mask):
            return image

        # Ensure mask is single channel 8-bit for inpainting
        if len(mask.shape) == 3:
            mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        else:
            mask_gray = mask
            
        _, mask_bin = cv2.threshold(mask_gray, 127, 255, cv2.THRESH_BINARY)
        
        # Step 1: Telea Inpaint
        inpainted = cv2.inpaint(image, mask_bin, self.inpaint_radius, cv2.INPAINT_TELEA)

        # Step 2: Frequency Refinement
        frequency_refined = self.freq_sep_plugin.process(inpainted, mask_bin)

        return frequency_refined
