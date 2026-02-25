from flask import Flask, render_template, send_from_directory, request, jsonify
import cv2
import numpy as np
import base64
import os
import io
import datetime
from style_cloning_engine import StyleCloningEngine
from sfx_style_system import SFXRenderer
import easyocr
import pytesseract
from PIL import Image

import json

app = Flask(__name__)

PRESETS_FILE = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/presets.json"

def load_presets_from_file():
    try:
        if os.path.exists(PRESETS_FILE):
            with open(PRESETS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar presets: {e}")
    return []

def save_presets_to_file(presets):
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump(presets, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar presets: {e}")

@app.route('/api/list_presets')
def list_presets():
    return jsonify(load_presets_from_file())

@app.route('/api/save_preset', methods=['POST'])
def save_preset():
    try:
        new_preset = request.json
        if not new_preset or 'name' not in new_preset:
            return jsonify({"error": "Dados inválidos"}), 400
        
        presets = load_presets_from_file()
        new_preset['id'] = new_preset.get('name', 'preset').lower().replace(' ', '_') + "_" + str(len(presets))
        presets.append(new_preset)
        save_presets_to_file(presets)
        
        return jsonify({"success": True, "preset": new_preset})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_debug(msg):
    with open("debug_style.txt", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {msg}\n")

@app.route('/fonts/<path:filename>')
def serve_font(filename):
    font_dir = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/Fontes - mangá"
    return send_from_directory(font_dir, filename)

@app.route('/api/list_fonts')
def list_fonts():
    font_dir = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/Fontes - mangá"
    categories = {}
    for root, dirs, files in os.walk(font_dir):
        category_name = os.path.basename(root)
        if root == font_dir: category_name = "Geral"
        font_files = [f for f in files if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2'))]
        if font_files:
            rel_dir = os.path.relpath(root, font_dir)
            if rel_dir == ".": rel_dir = ""
            if category_name not in categories: categories[category_name] = []
            for f in font_files:
                categories[category_name].append({"name": f, "path": os.path.join(rel_dir, f)})
    return {"categories": categories}

@app.route('/api/render_sfx', methods=['POST'])
def render_sfx():
    try:
        data = request.json
        text = data.get('text', '')
        fill = data.get('fill', '#ff0000')
        stroke = data.get('stroke', '#000000')
        s_width = int(data.get('stroke_width', 4))
        w_intensity = float(data.get('warp_intensity', 1.0))
        arch_val = float(data.get('arch', 0.0))
        l_spacing = float(data.get('letter_spacing', 0.0))
        l_height = float(data.get('line_height', 1.0))
        f_weight = data.get('font_weight', 'normal')
        f_size = int(data.get('font_size', 120))
        
        # Degradê
        grad_enabled = data.get('grad_enabled', False)
        grad_color_1 = data.get('grad_color_1', fill)
        grad_color_2 = data.get('grad_color_2', fill)
        grad_direction = data.get('grad_direction', 'vertical')
        
        # Sombra (v28.6)
        s_enabled = data.get('shadow_enabled', False)
        s_blur = int(data.get('shadow_blur', 5))
        s_offset = int(data.get('shadow_offset', 5))
        s_color_hex = data.get('shadow_color', '#000000')

        # Converter hex para RGB
        def hex_to_rgb(h): 
            h = h.lstrip('#')
            if len(h) == 3: h = ''.join([c*2 for c in h])
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Caminho da fonte (usar a selecionada)
        font_family = data.get('font_family', 'Arial')
        font_path = None
        
        print(f"DEBUG DNA: Renderizando '{text}' ({f_weight})")
        
        # Localizar arquivo da fonte (Busca inteligente por Peso)
        font_dir = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/Fontes - mangá"
        search_terms = []
        if f_weight in ['bold', '700']: search_terms.append('bold')
        elif f_weight in ['900', 'heavy', 'black']: search_terms.extend(['black', 'heavy', 'extrabold', 'bold'])
        elif f_weight in ['300', 'light', 'thin']: search_terms.extend(['light', 'thin'])

        # Prioritização: 
        # 1. Deve conter o nome da família
        # 2. Tentar achar o peso específico solicitado
        # 3. Se não houver peso, pega o primeiro que bater com a família
        best_match = None
        for root, dirs, files in os.walk(font_dir):
            for f in files:
                f_lower = f.lower()
                if font_family.lower() in f_lower:
                    # Se não temos nada ainda, essa é a base
                    if not best_match: best_match = os.path.join(root, f)
                    
                    # Se houver termos de busca de peso, tenta o match mais específico
                    if search_terms and any(term in f_lower for term in search_terms):
                        font_path = os.path.join(root, f)
                        break
            if font_path: break
        
        if not font_path: font_path = best_match

        if not font_path:
            # Fallback absoluto
            for root, dirs, files in os.walk(font_dir):
                for f in files:
                    if f.lower().endswith(('.ttf', '.otf')):
                        font_path = os.path.join(root, f)
                        break
                if font_path: break

        img_pil = SFXRenderer.render(
            text=text,
            fill_color=hex_to_rgb(grad_color_1 if grad_enabled else fill),
            stroke_color=hex_to_rgb(stroke),
            font_path=font_path or "Arial",
            font_size=f_size,
            stroke_width=s_width,
            warp_intensity=w_intensity,
            arch=arch_val,
            grad_enabled=grad_enabled,
            grad_color_2=hex_to_rgb(grad_color_2),
            grad_direction=grad_direction,
            letter_spacing=l_spacing,
            line_height=l_height,
            shadow_enabled=s_enabled,
            shadow_color=hex_to_rgb(s_color_hex),
            shadow_blur=s_blur,
            shadow_offset=s_offset
        )
        
        # Converter PIL para base64
        buffered = io.BytesIO()
        img_pil.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        print(f"DEBUG DNA: SFX Gerado com sucesso (Arch: {arch_val})")
        return jsonify({"image": f"data:image/png;base64,{img_str}"})
    except Exception as e:
        print(f"ERRO FATAL RENDER SFX: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract_style', methods=['POST'])
def extract_style():
    try:
        data = request.json
        image_b64 = data.get('image')
        if not image_b64: return jsonify({"error": "Sem imagem"}), 400

        header, encoded = image_b64.split(",", 1)
        img_data = base64.b64decode(encoded)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None: return jsonify({"error": "Erro ao ler imagem"}), 400

        # Usar o novo motor de clonagem de estilo
        style_model = StyleCloningEngine.process(img)
        
        if "error" in style_model:
            return jsonify(style_model), 404
            
        log_debug(f"Style Model Extraído: {style_model}")
        return jsonify(style_model)
    except Exception as e:
        log_debug(f"ERRO CRÍTICO NA EXTRAÇÃO: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

# Inicialização robusta do motor OCR
_ocr_reader = None

def init_ocr():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            print(">>> [INIT] Carregando motor EasyOCR (EN, PT)...")
            # Japanese is not compatible with PT in the same reader.
            _ocr_reader = easyocr.Reader(['en', 'pt'], gpu=False) 
            print(">>> [INIT] Motor EasyOCR pronto!")
        except Exception as e:
            print(f">>> [ERROR] Falha crítica ao iniciar OCR: {e}")
    return _ocr_reader

# O OCR será inicializado apenas na primeira vez que for usado (Lazy Loading)
def get_ocr_reader():
    return init_ocr()

@app.route('/extract', methods=['POST'])
def extract_text():
    """
    Novo endpoint OCR usando Pytesseract solicitado pelo usuário (v27.2)
    """
    try:
        # 1. Validar se o arquivo foi enviado (Sênior Spec)
        if 'image' not in request.files:
            print("OCR ERROR: Nenhuma imagem enviada no Form-Data")
            return jsonify({"error": "Nenhuma imagem enviada. Use a chave 'image'."}), 400

        file = request.files['image']

        # 2. Validar se o arquivo não está vazio
        if file.filename == '':
            print("OCR ERROR: Nome do arquivo vazio")
            return jsonify({"error": "Arquivo vazio"}), 400

        # 3. Validar Formato Suportado
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
             print(f"OCR ERROR: Formato {ext} não suportado")
             return jsonify({"error": f"Formato {ext} não suportado. Use PNG, JPG ou BMP."}), 400

        # 4. Abrir imagem via PIL e garantir modo RGB
        try:
            image_pil = Image.open(file.stream).convert('RGB')
            
            # Salvar original para comparação (DadosHD tem espaço)
            orig_debug_path = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/debug_ocr_orig.png"
            image_pil.save(orig_debug_path)

            # --- UPGRADE v27.9: Pré-processamento com OpenCV para Tesseract ---
            open_cv_image = np.array(image_pil) 
            # RGB to BGR
            open_cv_image = cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
            
            # Grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Threshold binário simples (Preto no Branco para Tesseract)
            _, processed = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
            
            # Se o thresholding apagar tudo (imagem 100% branca ou preta), usa a cinza direto
            if np.mean(processed) > 250 or np.mean(processed) < 5:
                processed = gray

            # Salvar dump para debug
            debug_path = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/debug_ocr_processed.png"
            cv2.imwrite(debug_path, processed)
            
            image_final = Image.fromarray(processed)
            
        except Exception as e:
            print(f"OCR ERROR: Falha no processamento de imagem: {e}")
            # Se falhar o processamento, tenta usar a original mesmo
            image_final = image_pil
        
        print(f"\n[DEBUG OCR TESSERACT] Lendo: {file.filename} | Tamanho: {image_final.size}")

        # 5. Executar OCR com Tesseract (Vários PSMs se necessário)
        # PSM 6: Uniform block of text
        # PSM 11: Sparse text. Find as much text as possible in no particular order.
        text = pytesseract.image_to_string(
            image_final,
            lang="eng+por",
            config="--oem 3 --psm 6"
        )

        # Fallback para PSM 11 (Melhor para textos únicos ou isolados)
        if not text.strip():
            text = pytesseract.image_to_string(image_final, lang="eng+por", config="--oem 3 --psm 11")

        # Fallback para a imagem ORIGINAL se a processada der vazio
        if not text.strip():
            text = pytesseract.image_to_string(image_pil, lang="eng+por", config="--oem 3 --psm 6")

        # Logar resultado no terminal (Sênior Logger)
        print("--- TEXTO EXTRAÍDO ---")
        print(f"'{text.strip()}'" if text.strip() else "[NENHUM TEXTO DETECTADO]")
        print("-----------------------\n")

        return jsonify({"text": text.strip()})

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print("\n!!! ERRO CRÍTICO NO OCR /EXTRACT !!!")
        print(err_msg)
        return jsonify({"error": f"Falha interna no motor OCR: {str(e)}"}), 500

@app.route('/api/ocr', methods=['POST', 'OPTIONS'])
def perform_ocr():
    # CORS Manual para suportar chamadas de outras portas
    if request.method == 'OPTIONS':
        resp = jsonify({})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        resp.headers.add('Access-Control-Allow-Methods', 'POST')
        return resp

    log_file = "/home/sam/DadosHD/manga_cleaner_v2/ocr_debug.log"
    with open(log_file, "a", encoding="utf-8") as f:
        try:
            import time
            import traceback
            start_time = time.time()
            data = request.json
            img_b64 = data.get('image')
            if not img_b64:
                return jsonify({'error': 'Nenhuma imagem fornecida'}), 400

            # Decodificar imagem
            header, encoded = img_b64.split(",", 1)
            img_data = base64.b64decode(encoded)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            f.write(f"[{time.ctime()}] DEBUG: Imagem recebida {img.shape}\n")

            # Usar Reader Global (Singleton)
            reader = get_ocr_reader()
            results = reader.readtext(img)
            
            f.write(f"[{time.ctime()}] DEBUG: Detectados {len(results)} fragmentos\n")
            text_lines = []
            for res in results:
                f.write(f"  > [{res[2]:.2f}] {res[1]}\n")
                text_lines.append(res[1])

            text_found = " ".join(text_lines)
            elapsed = time.time() - start_time
            f.write(f"[{time.ctime()}] DEBUG: Finalizado em {elapsed:.2f}s. Texto total: '{text_found}'\n")
            
            resp = jsonify({'text': text_found.strip()})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp
        except Exception as e:
            err_msg = traceback.format_exc()
            f.write(f"[{time.ctime()}] CRITICAL ERROR: {err_msg}\n")
            resp = jsonify({'error': str(e)})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp, 500

def check_tesseract():
    """Validação Sênior de Dependências OCR (v27.2)"""
    print("\n" + "="*50)
    print("VERIFICAÇÃO DE AMBIENTE OCR (Pytesseract)")
    print("="*50)
    
    # 1. Verificar Binário
    try:
        # Configuração para Windows (Descomente se necessário)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        version = pytesseract.get_tesseract_version()
        print(f"[OK] Tesseract encontrado: v{version}")
    except pytesseract.TesseractNotFoundError:
        print("[ALERTA CRÍTICO] Motor Tesseract-OCR NÃO encontrado!")
        print("   -> Linux: Execute 'sudo apt install tesseract-ocr tesseract-ocr-por'")
        print("   -> Windows: Instale e configure pytesseract.pytesseract.tesseract_cmd")
    except Exception as e:
        print(f"[ERRO] Falha técnica ao verificar Tesseract: {e}")

    # 2. Verificar Pacotes de Idiomas (eng, por)
    try:
        langs = pytesseract.get_languages()
        print(f"[INFO] Idiomas disponíveis no motor: {langs}")
        if 'por' not in langs:
             print("[AVISO] 'por.traineddata' (Português) ausente!")
        if 'eng' not in langs:
             print("[AVISO] 'eng.traineddata' (Inglês) ausente!")
    except Exception as e:
        print(f"[!] Não foi possível listar idiomas: {e}")
    print("="*50 + "\n")

if __name__ == '__main__':
    # Rodar diagnóstico sênior
    check_tesseract()
    
    # Iniciar com DEBUG ATIVO conforme solicitado
    print("Servidor Webtoon Editor Backend (v27.2) Iniciando nas portas 5002...")
    app.run(debug=True, port=5002, host='0.0.0.0')
