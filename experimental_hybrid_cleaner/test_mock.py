import cv2
import numpy as np
from hybrid_cleaner import HybridCleaner

img = cv2.imread("mock_input.png")
mask = cv2.imread("mock_mask.png", cv2.IMREAD_GRAYSCALE)

cleaner = HybridCleaner(
    inpaint_radius=5,
    blur_kernel=51,
    texture_strength=1.5,
    feather_radius=3,
    padding=15
)
result = cleaner.process(img, mask)
cv2.imwrite("mock_hybrid_fixed.png", result)

print("Process finished.")
