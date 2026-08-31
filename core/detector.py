import os
import sys
import threading
import contextlib
import io
import numpy as np
import easyocr
from typing import List, Dict, Any, Optional

# Force UTF-8 encoding on Windows to avoid charmap codec errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and getattr(stream, "buffer", None) is not None:
            try:
                setattr(sys, stream_name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))
            except Exception:
                pass

from config.settings import settings
from config.user_config import get_models_dir
from core.exceptions import OCRInitializationError, OCRFailureError
from core.logger import logger

class TextDetector:
    """
    Thread-safe Singleton OCR Detector.
    Uses EasyOCR as a production-grade proxy for Phase 2.6.
    """
    _instance: Optional['TextDetector'] = None
    _lock = threading.Lock()
    _ocr: Optional[easyocr.Reader] = None
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TextDetector, cls).__new__(cls)
        return cls._instance

    @property
    def ocr(self) -> easyocr.Reader:
        """Lazy loader for EasyOCR engine."""
        if self._ocr is None:
            with self._lock:
                if self._ocr is None:
                    try:
                        logger.info("Initializing EasyOCR (Lazy Loading)...", extra={
                            "extra": {
                                "lang": [settings.OCR_LANG, 'en'],
                                "use_gpu": settings.ENABLE_GPU
                            }
                        })
                        # Portability: weights live in the user-chosen models disk
                        model_path = os.path.join(str(get_models_dir()), "assets", "ocr", "model")
                        os.makedirs(model_path, exist_ok=True)
                        
                        # On Windows, we need to redirect output to avoid charmap codec errors
                        # when easyocr tries to print progress bars with special characters
                        devnull = open(os.devnull, 'w', encoding='utf-8')
                        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                            self._ocr = easyocr.Reader(
                                ['ch_sim', 'en'] if settings.OCR_LANG == 'ch' else [settings.OCR_LANG, 'en'],
                                gpu=settings.ENABLE_GPU,
                                model_storage_directory=model_path,
                                verbose=False  # Disable verbose mode to suppress progress bars
                            )
                        devnull.close()
                        
                        logger.info("EasyOCR Engine initialized successfully")
                    except Exception as e:
                        logger.critical(f"OCR Initialization Failed: {str(e)}")
                        raise OCRInitializationError(f"Failed to start OCR engine: {str(e)}")
        return self._ocr

    def detect(self, image: np.ndarray, job_id: str = "unknown") -> List[Dict[str, Any]]:
        """
        Detects text in an image using EasyOCR.
        Returns a list of bounding boxes and confidence.
        """
        try:
            logger.info(f"Starting OCR detection [Job: {job_id}]", extra={"job_id": job_id})
            
            # EasyOCR returns list of (bbox, text, prob)
            results = self.ocr.readtext(image)
            
            boxes = []
            for (bbox, text, prob) in results:
                if prob >= settings.OCR_CONFIDENCE_THRESHOLD:
                    # bbox is [[x, y], [x, y], [x, y], [x, y]]
                    # We cast to float for consistency with previous pipeline expectations if needed
                    boxes.append({
                        "box": [[float(p[0]), float(p[1])] for p in bbox],
                        "text": text,
                        "confidence": float(prob)
                    })
            
            logger.info(f"OCR detection complete. Found {len(boxes)} candidates.", extra={"job_id": job_id})
            return boxes
            
        except Exception as e:
            logger.error(f"OCR Operation Failed [Job: {job_id}]: {str(e)}")
            raise OCRFailureError(f"OCR process failed: {str(e)}")
