import sys
from unittest.mock import MagicMock

# Module-level Mocking for dependencies that might not be in the test environment (e.g. PaddleOCR on Python 3.14)
mock_paddle = MagicMock()
sys.modules["paddleocr"] = mock_paddle
sys.modules["paddle"] = MagicMock()

import pytest
import numpy as np
import threading
from unittest.mock import MagicMock, patch
from core.detector import TextDetector
from core.inpaint_engine import InpaintEngine
from core.pipeline import MangaCleanerPipeline
from core.exceptions import (
    MangaCleanerError, MemoryLimitExceededError, InvalidImageError,
    OCRInitializationError, OCRFailureError, InpaintServiceError,
    InpaintTimeoutError, TileSeamError, MaskAlignmentError
)

# 1. DETECTOR TESTS
def test_detector_singleton():
    """Verify that TextDetector is a real Singleton across threads."""
    with patch('core.detector.PaddleOCR') as mock_ocr:
        d1 = TextDetector()
        d2 = TextDetector()
        assert d1 is d2
        
        # Test in multiple threads
        def get_instance(result_list):
            result_list.append(TextDetector())
            
        results = []
        threads = [threading.Thread(target=get_instance, args=(results,)) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        for inst in results:
            assert inst is d1

def test_detector_initialization_failure():
    """Verify OCRInitializationError is raised when PaddleOCR fails."""
    TextDetector._instance = None # Reset singleton for test
    with patch('core.detector.PaddleOCR', side_effect=Exception("GPU Fail")):
        with pytest.raises(OCRInitializationError):
            TextDetector()

# 2. INPAINT ENGINE TESTS
@patch('requests.post')
def test_inpaint_exponential_backoff(mock_post):
    """Simulate HTTP 500 response and verify retry with backoff."""
    mock_post.side_effect = [
        MagicMock(status_code=500, text="Internal Error"),
        MagicMock(status_code=500, text="Internal Error"),
        MagicMock(status_code=200, content=b"fake_image_bytes")
    ]
    
    # Mock cv2 to return numpy array which has .tobytes()
    mock_img = MagicMock(spec=np.ndarray)
    mock_img.tobytes.return_value = b"raw_bytes"
    
    with patch('cv2.imencode', return_value=(True, mock_img)):
        with patch('cv2.imdecode', return_value=np.zeros((10, 10, 3))):
            with patch('time.sleep'):
                engine = InpaintEngine()
                result = engine.process(np.zeros((10, 10, 3)), np.zeros((10, 10)))
                assert result is not None
                assert mock_post.call_count == 3

@patch('requests.post')
def test_inpaint_fail_fast_on_4xx(mock_post):
    """Verify NO retry on 400 Client Error."""
    mock_post.return_value = MagicMock(status_code=400, text="Bad Request")
    
    mock_img = MagicMock(spec=np.ndarray)
    mock_img.tobytes.return_value = b"raw_bytes"
    
    with patch('cv2.imencode', return_value=(True, mock_img)):
        engine = InpaintEngine()
        with pytest.raises(InpaintServiceError) as exc:
            engine.process(np.zeros((10, 10, 3)), np.zeros((10, 10)))
        assert "Inpaint client error 400" in str(exc.value)
        assert mock_post.call_count == 1

@patch('requests.post')
def test_inpaint_timeout_retry(mock_post):
    """Verify retry on requests.Timeout."""
    from requests import Timeout
    mock_post.side_effect = [Timeout(), MagicMock(status_code=200, content=b"ok")]
    
    mock_img = MagicMock(spec=np.ndarray)
    mock_img.tobytes.return_value = b"raw_bytes"
    
    with patch('cv2.imencode', return_value=(True, mock_img)):
        with patch('cv2.imdecode', return_value=np.zeros((10, 10, 3))):
            with patch('time.sleep'):
                engine = InpaintEngine()
                engine.process(np.zeros((10, 10, 3)), np.zeros((10, 10)))
                assert mock_post.call_count == 2

def test_detector_detect_logic():
    """Verify detection result parsing logic in the real class."""
    TextDetector._instance = None # Reset
    with patch('core.detector.PaddleOCR') as mock_paddle_cls:
        mock_ocr_inst = mock_paddle_cls.return_value
        # Mock PaddleOCR return format: [[ [box, (text, conf)], ... ]]
        mock_ocr_inst.ocr.return_value = [[
            [[[0,0], [10,0], [10,10], [0,10]], ("Hello", 0.9)],
            [[[20,20], [30,20], [30,30], [20,30]], ("LowConf", 0.1)]
        ]]
        
        detector = TextDetector()
        results = detector.detect(np.zeros((100, 100, 3)))
        
        assert len(results) == 1
        assert results[0]["text"] == "Hello"
        assert results[0]["confidence"] == 0.9

def test_mask_builder_dilation_and_alignment():
    """Verify mask building, dilation, and alignment validation."""
    from core.mask_builder import MaskBuilder
    shape = (100, 100, 3)
    boxes = [{"box": [[10, 10], [20, 10], [20, 20], [10, 20]]}]
    
    mask = MaskBuilder.build(shape, boxes, dilation=2)
    assert mask.shape == (100, 100)
    assert mask.dtype == np.uint8
    assert np.any(mask == 255)
    
    # Validation should pass
    MaskBuilder.validate_alignment(np.zeros(shape), mask)
    
    # Validation should fail on shape mismatch
    with pytest.raises(MaskAlignmentError):
        MaskBuilder.validate_alignment(np.zeros((50, 50, 3)), mask)
    
    # Validation should fail on dtype mismatch
    with pytest.raises(MaskAlignmentError):
        MaskBuilder.validate_alignment(np.zeros(shape), mask.astype(np.float32))

def test_inpaint_request_exception():
    """Verify InpaintServiceError on network failure."""
    from requests import RequestException
    engine = InpaintEngine()
    with patch('requests.post', side_effect=RequestException("Bad Connection")):
        with pytest.raises(InpaintServiceError):
            engine.process(np.zeros((10, 10, 3)), np.zeros((10, 10)))

def test_pipeline_cleanup_and_latency_logging():
    """Verify manual gc.collect and logging in pipeline."""
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    pipeline = MangaCleanerPipeline()
    
    pipeline.detector.detect = MagicMock(return_value=[{"box": [[1,1], [2,1], [2,2], [1,2]], "text": "ok", "confidence": 0.9}])
    pipeline.inpaint_engine.process = MagicMock(return_value=dummy_img.copy())
    
    with patch('gc.collect') as mock_gc:
        pipeline.clean_image(dummy_img)
        assert mock_gc.call_count >= 3

def test_pipeline_invalid_image_shape():
    """Verify check for invalid shape (too high resolution)."""
    pipeline = MangaCleanerPipeline()
    # Mocking the settings instance attribute
    with patch('core.memory.settings') as mock_settings:
        mock_settings.MAX_IMAGE_PIXELS = 10
        with pytest.raises(MemoryLimitExceededError) as exc:
            pipeline.clean_image(np.zeros((10, 10, 3)))
        assert "Resolution check failed" in str(exc.value)

def test_all_exceptions_coverage():
    """Touch all exceptions to ensure 100% coverage in exceptions.py."""
    MangaCleanerError("msg")
    InvalidImageError("msg")
    MemoryLimitExceededError("msg")
    OCRInitializationError("msg")
    OCRFailureError("msg")
    InpaintServiceError("msg")
    InpaintTimeoutError("msg")
    TileSeamError("msg")
    MaskAlignmentError("msg")

def test_memory_utils_coverage():
    """Ensure all utility lines in memory.py are covered."""
    from core.memory import get_real_available_ram, calculate_estimated_usage, validate_memory_safety
    
    # Test calculate_estimated_usage branches
    # Formula uses 3 channels and 3 buffers hardcoded for safety
    expected = int((100 * 100 * 3 * 3) * 1.25)
    assert calculate_estimated_usage((100, 100, 3)) == expected
    assert calculate_estimated_usage((100, 100)) == expected # grayscale still uses 3 channels for safety
    assert calculate_estimated_usage((100,)) == 0 # invalid
    
    # Test get_real_available_ram branches with psutil mock
    with patch('psutil.virtual_memory') as mock_vm:
        mock_vm.return_value.available = 1024 * 1024 * 100 # 100MB
        assert get_real_available_ram() == 1024 * 1024 * 100
        
    # Test validate_memory_safety threshold branch
    with patch('core.memory.get_real_available_ram', return_value=1000):
        with patch('core.memory.settings') as mock_settings:
            mock_settings.MAX_RAM_PERCENTAGE = 1
            mock_settings.MAX_IMAGE_PIXELS = 1000000 
            mock_settings.SAFETY_MARGIN = 1.25
            with pytest.raises(MemoryLimitExceededError) as exc:
                validate_memory_safety((10, 10, 3))
            assert "Memory check failed" in str(exc.value)

@patch('requests.post')
def test_inpaint_service_other_errors(mock_post):
    """Verify InpaintServiceError on 500 without retries remaining."""
    mock_post.return_value = MagicMock(status_code=500, text="Internal Error")
    with patch('core.inpaint_engine.settings') as mock_settings:
        mock_settings.INPAINT_MAX_RETRIES = 0
        engine = InpaintEngine()
        with pytest.raises(InpaintServiceError):
            engine.process(np.zeros((10, 10, 3)), np.zeros((10, 10)))
