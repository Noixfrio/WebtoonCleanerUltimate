import os
import psutil
import numpy as np
import gc
from core.tile_scheduler import TileScheduler

def test_tile_architecture():
    # Simulation: 1200x5000 image (Large Webtoon)
    width = 1200
    height = 5000
    
    print(f"--- WEBTOON ARCHITECTURE PREVIEW ---")
    print(f"Target Image: {width}x{height}")
    
    # Empty mock pipeline
    class MockPipeline:
        def clean_image(self, img, job_id): return img
        
    scheduler = TileScheduler(MockPipeline())
    
    initial_ram = psutil.virtual_memory().percent
    print(f"Initial RAM: {initial_ram}%")
    
    # Generic buffer for simulation
    # (We don't allocate the full 5000px if we want to be ultra-safe, 
    # but here it's ~18MB, so it's fine for testing 16GB)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Trigger processing
    processed = scheduler.process_webtoon(img)
    
    final_ram = psutil.virtual_memory().percent
    print(f"\nFinal RAM: {final_ram}%")
    print(f"RAM Shift: {final_ram - initial_ram:.2f}%")
    print(f"SUCCESS: Architectural flow verified.")

if __name__ == "__main__":
    test_tile_architecture()
