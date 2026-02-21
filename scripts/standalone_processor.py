# scripts/standalone_processor.py

import os
import sys
import gc
import cv2
import time
import re
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.pipeline import MangaCleanerPipeline
from core.logger import logger

def natural_sort_key(s):
    """
    Key function for natural sorting (e.g., 1.png, 2.png, 10.png).
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def run_batch_processing(input_dir: str, output_dir: str):
    """
    Sênior Computer Vision Pipeline (V2.1 - Hardened):
    - 100% Offline
    - Natural Sorting implementation
    - Recursive OCR Verification Pass
    - Memory-Safe (16GB Plateau)
    """
    # 1. Setup
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pipeline = MangaCleanerPipeline()
    
    # 2. Natural Sorting
    extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    raw_files = [f for f in os.listdir(input_dir) if Path(f).suffix.lower() in extensions]
    
    # SORTING: MATHEMATICALLY CORRECT ORDER
    image_files = sorted(raw_files, key=natural_sort_key)
    
    logger.info(f"--- BATCH START: {len(image_files)} IMAGES (Natural Sorted) ---")
    start_time = time.time()
    
    success_count = 0
    fail_count = 0

    for i, filename in enumerate(image_files, 1):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"cleaned_{filename}")
        
        logger.info(f"[{i}/{len(image_files)}] Processing: {filename}")
        
        try:
            # 3. Memory-Safe Load
            image = cv2.imread(input_path)
            if image is None:
                logger.error(f"CORRUPT: Skipping {filename}")
                fail_count += 1
                continue
            
            # 4. Professional Streaming Pipeline (Includes Verification Pass)
            job_id = f"v2_{int(time.time())}_{i}"
            result = pipeline.process_webtoon_streaming(image, job_id=job_id, threshold=0.20)
            
            # 5. Optimized Save
            cv2.imwrite(output_path, result, [cv2.IMWRITE_PNG_COMPRESSION, 3])
            
            # 6. AGGRESSIVE CLEANUP
            del image
            del result
            gc.collect()
            
            success_count += 1
            logger.info(f"SUCCESS: {filename}")

        except Exception as e:
            logger.exception(f"FAILED {filename}: {str(e)}")
            fail_count += 1
            continue

    total_time = time.time() - start_time
    logger.info(f"--- BATCH FINISHED ---")
    logger.info(f"Total: {len(image_files)} | OK: {success_count} | Error: {fail_count}")
    logger.info(f"Time Taken: {total_time:.2f}s")

if __name__ == "__main__":
    in_dir = sys.argv[1] if len(sys.argv) > 1 else "inputs"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs"
    
    Path(in_dir).mkdir(exist_ok=True)
    run_batch_processing(in_dir, out_dir)
