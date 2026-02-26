import os
import io
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify

# Importando o pipeline híbrido local
try:
    # Try absolute imports first
    from lama_wrapper import lama_inpaint
    from frequency_refinement import FrequencySeparationPlugin
    from hybrid_pipeline import LamaFrequencyHybrid
except ImportError:
    # If absolute imports fail, try relative imports
    from .lama_wrapper import lama_inpaint
    from .frequency_refinement import FrequencySeparationPlugin
    from .hybrid_pipeline import LamaFrequencyHybrid

app = Flask(__name__)

# Configurações para carregar templates da pasta local
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        image_data = data.get('image')
        mask_data = data.get('mask')

        if not image_data or not mask_data:
            return jsonify({'error': 'Faltando imagem ou máscara'}), 400

        # Decodificar imagem original
        img_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Decodificar máscara
        # A máscara vem do canvas (RGBA), queremos apenas o canal Alpha ou converter para escala de cinza
        mask_bytes = base64.b64decode(mask_data.split(',')[1])
        nparr_mask = np.frombuffer(mask_bytes, np.uint8)
        mask_rgba = cv2.imdecode(nparr_mask, cv2.IMREAD_UNCHANGED)
        
        # Converter máscara para grayscale (255 para áreas a pintar, 0 para resto)
        # O canvas desenha em preto/colorido sobre transparente. 
        # Pegamos onde o Alpha > 0.
        if mask_rgba.shape[2] == 4:
            mask = mask_rgba[:, :, 3] 
        else:
            mask = cv2.cvtColor(mask_rgba, cv2.COLOR_BGR2GRAY)
        
        # Garantir que a máscara é binária (0 ou 255)
        _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)

        # Executar Pipeline Híbrido
        hybrid = LamaFrequencyHybrid()
        result = hybrid.process(img, mask)

        # Codificar resultado para base64
        _, buffer = cv2.imencode('.png', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({'result': f'data:image/png;base64,{result_base64}'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


