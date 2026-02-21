# core/tile_strategy.py

import math
import psutil
from config.settings import settings


MIN_TILE_HEIGHT = 512
OVERLAP = 64
BYTES_PER_PIXEL_EFFECTIVE = 11.25  # 3 * 3 * 1.25


def compute_dynamic_tile_height(image_width, image_height, threshold_percent=0.85):
    """
    Computes tile height dynamically based on real-time memory availability.
    Strictly follows the Version 3A architecture logic.
    """
    vm = psutil.virtual_memory()

    total_bytes = vm.total
    used_bytes = total_bytes - vm.available

    allowed_bytes = total_bytes * threshold_percent
    usable_bytes = allowed_bytes - used_bytes

    if usable_bytes <= 0:
        raise MemoryError("Not enough memory to safely allocate tile.")

    max_pixels = usable_bytes / BYTES_PER_PIXEL_EFFECTIVE
    tile_height = math.floor(max_pixels / image_width)

    tile_height = min(tile_height, image_height)
    tile_height = max(tile_height, MIN_TILE_HEIGHT)

    return tile_height


def generate_vertical_tiles(image_height, tile_height, overlap=OVERLAP):
    """
    Generator for vertical tile bounds (y_start, y_end) with specified overlap.
    """
    y = 0
    while y < image_height:
        end = min(y + tile_height, image_height)
        yield y, end

        if end == image_height:
            break

        y = end - overlap
