import cv2
import numpy as np
import time
import os
from core.pipeline import MangaCleanerPipeline

def test_manual():
    print("Initializing Pipeline with real components...")
    pipeline = MangaCleanerPipeline()
    
    img_path = "inputs/42.png"
    if not os.path.exists(img_path):
        print(f"Error: Could not find {img_path}")
        return
        
    img = cv2.imread(img_path)
    
    print("Starting processing...")
    start = time.time()
    try:
        # A nova pipeline tem esse nome
        result = pipeline.process_webtoon_streaming(img, job_id="manual_test")
        latency = (time.time() - start) * 1000
        print(f"Success! Latency: {latency:.2f} ms")
        
        cv2.imwrite("outputs/manual_test_result.png", result)
        print("Result saved to outputs/manual_test_result.png")
        
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    test_manual()
