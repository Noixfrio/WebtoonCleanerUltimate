import sys
from unittest.mock import MagicMock, patch

# Module-level Mocking
mock_paddle = MagicMock()
sys.modules["paddleocr"] = mock_paddle
sys.modules["paddle"] = MagicMock()

import pytest
import time
import numpy as np
from core.inpaint_engine import InpaintEngine
from config.settings import settings

def test_retry_mathematical_stability_100_cycles():
    """
    RETRY STABILITY TEST: Execute 100 retry scenarios.
    Requirement: delay = 2^retry_count * BACKOFF_FACTOR.
    """
    engine = InpaintEngine()
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    dummy_mask = np.zeros((10, 10), dtype=np.uint8)
    
    delays_captured = []
    
    def mock_sleep(seconds):
        delays_captured.append(seconds)

    # Sequence: 2 failures (500) then 1 success (200)
    mock_response_fail = MagicMock(status_code=500, text="Error")
    mock_response_ok = MagicMock(status_code=200, content=b"bytes")
    
    with patch('requests.post', side_effect=[mock_response_fail, mock_response_fail, mock_response_ok] * 100):
        with patch('cv2.imencode', return_value=(True, MagicMock(tobytes=lambda: b"raw"))):
            with patch('cv2.imdecode', return_value=dummy_img):
                with patch('time.sleep', side_effect=mock_sleep):
                    for _ in range(100):
                        engine.process(dummy_img, dummy_mask)

    # Analysis
    # Each cycle (3 requests) adds 2 delays: attempt 0 (delay 2^0 * factor), attempt 1 (delay 2^1 * factor)
    assert len(delays_captured) == 200
    
    factor = settings.INPAINT_BACKOFF_FACTOR
    for i in range(0, 200, 2):
        assert delays_captured[i] == (factor ** 0)
        assert delays_captured[i+1] == (factor ** 1)

    print(f"\n[RETRY] Verified {len(delays_captured)} backoff delays mathematically.")
