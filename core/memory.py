import psutil
import numpy as np
from typing import Tuple
from config.settings import settings
from core.exceptions import MemoryLimitExceededError
from core.logger import logger

def get_real_available_ram() -> int:
    """Returns real available RAM in bytes using psutil."""
    return psutil.virtual_memory().available

def calculate_estimated_usage(shape: Tuple[int, ...]) -> int:
    """
    Official Disciplined Formula: (W * H * 3 channels * 3 buffers) * 1.25 margin.
    """
    if len(shape) < 2:
        return 0
    h, w = shape[:2]
    # Assuming 3 channels (RGB) and 3 buffers (Original, Mask, Result)
    # Each pixel in uint8 is 1 byte
    base_size = h * w * 3 * 3
    estimated = int(base_size * settings.SAFETY_MARGIN)
    return estimated

def validate_memory_safety(image_shape: Tuple[int, ...], job_id: str = "foundation"):
    """
    Checks if job can proceed. Blocks and raises error if unsafe.
    """
    available_ram = get_real_available_ram()
    estimated_usage = calculate_estimated_usage(image_shape)
    
    # Threshold based on available RAM and max percentage setting
    threshold = int(available_ram * (settings.MAX_RAM_PERCENTAGE / 100.0))
    
    # Extra check for absolute resolution limit
    h, w = image_shape[:2]
    total_pixels = h * w
    
    log_data = {
        "job_id": job_id,
        "extra": {
            "ram_available_mb": round(available_ram / 1024**2, 2),
            "estimated_usage_mb": round(estimated_usage / 1024**2, 2),
            "threshold_mb": round(threshold / 1024**2, 2),
            "resolution": f"{w}x{h}"
        }
    }
    
    logger.info("Starting memory audit", extra=log_data)

    if estimated_usage > threshold:
        msg = f"Memory check failed: Required ~{estimated_usage / 1024**2:.2f}MB, Available: {available_ram / 1024**2:.2f}MB (Threshold: {threshold / 1024**2:.2f}MB)"
        logger.error(msg, extra=log_data)
        raise MemoryLimitExceededError(msg)
        
    if total_pixels > settings.MAX_IMAGE_PIXELS:
        msg = f"Resolution check failed: {total_pixels} pixels exceeds limit of {settings.MAX_IMAGE_PIXELS}"
        logger.error(msg, extra=log_data)
        raise MemoryLimitExceededError(msg)

    logger.info("Memory validation passed", extra=log_data)
