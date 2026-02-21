import pytest
import os
import json
import numpy as np
import psutil
from config.settings import settings
from core.exceptions import (
    MangaCleanerError, MemoryLimitExceededError, InvalidImageError,
    OCRInitializationError, OCRFailureError, InpaintServiceError,
    InpaintTimeoutError, TileSeamError, MaskAlignmentError
)
from core.logger import logger
from core.memory import calculate_estimated_usage, validate_memory_safety, get_real_available_ram

def test_exception_hierarchy():
    """Verify all exceptions inherit correctly from MangaCleanerError."""
    exceptions_to_test = [
        MemoryLimitExceededError, InvalidImageError, OCRInitializationError,
        OCRFailureError, InpaintServiceError, InpaintTimeoutError,
        TileSeamError, MaskAlignmentError
    ]
    for exc_class in exceptions_to_test:
        assert issubclass(exc_class, MangaCleanerError)
        inst = exc_class("test message")
        assert inst.message == "test message"
        assert inst.error_code is not None

def test_memory_formula():
    """Verify the official pixel formula: (W * H * 3 * 3) * 1.25."""
    shape = (100, 100, 3)
    # 100 * 100 * 3 * 3 = 90,000
    # 90,000 * 1.25 = 112,500
    expected = int(100 * 100 * 3 * 3 * 1.25)
    assert calculate_estimated_usage(shape) == expected
    
    # Test grayscale: Original formula (W*H*3*3) remains constant as per user specification
    gray_shape = (100, 100)
    expected_gray = int(100 * 100 * 3 * 3 * 1.25)
    assert calculate_estimated_usage(gray_shape) == expected_gray

def test_memory_safety_blocking():
    """Verify that validated_memory_safety raises error for huge images."""
    bomb_shape = (100000, 100000, 3)
    with pytest.raises(MemoryLimitExceededError) as exc:
        validate_memory_safety(bomb_shape, job_id="test_bomb")
    assert "Memory check failed" in str(exc.value)
    
    # Test pixel limit
    pixel_bomb = (settings.MAX_IMAGE_PIXELS + 1, 1, 3)
    with pytest.raises(MemoryLimitExceededError) as exc:
        validate_memory_safety(pixel_bomb, job_id="pixel_bomb")
    assert "Resolution check failed" in str(exc.value)

def test_memory_safety_passing():
    """Verify small images pass validation."""
    small_shape = (100, 100, 3)
    validate_memory_safety(small_shape, job_id="test_pass")

def test_logger_json_validity():
    """Verify that the logger output is valid JSON using a unique test log."""
    test_log = "test_foundation.log"
    import logging
    from core.logger import DisciplinedJSONFormatter
    from logging.handlers import RotatingFileHandler
    
    test_logger = logging.getLogger("test_disciplined")
    test_logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(test_log, maxBytes=1000, backupCount=1)
    handler.setFormatter(DisciplinedJSONFormatter())
    test_logger.addHandler(handler)
    
    test_logger.info("Test JSON log", extra={"job_id": "test_json"})
    
    # Force close handler to release file
    handler.close()
    test_logger.removeHandler(handler)
    
    assert os.path.exists(test_log)
    with open(test_log, "r", encoding="utf-8") as f:
        line = f.readline()
        data = json.loads(line)
        assert data["message"] == "Test JSON log"
        assert data["job_id"] == "test_json"
        
    os.remove(test_log)

def test_settings_load():
    """Verify settings defaults and ENV override potential."""
    assert settings.SAFETY_MARGIN == 1.25
    assert settings.LOG_LEVEL == "INFO"
    
def test_real_ram_detection():
    """Verify psutil is returning a reasonable value."""
    ram = get_real_available_ram()
    assert ram > 0
    assert isinstance(ram, int)
