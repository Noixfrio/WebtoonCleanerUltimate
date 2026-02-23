import os
import threading
import numpy as np
import easyocr
from typing import List, Dict, Any, Optional
from config.settings import settings
from core.exceptions import OCRInitializationError, OCRFailureError
from core.logger import logger

class TextDetector:
    """
    Thread-safe Singleton OCR Detector.
    Uses EasyOCR as a production-grade proxy for Phase 2.6.
    """
    _instance: Optional['TextDetector'] = None
    _lock = threading.Lock()
    ocr: easyocr.Reader
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                try:
                    logger.info("Initializing EasyOCR Singleton Instance", extra={
                        "extra": {
                            "lang": [settings.OCR_LANG, 'en'],
                            "use_gpu": settings.ENABLE_GPU
                        }
                    })
                    cls._instance = super(TextDetector, cls).__new__(cls)
                    # EasyOCR initialization
                    # Note: easyocr uses 'ch_sim' or 'ch_tra' for chinese, mapping settings.OCR_LANG if needed
                    # but here we'll assume settings matches easyocr conventions or use 'en' as fallback
                    # Portability: Define local directory for weights if not provided
                    model_path = os.path.join(os.getcwd(), "assets", "ocr")
                    os.makedirs(model_path, exist_ok=True)
                    
                    cls._instance.ocr = easyocr.Reader(
                        ['ch_sim', 'en'] if settings.OCR_LANG == 'ch' else [settings.OCR_LANG, 'en'],
                        gpu=settings.ENABLE_GPU,
                        model_storage_directory=model_path
                    )
                    logger.info("EasyOCR Engine initialized successfully")
                except Exception as e:
                    logger.critical(f"OCR Initialization Failed: {str(e)}")
                    cls._instance = None
                    raise OCRInitializationError(f"Failed to start OCR engine: {str(e)}")
        return cls._instance

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
