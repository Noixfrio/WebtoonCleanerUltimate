import sys
from unittest.mock import MagicMock, patch

# Module-level Mocking
mock_paddle = MagicMock()
sys.modules["paddleocr"] = mock_paddle
sys.modules["paddle"] = MagicMock()

import pytest
import threading
import numpy as np
from core.detector import TextDetector
from core.pipeline import MangaCleanerPipeline

def test_singleton_concurrency_load():
    """
    STRESS TEST: 20 simultaneous threads requesting the detector.
    Requirement: Only 1 instance must exist.
    """
    instances = []
    errors = []
    
    def worker():
        try:
            # Each worker attempts to get or create the singleton
            inst = TextDetector()
            instances.append(inst)
        except Exception as e:
            errors.append(e)

    # Launch 20 threads
    threads = [threading.Thread(target=worker) for _ in range(20)]
    
    with patch('core.detector.PaddleOCR'):
        # Reset singleton to ensure fresh test
        TextDetector._instance = None
        
        for t in threads: t.start()
        for t in threads: t.join()

    assert len(errors) == 0, f"Errors during concurrency: {errors}"
    assert len(instances) == 20
    
    # All instances should be the exact same object in memory
    first_id = id(instances[0])
    for i, inst in enumerate(instances):
        assert id(inst) == first_id, f"Thread {i} got a different instance!"
    
    print(f"\n[STRESS] Singleton uniqueness verified for {len(instances)} threads.")

def test_pipeline_parallel_execution():
    """
    STRESS TEST: 10 threads executing the full pipeline simultaneously.
    Validates thread-safety and lack of deadlocks.
    """
    pipeline = MangaCleanerPipeline()
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    results = []
    
    def run_pipeline():
        try:
            res = pipeline.clean_image(dummy_img, job_id=f"stress_{threading.get_ident()}")
            results.append(res)
        except Exception as e:
            results.append(e)

    # Patch external calls
    with patch('core.pipeline.validate_memory_safety'):
        with patch.object(pipeline.detector, 'detect', return_value=[]):
            threads = [threading.Thread(target=run_pipeline) for _ in range(10)]
            for t in threads: t.start()
            for t in threads: t.join()

    assert len(results) == 10
    for res in results:
        assert isinstance(res, np.ndarray), f"Pipeline failed in thread: {res}"
        
    print(f"\n[STRESS] Parallel pipeline execution successful for 10 threads.")
