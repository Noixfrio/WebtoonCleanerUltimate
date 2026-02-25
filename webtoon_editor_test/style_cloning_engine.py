import cv2
import numpy as np
import base64

class TextIsolation:
    """FASE 1 — ISOLAMENTO DO TEXTO"""
    
    @staticmethod
    def get_mask(img_bgr):
        # 1. Converter para escala LAB (L=Luminância, A, B=Canais de cor)
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # 2. Analisar luminância para identificar se o fundo é claro ou escuro
        h, w = l_channel.shape
        edge_brightness = (np.mean(l_channel[0,:]) + np.mean(l_channel[-1,:]) + 
                           np.mean(l_channel[:,0]) + np.mean(l_channel[:,-1])) / 4
        is_dark_bg = edge_brightness < 127
        
        # 3. Detectar bordas com Canny (usa luminância para maior precisão estrutural)
        edges = cv2.Canny(l_channel, 50, 150)
        
        # 4. Criar máscara binária básica via OTSU adaptativo
        if is_dark_bg:
            _, thresh = cv2.threshold(l_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, thresh = cv2.threshold(l_channel, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
        # Combinar Canny com Threshold para garantir bordas fechadas
        combined = cv2.bitwise_or(thresh, edges)
        
        # 5. Morfologia: Dilatação leve para conectar hastes e Abertura para remover ruído
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.dilate(combined, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask

class StyleExtraction:
    """FASE 2 — EXTRAÇÃO DE ESTRUTURA TIPOGRÁFICA"""
    
    @staticmethod
    def extract(img_bgr, mask):
        h, w = mask.shape
        text_indices = np.where(mask == 255)
        
        if text_indices[0].size < 10:
            return None
            
        text_pixels = img_bgr[text_indices]
        
        # --- 1. FILL (Preenchimento) ---
        fill_info = StyleExtraction._analyze_fill(img_bgr, mask, text_indices)
        
        # --- 2. STROKE (Contorno) ---
        stroke_info = StyleExtraction._analyze_stroke(img_bgr, mask)
        
        # --- 3. SHADOW (Sombra) ---
        shadow_info = StyleExtraction._analyze_shadow(img_bgr, mask)
        
        # --- 4. WEIGHT (Peso) ---
        weight_str = StyleExtraction._estimate_weight(mask)
        
        # --- 5. LETTER SPACING ---
        spacing = StyleExtraction._estimate_spacing(mask)
        
        return {
            "fill": fill_info,
            "stroke": stroke_info,
            "shadow": shadow_info,
            "weight": weight_str,
            "letter_spacing": spacing
        }

    @staticmethod
    def _analyze_fill(img, mask, indices):
        pixels = img[indices] # BGR
        
        # KMeans básico para encontrar as cores dominantes dentro do texto
        data = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(data, 2, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        y_min, y_max = np.min(indices[0]), np.max(indices[0])
        x_min, x_max = np.min(indices[1]), np.max(indices[1])
        dy, dx = y_max - y_min, x_max - x_min
        
        # Amostras de cor no topo/fundo/esquerda/direita
        mid_y = y_min + dy // 2
        mid_x = x_min + dx // 2
        
        # Simplificação: Detectar gradiente vertical (mais comum)
        top_px = img[indices[0] <= y_min + dy*0.25]
        bot_px = img[indices[0] >= y_max - dy*0.25]
        
        if top_px.size > 0 and bot_px.size > 0:
            c1 = np.mean(top_px, axis=0) # BGR
            c2 = np.mean(bot_px, axis=0)
            
            diff = np.linalg.norm(c1 - c2)
            if diff > 40:
                return {
                    "type": "gradient",
                    "colors": [StyleExtraction._bgr_to_hex(c1), StyleExtraction._bgr_to_hex(c2)],
                    "direction": "vertical"
                }

        # Sólido (média global ou centro do KMeans)
        avg_color = np.mean(pixels, axis=0)
        return {
            "type": "solid",
            "colors": [StyleExtraction._bgr_to_hex(avg_color)],
            "direction": "none"
        }

    @staticmethod
    def _analyze_stroke(img, mask):
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=1)
        edge_mask = cv2.subtract(dilated, mask)
        
        edge_pixels = img[edge_mask == 255]
        if edge_pixels.size > 5:
            avg_color = np.mean(edge_pixels, axis=0)
            text_pixels = img[mask == 255]
            text_avg = np.mean(text_pixels, axis=0)
            
            # Se a cor da borda for muito diferente do preenchimento, assumimos stroke
            if np.linalg.norm(avg_color - text_avg) > 50:
                return {"enabled": True, "width": 2, "color": StyleExtraction._bgr_to_hex(avg_color)}
        
        return {"enabled": False, "width": 0, "color": "#000000"}

    @staticmethod
    def _analyze_shadow(img, mask):
        dilated = cv2.dilate(mask, np.ones((3,3), np.uint8), iterations=1)
        
        for ox, oy in [(4,4), (3,3), (5,5)]:
            M = np.float32([[1, 0, ox], [0, 1, oy]])
            shifted_mask = cv2.warpAffine(mask, M, (mask.shape[1], mask.shape[0]))
            shadow_area = cv2.subtract(shifted_mask, dilated)
            
            if np.any(shadow_area == 255):
                sh_px = img[shadow_area == 255]
                if sh_px.size > 0:
                    avg_sh = np.mean(sh_px, axis=0)
                    if np.mean(avg_sh) < 130: # Sombra é geralmente escura
                        return {
                            "enabled": True, "offset_x": ox, "offset_y": oy, 
                            "blur": 4, "color": StyleExtraction._bgr_to_hex(avg_sh)
                        }
        
        return {"enabled": False, "offset_x": 0, "offset_y": 0, "blur": 0, "color": "#000000"}

    @staticmethod
    def _estimate_weight(mask):
        # Distance Transform calcula a distância de cada pixel branco até o pixel preto mais próximo
        # O valor máximo nos dá a metade da espessura da "haste" mais grossa
        dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        max_thick = np.max(dist)
        
        if max_thick < 3: return "light"
        if max_thick < 5: return "regular"
        if max_thick < 8: return "bold"
        return "heavy"

    @staticmethod
    def _estimate_spacing(mask):
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
        if num_labels < 3: return 0
        
        # Ordenar stats por X
        boxes = stats[1:] # Ignorar background (label 0)
        boxes = boxes[boxes[:, cv2.CC_STAT_LEFT].argsort()]
        
        spacings = []
        for i in range(len(boxes) - 1):
            gap = boxes[i+1][cv2.CC_STAT_LEFT] - (boxes[i][cv2.CC_STAT_LEFT] + boxes[i][cv2.CC_STAT_WIDTH])
            if -10 < gap < 50: # Evitar gaps gigantes de palavras separadas
                spacings.append(gap)
        
        return float(np.mean(spacings)) if spacings else 0

    @staticmethod
    def _bgr_to_hex(bgr):
        return '#%02x%02x%02x' % (int(bgr[2]), int(bgr[1]), int(bgr[0]))

class StyleCloningEngine:
    """FASE 3 — CRIAÇÃO DO MODELO DE ESTILO (Fachada Principal)"""
    
    @staticmethod
    def process(img_bgr):
        # 1. Isolamento
        mask = TextIsolation.get_mask(img_bgr)
        
        # 2. Extração
        extracted = StyleExtraction.extract(img_bgr, mask)
        
        if not extracted:
            return {"error": "Falha ao isolar texto"}
            
        return extracted
