### Step 3 – Compute Maximum Tile Pixels
- `max_pixels = usable_bytes / 11.25`
- `tile_height = floor(max_pixels / image_width)`

### Step 4 – Clamp
- `tile_height = min(tile_height, image_height)`
- `tile_height = max(tile_height, 512)`

## 4. Overlap Strategy (Critical for Seam Safety)
Webtoon slicing is strictly vertical.
- **Minimum Overlap:** 64px recommended (never below 48px).
- **Rationale:** Prevents balloon center splitting, partial OCR detection, and visible seam artifacts.

## 5. Vertical Blend Merge (Mathematically Defined)
Blending applies ONLY to vertical overlap region.
- Let `O = overlap_height`, `y ∈ [0, O]`.
- `alpha = y / O`
- `final_pixel = (1 - alpha) * previous_tile_pixel + alpha * current_tile_pixel`

## 6. Memory Disposal Strategy (Mandatory)
After each tile:
- Merge tile into final buffer
- Explicitly delete: `tile_crop`, `tile_mask`, `tile_result`.
- Clear temporary OCR result structures.
- Call `gc.collect()`.

## 7. High-Risk Edge Case – Balloon Crossing Tile Boundary
- **Risk:** OCR may detect only partial text or mask may be incomplete.
- **Mitigation:** 64px overlap minimum + Mask dilation (2–4px).

## 8. CPU Performance Reality
- Estimated CPU timing: ~18–22s per tile (Inpaint dominant).
- 1200x8000 image ≈ 7 tiles ≈ **120–150s total processing time**.

## 9. GPU Optimization Path (Future Phase)
- When GPU available: Pre-allocate fixed VRAM buffer, remove safety multiplier, reduce tile count.

## 10. Strict Architectural Rules
- **Prohibited:** Multiprocessing (Phase 3A), Parallel tile execution, Storing tile list in memory, Copying full image per iteration.
- **Required:** Single final output buffer, Tile scoped variables only, Deterministic memory cleanup.

## 11. Roadmap
- **Phase 3B:** Real Tile Engine Implementation (Slicing, Blending, Validation).
- **Phase 4:** Web Layer (FastAPI).
- **Phase 5:** Desktop Mode.
- **Phase 6:** Stress Test & Production Certification.

**PHASE 3A STATUS: READY FOR ARCHITECTURE AUDIT ✅**
