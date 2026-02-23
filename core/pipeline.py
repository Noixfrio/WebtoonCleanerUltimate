# core/pipeline.py

import cv2
import numpy as np
import gc
import os
from pathlib import Path
from typing import List, Dict

from core.detector import TextDetector
from core.mask_builder import MaskBuilder
from core.inpaint_engine import InpaintEngine
from core.logger import logger

DEBUG_MODE = True
DEBUG_DIR = "debug"

class MangaCleanerPipeline:
    def __init__(self):
        self.detector = TextDetector()
        self.mask_builder = MaskBuilder()
        self.inpaint_engine = InpaintEngine()
        if DEBUG_MODE: Path(DEBUG_DIR).mkdir(exist_ok=True)

    def _preprocess_for_ocr(self, tile: np.ndarray) -> np.ndarray:
        # EasyOCR (CRAFT) precisa de imagens naturais para funcionar bem.
        img = np.ascontiguousarray(tile, dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def build_feathered_mask(self, shape: tuple, boxes: List[Dict], padding: int = 15) -> np.ndarray:
        h, w = shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        tile_area = h * w
        for box_item in boxes:
            pts = np.array(box_item["box"], dtype=np.int32)
            rx, ry, bw, bh = cv2.boundingRect(pts)
            if (bw * bh) > (tile_area * 0.05): continue
            
            temp = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(temp, [pts], 255)
            mask = cv2.bitwise_or(mask, temp)
        
        if np.any(mask):
            k_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (padding, padding))
            mask = cv2.dilate(mask, k_connect)
        return mask

    def process_webtoon_streaming(self, image: np.ndarray, job_id: str, threshold: float = 0.05) -> np.ndarray:
        """Architecture V21.0: Balloon-Aware Local Cleaner."""
        res, count = self._process_core(image, job_id, threshold)
        return res

    def _process_core(self, image: np.ndarray, job_id: str, threshold: float = 0.05):
        """Architecture V21.0: Balloon-Aware Local Cleaner CORE."""
        raw_full = np.ascontiguousarray(image, dtype=np.uint8)
        h, w = raw_full.shape[:2]
        pad_h = 150
        img_padded = cv2.copyMakeBorder(raw_full, 0, pad_h, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        tile_h = 2048
        overlap = 120
        stride = tile_h - overlap
        result_padded = np.zeros(img_padded.shape, dtype=np.uint8)
        
        logger.info(f"V21.0 BALLOON-AWARE MISSION [Job: {job_id}] | Threshold {threshold}")

        cleaned_total_count = 0
        y_start = 0
        padded_h = img_padded.shape[0]
        while y_start < padded_h:
            y_end = min(y_start + tile_h, padded_h)
            tile = np.array(img_padded[y_start:y_end, 0:w], copy=True, order='C')
            
            ocr_ready = self._preprocess_for_ocr(tile)
            results = self.detector.ocr.readtext(ocr_ready)
            
            boxes = [{"box": [[float(p_val[0]), float(p_val[1])] for p_val in b]} for (b, t, p) in results if p >= threshold]
            
            cleaned_tile = tile.copy()
            if boxes:
                logger.info(f"Page Mission [Job: {job_id}]: Found {len(boxes)} text candidates in tile.")
                for box_item in boxes:
                    pts = np.array(box_item["box"], dtype=np.int32)
                    rx, ry, bw, bh = cv2.boundingRect(pts)
                    rx, ry = max(0, rx), max(0, ry)
                    
                    if (bw * bh) > (tile.shape[0] * tile.shape[1] * 0.15): 
                        continue
                    
                    bg_pad = 12
                    bg_x1 = max(0, rx - bg_pad)
                    bg_y1 = max(0, ry - bg_pad)
                    bg_x2 = min(w, rx + bw + bg_pad)
                    bg_y2 = min(tile.shape[0], ry + bh + bg_pad)
                    
                    roi_bg = cleaned_tile[bg_y1:bg_y2, bg_x1:bg_x2]
                    if roi_bg.size == 0: continue
                    
                    top = roi_bg[0, :]
                    bottom = roi_bg[-1, :]
                    left = roi_bg[:, 0]
                    right = roi_bg[:, -1]
                    borders = np.concatenate([top, bottom, left, right], axis=0).astype(np.int32)
                    
                    if len(borders) == 0: continue
                    
                    median_c = np.median(borders, axis=0).astype(np.int32)
                    diffs = np.sum(np.abs(borders - median_c), axis=-1)
                    uniform_ratio = np.mean(diffs < 60)
                    
                    if uniform_ratio > 0.65:
                        cleaned_total_count += 1
                        pad = 5
                        x1 = max(0, rx - pad)
                        y1 = max(0, ry - pad)
                        x2 = min(w, rx + bw + pad)
                        y2 = min(tile.shape[0], ry + bh + pad)
                        
                        tight_roi = cleaned_tile[y1:y2, x1:x2].copy()
                        bg_luminance = int(median_c[0]) + int(median_c[1]) + int(median_c[2])
                        roi_luminance = np.sum(tight_roi.astype(np.int32), axis=-1)
                        
                        if bg_luminance > 380: # Light Balloon
                            mask = (roi_luminance < bg_luminance - 40).astype(np.uint8) * 255
                        else: # Dark Balloon
                            mask = (roi_luminance > bg_luminance + 40).astype(np.uint8) * 255
                            
                        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                        mask = cv2.dilate(mask, kernel, iterations=1)
                        
                        local_cleaned = self.inpaint_engine.process(tight_roi, mask)
                        cleaned_tile[y1:y2, x1:x2] = local_cleaned
            
            if y_start == 0:
                result_padded[y_start:y_end, 0:w] = cleaned_tile
            else:
                act = min(overlap, y_end - y_start)
                alpha = np.linspace(0, 1, act).reshape(-1, 1, 1).astype(np.float32)
                base = result_padded[y_start : y_start+act, 0:w].astype(np.float32)
                new = cleaned_tile[0:act, 0:w].astype(np.float32)
                blend = (base * (1-alpha) + new * alpha).astype(np.uint8)
                result_padded[y_start : y_start+act, 0:w] = blend
                if y_start + act < y_end:
                    result_padded[y_start+act : y_end, 0:w] = cleaned_tile[act:, 0:w]
            
            if y_end >= padded_h: break
            y_start += stride
            del tile, ocr_ready, cleaned_tile
            gc.collect()

        final = result_padded[0:h, 0:w]
        return np.ascontiguousarray(final, dtype=np.uint8), cleaned_total_count
