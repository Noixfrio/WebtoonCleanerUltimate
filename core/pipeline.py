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
        # Binarizar ou Inverter a imagem destrói a detecção neural!
        img = np.ascontiguousarray(tile, dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apenas um CLAHE leve para dar contraste nas letras claras
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

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
            # Apenas uma dilatação suave para engolir anti-aliasing e imperfeições da fonte OCR
            k_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (padding, padding))
            mask = cv2.dilate(mask, k_connect)
        return mask

    def process_webtoon_streaming(self, image: np.ndarray, job_id: str, threshold: float = 0.05) -> np.ndarray:
        """Architecture V21.0: Balloon-Aware Local Cleaner."""
        raw_full = np.ascontiguousarray(image, dtype=np.uint8)
        h, w = raw_full.shape[:2]
        pad_h = 150
        img_padded = cv2.copyMakeBorder(raw_full, 0, pad_h, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        tile_h = 2048
        overlap = 120
        stride = tile_h - overlap
        result_padded = np.zeros(img_padded.shape, dtype=np.uint8)
        
        logger.info(f"V21.0 BALLOON-AWARE MISSION [Job: {job_id}] | Threshold {threshold}")

        y_start = 0
        padded_h = img_padded.shape[0]
        while y_start < padded_h:
            y_end = min(y_start + tile_h, padded_h)
            tile = np.array(img_padded[y_start:y_end, 0:w], copy=True, order='C')
            
            ocr_ready = self._preprocess_for_ocr(tile)
            results = self.detector.ocr.readtext(ocr_ready)
            
            # Abaixamos o threshold nativo pra 0.05 porque nós mesmos validaremos se é balão ou não!
            boxes = [{"box": [[float(p_val[0]), float(p_val[1])] for p_val in b]} for (b, t, p) in results if p >= threshold]
            
            cleaned_tile = tile.copy()
            if boxes:
                for box_item in boxes:
                    pts = np.array(box_item["box"], dtype=np.int32)
                    rx, ry, bw, bh = cv2.boundingRect(pts)
                    rx, ry = max(0, rx), max(0, ry)
                    
                    # Ignorar se o box ocupar mais de 15% da imagem inteira (falhas do OCR ou sons gigantes)
                    if (bw * bh) > (tile.shape[0] * tile.shape[1] * 0.15): continue
                    
                    # 1. Expandir a caixa pra pegar o contexto DO FUNDO do box
                    bg_pad = 12
                    bg_x1 = max(0, rx - bg_pad)
                    bg_y1 = max(0, ry - bg_pad)
                    bg_x2 = min(w, rx + bw + bg_pad)
                    bg_y2 = min(tile.shape[0], ry + bh + bg_pad)
                    
                    roi_bg = cleaned_tile[bg_y1:bg_y2, bg_x1:bg_x2]
                    if roi_bg.size == 0: continue
                    
                    # Pegar apenas a Borda "moldura" do box
                    top = roi_bg[0, :]
                    bottom = roi_bg[-1, :]
                    left = roi_bg[:, 0]
                    right = roi_bg[:, -1]
                    borders = np.concatenate([top, bottom, left, right], axis=0).astype(np.int32)
                    
                    if len(borders) == 0: continue
                    
                    # Descobrir a cor dominante da Borda (Cor do Balão)
                    median_c = np.median(borders, axis=0).astype(np.int32)
                    diffs = np.sum(np.abs(borders - median_c), axis=-1)
                    
                    # Consideramos "Fundo Controlado" (Balão) se 65% da borda tiver cor quase igual à mediana
                    uniform_ratio = np.mean(diffs < 60)
                    
                    if uniform_ratio > 0.65:
                        # Achamos um Balão Uniforme! (Exclui arte de fundo caótica)
                        pad = 5
                        x1 = max(0, rx - pad)
                        y1 = max(0, ry - pad)
                        x2 = min(w, rx + bw + pad)
                        y2 = min(tile.shape[0], ry + bh + pad)
                        
                        tight_roi = cleaned_tile[y1:y2, x1:x2].copy()
                        bg_luminance = int(median_c[0]) + int(median_c[1]) + int(median_c[2])
                        roi_luminance = np.sum(tight_roi.astype(np.int32), axis=-1)
                        
                        # Isolar apenas as letras usando a luminância do balão como ref!
                        if bg_luminance > 380: # Balão Claro
                            mask = (roi_luminance < bg_luminance - 70).astype(np.uint8) * 255
                        else: # Balão Escuro
                            mask = (roi_luminance > bg_luminance + 70).astype(np.uint8) * 255
                            
                        # Dilatação leve de segurança para cobrir blur da fonte
                        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                        mask = cv2.dilate(mask, kernel, iterations=1)
                        
                        # Inpaint milimétrico usando Telea apenas na zona LOCAL (não borra nada em volta!)
                        local_cleaned = cv2.inpaint(tight_roi, mask, 5, cv2.INPAINT_TELEA)
                        cleaned_tile[y1:y2, x1:x2] = local_cleaned
            
            # Blending Costura Padrão
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
        return np.ascontiguousarray(final, dtype=np.uint8)
