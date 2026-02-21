import gc
import numpy as np
import logging
from core.tile_strategy import TileStrategy

logger = logging.getLogger(__name__)

class TileScheduler:
    """Orchestrates the tile-by-tile streaming process."""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.strategy = TileStrategy()

    def process_webtoon(self, image: np.ndarray, overlap: int = 64):
        """Processes an ultra-tall image using streaming tiles."""
        h, w = image.shape[:2]
        
        # 1. Calculate dynamic tile height based on current RAM
        tile_height = self.strategy.calculate_dynamic_height(w, h)
        coords = self.strategy.get_tile_coordinates(h, tile_height, overlap)
        
        logger.info(f"Starting Webtoon Streaming: {len(coords)} tiles [Size: {w}x{h}, TileH: {tile_height}]")
        
        # 2. Initialize final buffer (incremental construction)
        # In a real implementation, we might use the original image copy or a blank canvas
        # To save memory, we use the input image as a base if allowed, or pre-allocate.
        final_image = image.copy()
        
        for i, (y_start, y_end) in enumerate(coords):
            logger.info(f"Processing Tile {i+1}/{len(coords)} [Y: {y_start}:{y_end}]")
            
            # --- TILE ISOLATION START ---
            # Extract tile (This creates a view or copy)
            tile = image[y_start:y_end, :].copy()
            
            try:
                # Run the atomic pipeline on this tile
                # Note: This is where we call the existing pipeline.clean_image logic
                # For Phase 3A, we just define the loop structure.
                processed_tile = self._process_single_tile(tile)
                
                # Merge into final buffer
                # TODO: Implement blending in Phase 3B
                final_image[y_start:y_end, :] = processed_tile
                
            finally:
                # --- EXPLICIT DISPOSAL ---
                del tile
                if 'processed_tile' in locals():
                    del processed_tile
                gc.collect() 
            # --- TILE ISOLATION END ---
            
        return final_image

    def _process_single_tile(self, tile: np.ndarray):
        """Placeholder for actual tile processing (Phase 3B)."""
        # In the future, this calls self.pipeline logic
        return tile # Identity for now
