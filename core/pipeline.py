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
        # Córtex Otimizado: Solução definitiva para fontes coloridas em fundos claros
        img = np.ascontiguousarray(tile, dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Blur Mediano arranca ruídos sem estragar bordas de letras finas
        blurred = cv2.medianBlur(gray, 3)
        
        # Adaptive Threshold com kernel Gigante (51px) para pegar centros de letras gordas e fontes azuis
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 51, 15
        )
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    def build_feathered_mask(self, shape: tuple, boxes: List[Dict], padding: int = 15) -> np.ndarray:
        h, w = shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        tile_area = h * w
        for box_item in boxes:
            pts = np.array(box_item["box"], dtype=np.int32)
            rx, ry, bw, bh = cv2.boundingRect(pts)
            # Area Guard 5%: Prevents inpainting geometric disasters (V20.0 Hardened)
            if (bw * bh) > (tile_area * 0.05): continue
            
            temp = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(temp, [pts], 255)
            mask = cv2.bitwise_or(mask, temp)
        
        # Super-Feathering: Une linhas separadas de texto dentro do mesmo balão
        if np.any(mask):
            # 1. Dilatação retangular pesada para conectar frases e engolir bordas da fonte
            k_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (padding*2+1, padding*2+1))
            mask = cv2.dilate(mask, k_connect)
            
            # 2. Suavização das bordas da máscara para o inpaint não criar quinas
            soft = cv2.GaussianBlur(mask, (15, 15), 0)
            _, mask = cv2.threshold(soft, 127, 255, cv2.THRESH_BINARY)
        return mask

    def process_webtoon_streaming(self, image: np.ndarray, job_id: str, threshold: float = 0.2) -> np.ndarray:
        """Architecture V20.0: Diamond Boss (Hardened Stability)."""
        raw_full = np.ascontiguousarray(image, dtype=np.uint8)
        h, w = raw_full.shape[:2]
        pad_h = 150
        img_padded = cv2.copyMakeBorder(raw_full, 0, pad_h, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        tile_h = 2048
        overlap = 120
        stride = tile_h - overlap
        result_padded = np.zeros(img_padded.shape, dtype=np.uint8)
        
        logger.info(f"V20.0 MISSION [Job: {job_id}] | Threshold {threshold}")

        y_start = 0
        padded_h = img_padded.shape[0]
        while y_start < padded_h:
            y_end = min(y_start + tile_h, padded_h)
            tile = np.array(img_padded[y_start:y_end, 0:w], copy=True, order='C')
            
            ocr_ready = self._preprocess_for_ocr(tile)
            results = self.detector.ocr.readtext(ocr_ready)
            
            boxes = [{"box": [[float(p_val[0]), float(p_val[1])] for p_val in b]} for (b, t, p) in results if p >= threshold]
            
            if boxes:
                # Aumentando o padding de 3 para 8 para garantir que a máscara engula os contornos das letras e apague tudo.
                mask = self.build_feathered_mask(tile.shape, boxes, padding=8)
                if DEBUG_MODE:
                    cv2.imwrite(f"{DEBUG_DIR}/{job_id}_t{y_start}_mask.png", mask)
                # Usando o core InpaintEngine nativo com NS e injeção de ruído para preencher o balão corretamente
                cleaned = self.inpaint_engine.process(tile, mask, job_id)
            else:
                cleaned = tile.copy()
            
            # Linear Alpha Blending (Restore Seam Perfection)
            if y_start == 0:
                result_padded[y_start:y_end, 0:w] = cleaned
            else:
                act = min(overlap, y_end - y_start)
                alpha = np.linspace(0, 1, act).reshape(-1, 1, 1).astype(np.float32)
                base = result_padded[y_start : y_start+act, 0:w].astype(np.float32)
                new = cleaned[0:act, 0:w].astype(np.float32)
                blend = (base * (1-alpha) + new * alpha).astype(np.uint8)
                result_padded[y_start : y_start+act, 0:w] = blend
                if y_start + act < y_end:
                    result_padded[y_start+act : y_end, 0:w] = cleaned[act:, 0:w]
            
            if y_end >= padded_h: break
            y_start += stride
            del tile, ocr_ready, cleaned
            gc.collect()

        final = result_padded[0:h, 0:w]
        return np.ascontiguousarray(final, dtype=np.uint8)
