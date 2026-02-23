import cv2
import numpy as np
import time
from core.pipeline import MangaCleanerPipeline

print("Starting Advanced DL Inpainting Test...")
pipeline = MangaCleanerPipeline()

# Gen Mock
img = np.zeros((800, 600, 3), dtype=np.uint8)
for y in range(800):
    b = int(255 - (y / 800) * 100)
    g = int(100 + (y / 800) * 155)
    r = 50
    img[y, :] = [b, g, r]

noise = np.random.randint(-30, 30, (800, 600, 3), dtype=np.int16)
img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

img_with_text = img.copy()
cv2.putText(img_with_text, "TEST", (100, 300), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 50, 50), 5, cv2.LINE_AA)

print("Processing fake image through Manga Pipeline V21.0...")

t0 = time.time()
res = pipeline.process_webtoon_streaming(img_with_text, "dl_test_job")
t1 = time.time()

print(f"DL Pipeline execution time: {t1 - t0:.2f} seconds.")
cv2.imwrite("mock_dl_result.png", res)
print("Finished.")
