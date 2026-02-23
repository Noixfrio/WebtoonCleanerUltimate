import cv2
import numpy as np
import os

def create_mock_manga_panel():
    # 1. Create a background with a strong gradient and noise (simulating "texture" / "art")
    img = np.zeros((800, 600, 3), dtype=np.uint8)
    for y in range(800):
        # Blue to cyan gradient
        b = int(255 - (y / 800) * 100)
        g = int(100 + (y / 800) * 155)
        r = 50
        img[y, :] = [b, g, r]
    
    # Add noise (grain/texture)
    noise = np.random.randint(-30, 30, (800, 600, 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 2. Add some "Speed Lines" (common in manga/manhwa)
    for _ in range(50):
        x1 = np.random.randint(0, 600)
        x2 = x1 + np.random.randint(-50, 50)
        y1 = np.random.randint(0, 800)
        y2 = y1 + np.random.randint(100, 300)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)

    # Save original art without text
    cv2.imwrite("mock_art_original.png", img)

    # 3. Add text that needs to be cleaned
    img_with_text = img.copy()
    font = cv2.FONT_HERSHEY_TRIPLEX
    cv2.putText(img_with_text, "THREE-DAY", (100, 300), font, 2, (255, 50, 50), 5, cv2.LINE_AA)
    cv2.putText(img_with_text, "TECHNIQUE", (100, 360), font, 2, (255, 50, 50), 5, cv2.LINE_AA)
    
    cv2.imwrite("mock_input.png", img_with_text)

    # 4. Create Mask for the text
    mask = np.zeros((800, 600), dtype=np.uint8)
    cv2.putText(mask, "THREE-DAY", (100, 300), font, 2, 255, 15, cv2.LINE_AA)
    cv2.putText(mask, "TECHNIQUE", (100, 360), font, 2, 255, 15, cv2.LINE_AA)
    
    cv2.imwrite("mock_mask.png", mask)
    
    # 5. Simulate BAD inpainting (what the user sees right now)
    bad_inpaint = cv2.inpaint(img_with_text, mask, 3, cv2.INPAINT_TELEA)
    cv2.imwrite("mock_bad_inpaint.png", bad_inpaint)

create_mock_manga_panel()
print("Mock images generated successfully.")
