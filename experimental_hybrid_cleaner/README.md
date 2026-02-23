# Experimental Hybrid Cleaner Module

## Overview
This module explores an experimental composite cleaning approach unifying standard Telea Inpainting with a Frequency Separation refining step. It removes low-frequency noise (or artifacts from the inpainting) while attempting to synthesize or preserve high-frequency details (textures/grain) within the cleaned region.

## Strict Isolation Policy
This implementation adheres to a **Strict Isolation Requirement**:
- Zero modifications to the main `manga_cleaner_v2` repository.
- Does not import from or affect main architectural components (`core/`, `web_app/`, etc.).
- Does not inject new global dependencies (only relies on standard `numpy` and `cv2`).
- Safe to modify, delete, or run entirely independently.

## Getting Started & Test Runner
A minimal local testing environment is provided via `test_runner.py`.

### Execution
```bash
python test_runner.py
```

- If you don't provide `input.png` and `mask.png` in the directory, the script will mock them on its first run to demonstrate execution.
- Generates `output_test.png` containing the processed result.

## Hardware Expectations
- **Compute:** CPU-bound purely via classical Computer Vision linear operations.
- **Constraints Supported:** Lightweight; completely sidesteps heavy deep learning / neural network models (e.g., PyTorch).
- **Optimization Strategy:** Strictly clips its computational footprint to the Mask's Bounding Box (ROI). It never evaluates the entire canvas unnecessarily.

## Known Limitations
- High `texture_strength` (above `1.5` for example) can artificially inject aggressive grain or worsen heavy JPEG artifacts.
- The default inpainting method is OpenCV's standard TELEA pass, meaning very large, fully masked sections will still blur, though frequency separation will help hide the gradient edge.

## Future Extension Notes
<!--
 FUTURE EXTENSION & INTEGRATION STRATEGY:
 - Plugin Architecture: This module could be wrapped into the existing `core/pipeline.py` or `core/cleaner.py` by registering `HybridCleaner` as an interchangeable subclass or hook without altering state logic.
 - GUI Integration: Modifiers like `blur_kernel`, `texture_strength`, and `padding` can map directly to a new UI modal / popover, allowing real-time previews leveraging ROI clipping for speedy interactivity.
 - Adaptive Kernel: Instead of a static `blur_kernel`, logic can be programmed to expand proportional to the ROI dimensions.
 - Dynamic ROI Scaling: Using lower resolution pyramids for interactive previews before applying processing bounds on the high-fidelity input.
-->
