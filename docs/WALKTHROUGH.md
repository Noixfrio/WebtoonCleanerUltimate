# MangaCleaner V2 - Technical Walkthrough

## Architecture Overview
MangaCleaner V2 is built as a **Modular Hybrid Application**, sharing a single **Core Engine** between a FastAPI SaaS and a local Desktop application.

### core/
- `detector.py`: Thread-safe Singleton utilizing PaddleOCR for text detection.
- `mask_builder.py`: Robust generation of binary masks with dilation and boundary validation.
- `inpaint_engine.py`: Resilient adapter for the LaMa inpainting service, featuring exponential backoff, circuit breaking, and shape validation.
- `pipeline.py`: Orchestrator that handles single images and ultra-tall Webtoons via tile processing.
- `memory.py`: Safety-first memory validator using real-time RAM estimation.

## Professional Features
- **Defensive Design**: Custom exceptions for every failure point.
- **Memory Protection**: `(W*H*C*3) * 1.25` formula prevents OOM crashes.
- **Webtoon Support**: Vertical slicing with 64px overlap and linear blending for seamless results.
- **Structured Logging**: JSON logs for easy parsing by monitoring tools.

## Mode Comparison
| Feature | Web Mode (SaaS) | Desktop Mode (Local) |
| :--- | :--- | :--- |
| **Concurrency** | High (Multi-Worker) | Single Process |
| **Security** | Rate Limiting + MIME Check | Local File Access |
| **Performance** | Optimized for response time | Optimized for quality/memory |
| **Dependencies** | Remote LaMa service | Local LaMa backend |

## Performance Benchmarks (Estimates)
- **Standard Manga Page (1MP)**: ~1-3s total process time.
- **Webtoon (12k px height)**: ~15-30s depending on GPU/CPU fallback.
- **Memory Overhead**: ~400MB base + image buffers.
