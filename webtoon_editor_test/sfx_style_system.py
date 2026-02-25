import cv2
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Tuple, List, Optional

class StyleExtractor:
    """
    Especialista em extração de propriedades cromáticas de onomatopeias.
    Utiliza OpenCV (cv2.kmeans) para isolar preenchimento e contorno.
    """

    @staticmethod
    def extract_colors(image_rgb: np.ndarray, mask_bin: np.ndarray) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Extrai as cores de preenchimento (Fill) e contorno (Stroke).
        
        Args:
            image_rgb: Imagem em formato NumPy (RGB).
            mask_bin: Máscara binária onde 255 representa o texto.
            
        Returns:
            Tupla contendo (RGB_Fill, RGB_Stroke).
        """
        if np.sum(mask_bin) == 0:
            raise ValueError("A máscara binária está vazia. Não há texto para analisar.")

        # --- 1. Extração de Fill (Preenchimento) ---
        fill_pixels = image_rgb[mask_bin == 255].astype(np.float32)
        
        # Usamos cv2.kmeans para evitar dependência do scikit-learn
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness, labels, centers = cv2.kmeans(fill_pixels, 2, None, criteria, 10, flags)
        
        # A cor predominante é do cluster com mais pontos
        counts = np.bincount(labels.flatten())
        dominant_fill = centers[np.argmax(counts)].astype(int)

        # --- 2. Extração de Stroke (Contorno) ---
        # Criamos uma "coroa" ao redor do texto dilatando a máscara e subtraindo a original
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(mask_bin, kernel, iterations=1)
        stroke_mask = cv2.subtract(dilated, mask_bin)
        
        stroke_pixels = image_rgb[stroke_mask == 255].astype(np.float32)
        
        if stroke_pixels.size > 0:
            compactness, labels, centers = cv2.kmeans(stroke_pixels, 2, None, criteria, 10, flags)
            # Pegamos a cor que mais difere do Fill
            diffs = [np.linalg.norm(c - dominant_fill) for c in centers]
            dominant_stroke = centers[np.argmax(diffs)].astype(int)
        else:
            dominant_stroke = (255, 255, 255) if np.mean(dominant_fill) < 127 else (0, 0, 0)

        return tuple(dominant_fill), tuple(dominant_stroke)

class SFXRenderer:
    """
    Renderizador tipográfico especializado em onomatopeias de mangá com distorção orgânica.
    """

    @staticmethod
    def render(
        text: str,
        fill_color: Tuple[int, int, int],
        stroke_color: Tuple[int, int, int],
        font_path: str,
        font_size: int = 100,
        stroke_width: int = 4,
        warp_intensity: float = 1.0,
        arch: float = 0.0,
        grad_enabled: bool = False,
        grad_color_2: Optional[Tuple[int, int, int]] = None,
        grad_direction: str = 'vertical',
        letter_spacing: float = 0.0,
        line_height: float = 1.0,
        shadow_enabled: bool = False,
        shadow_color: Tuple[int, int, int] = (0, 0, 0),
        shadow_blur: int = 5,
        shadow_offset: int = 5
    ) -> Image.Image:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        lines = text.split('\n')
        
        # Calcular bounding box total considerando espaçamento e altura de linha
        def get_line_size(line):
            if not line: return 0, 0
            # Soma das larguras dos caracteres + espaçamento
            w_acc = 0
            h_max = 0
            for char in line:
                bbox = font.getbbox(char)
                w_acc += (bbox[2] - bbox[0]) + letter_spacing
                h_max = max(h_max, bbox[3] - bbox[1])
            return w_acc - letter_spacing if w_acc > 0 else 0, h_max

        line_sizes = [get_line_size(l) for l in lines]
        w_text = max([s[0] for s in line_sizes]) if line_sizes else 0
        total_h_text = sum([s[1] for s in line_sizes]) * line_height
        
        # Margem generosa para garantir que deformações e SOMBRAS não cortem o texto
        padding = (stroke_width * 8) + int(150 * warp_intensity) + 300 + (shadow_blur * 2) + abs(shadow_offset)
        if abs(arch) > 0: padding += int(abs(arch) * total_h_text * 1.5)
        
        w, h = int(w_text + padding), int(total_h_text + padding)
        
        sfx_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sfx_img)
        
        def draw_text_custom(draw_obj, fill, is_stroke=False, offset=(0, 0), s_width=0):
            curr_y = (h - total_h_text) // 2 + offset[1]
            for i, line in enumerate(lines):
                line_w, line_h = line_sizes[i]
                curr_x = (w - line_w) // 2 + offset[0]
                
                for char in line:
                    char_bbox = font.getbbox(char)
                    char_w = char_bbox[2] - char_bbox[0]
                    
                    if is_stroke:
                        # Minkowski approximation para o stroke
                        for angle in range(0, 360, 45):
                            rad = math.radians(angle)
                            ox, oy = int(s_width * math.cos(rad)), int(s_width * math.sin(rad))
                            draw_obj.text((curr_x + ox, curr_y + oy), char, font=font, fill=fill)
                    else:
                        draw_obj.text((curr_x, curr_y), char, font=font, fill=fill)
                    
                    curr_x += char_w + letter_spacing
                
                curr_y += line_h * line_height

        # 1. SOMBRA (Shadow Layer) v28.6
        if shadow_enabled:
            shadow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            # Desenha a sombra com o offset aplicado
            draw_text_custom(shadow_draw, (shadow_color[0], shadow_color[1], shadow_color[2], 255), 
                            is_stroke=True, offset=(shadow_offset, shadow_offset), s_width=stroke_width)
            draw_text_custom(shadow_draw, (shadow_color[0], shadow_color[1], shadow_color[2], 255), 
                            offset=(shadow_offset, shadow_offset))
            
            if shadow_blur > 0:
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
            
            sfx_img.paste(shadow_layer, (0, 0), shadow_layer)

        # 2. Outer Stroke (Borda)
        draw = ImageDraw.Draw(sfx_img)
        if stroke_width > 0:
            draw_text_custom(draw, stroke_color, is_stroke=True, s_width=stroke_width)

        # 3. Preenchimento Principal (Sólido ou Degradê)
        if grad_enabled and grad_color_2:
            # Criar máscara do texto usando a mesma lógica de desenho caractere por caractere
            mask_img = Image.new('L', (w, h), 0)
            mask_draw = ImageDraw.Draw(mask_img)
            draw_text_custom(mask_draw, 255)
            
            grad_img = Image.new('RGB', (w, h), fill_color)
            grad_draw = ImageDraw.Draw(grad_img)
            
            c1, c2 = fill_color, grad_color_2
            if grad_direction == 'vertical':
                for y in range(h):
                    curr_color = tuple(int(c1[i] + (c2[i]-c1[i]) * y / h) for i in range(3))
                    grad_draw.line([(0, y), (w, y)], fill=curr_color)
            else:
                for x in range(w):
                    curr_color = tuple(int(c1[i] + (c2[i]-c1[i]) * x / w) for i in range(3))
                    grad_draw.line([(x, 0), (x, h)], fill=curr_color)
            
            sfx_img.paste(grad_img, (0, 0), mask_img)
        else:
            draw_text_custom(draw, fill_color)

        # 3. Distorção Orgânica (MESH Warp)
        return SFXRenderer._apply_advanced_warp(sfx_img, warp_intensity, arch)

    @staticmethod
    def _apply_advanced_warp(img: Image.Image, intensity: float = 1.0, arch: float = 0.0) -> Image.Image:
        w, h = img.size
        
        # Dividimos a imagem em fatias para criar uma malha curva (Arco)
        slices = 16
        slice_w = w / slices
        mesh = []
        
        # Intensidade da distorção orgânica (perfeição quebrada)
        base_jitter = 8 * intensity
        
        # Deslocamento máximo do Arco
        arch_max = arch * (h * 0.4) 
        
        # 1. Pré-calcular deslocamentos (offsets) para garantir continuidade entre fatias
        # Cada fatia i compartilha bordas com i-1 e i+1
        vertices_top = []
        vertices_bottom = []
        
        def get_y_offset(x_pos):
            rel_x = (x_pos / w) * 2 - 1 # -1 a 1
            return (1 - rel_x**2) * arch_max

        # Criar os pontos de controle (vértices) com jitter consistente
        for i in range(slices + 1):
            x = i * slice_w
            y_arch = get_y_offset(x)
            
            # Jitter consistente para este X
            jx = random.uniform(-base_jitter, base_jitter)
            jy_t = random.uniform(-base_jitter, base_jitter)
            jy_b = random.uniform(-base_jitter, base_jitter)
            
            vertices_top.append((x + jx, 0 - y_arch + jy_t))
            vertices_bottom.append((x + jx, h - y_arch + jy_b))
        
        # 2. Montar a malha usando os vértices compartilhados
        for i in range(slices):
            # Coordenadas da fatia na imagem original
            source_box = (int(i * slice_w), 0, int((i+1) * slice_w), h)
            
            # Pontos do QUAD: (TL, BL, BR, TR)
            # Pegamos os vértices pré-calculados para garantir que não haja "fendas"
            target_quad = [
                vertices_top[i],        # TL
                vertices_bottom[i],     # BL
                vertices_bottom[i+1],   # BR
                vertices_top[i+1]       # TR
            ]
            
            mesh.append((source_box, [p for sub in target_quad for p in sub]))
            
        return img.transform((w, h), Image.MESH, mesh, Image.BICUBIC)

if __name__ == "__main__":
    print("--- SFXStyleSystem: Teste de Execução ---")
    
    # Criar dados simulados (Texto Amarelo em Borda Azul)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = [255, 230, 50] # Amarelo
    img[25:30, 25:75] = [20, 50, 200]  # Borda Azul
    
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[30:70, 30:70] = 255
    
    try:
        ext = StyleExtractor(); fill, stroke = ext.extract_colors(img, mask)
        print(f"DNA SFX -> Fill: {fill}, Stroke: {stroke}")
        
        rend = SFXRenderer()
        # Nota: Usamos um caminho genérico ou o que estiver disponível
        output = rend.render("SFX!!", fill, stroke, "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 80, 5)
        output.save("sfx_dna_test.png")
        print("Sucesso! Resultado em 'sfx_dna_test.png'")
    except Exception as e:
        print(f"Erro no teste: {e}")
