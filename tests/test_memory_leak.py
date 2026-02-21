import sys
from unittest.mock import MagicMock, patch

# Module-level Mocking
mock_paddle = MagicMock()
sys.modules["paddleocr"] = mock_paddle
sys.modules["paddle"] = MagicMock()

import pytest
import os
import psutil
import gc
import numpy as np
from core.pipeline import MangaCleanerPipeline

def get_current_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def test_memory_leak_50_iterations():
    """
    MEMORY LEAK TEST: Execute 50 cycles and measure RAM Delta.
    Requirement: Max 5% variation.
    """
    pipeline = MangaCleanerPipeline()
    dummy_img = np.zeros((500, 500, 3), dtype=np.uint8)
    
    # Warup
    pipeline.clean_image(dummy_img)
    gc.collect()
    
    start_ram = get_current_memory_mb()
    print(f"\n[MEMORY] Start RAM: {start_ram:.2f} MB")

    with patch('core.pipeline.validate_memory_safety'):
        with patch.object(pipeline.detector, 'detect', return_value=[]):
            for i in range(50):
                pipeline.clean_image(dummy_img)
                if i % 10 == 0:
                    gc.collect()
                    print(f"[MEMORY] Iteration {i}, RAM: {get_current_memory_mb():.2f} MB")

    gc.collect()
    end_ram = get_current_memory_mb()
    delta_percent = ((end_ram - start_ram) / start_ram) * 100
    
    print(f"[MEMORY] End RAM: {end_ram:.2f} MB (Delta: {delta_percent:.2f}%)")
    
    # Allow small variance but fail on clear leak
    assert delta_percent < 5.0, f"Memory leak detected! Delta: {delta_percent:.2f}%"
