import os
import sys
import time
import cv2
import numpy as np

# Adicionar pasta pai ao sys.path temporariamente se precisar de absolute import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experimental_lama_frequency_test.hybrid_pipeline import LamaFrequencyHybrid

def main():
    print("--------------------------------------------------")
    print(" TESTE EXPERIMENTAL: LaMa + Frequency Refinement  ")
    print("--------------------------------------------------\\n")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, 'input.png')
    mask_path = os.path.join(current_dir, 'mask.png')
    output_path = os.path.join(current_dir, 'output_test.png')

    # Validação Básica
    if not os.path.exists(input_path):
        print(f"ERRO: input.png não encontrado no diretório: {current_dir}", file=sys.stderr)
        return
        
    if not os.path.exists(mask_path):
        print(f"ERRO: mask.png não encontrado no diretório: {current_dir}", file=sys.stderr)
        return

    # Carregamento
    image = cv2.imread(input_path, cv2.IMREAD_COLOR)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if image is None or mask is None:
        print("ERRO: Imagens não puderam ser lidas pelo OpenCV.", file=sys.stderr)
        return

    # Calcular tamanho da ROI
    y_idx, x_idx = np.where(mask > 0)
    if len(y_idx) > 0:
        roi_h = np.max(y_idx) - np.min(y_idx)
        roi_w = np.max(x_idx) - np.min(x_idx)
        roi_size = f"{roi_w}x{roi_h} pixels"
    else:
        roi_size = "0x0 (Máscara vaiza)"

    print(f"[INFO] Resolução da Imagem: {image.shape}")
    print(f"[INFO] Tamanho da ROI Alvo: {roi_size}\\n")

    # Parâmetros padrão do plugin
    freq_params = {
        'blur_kernel': 21,
        'texture_strength': 1.2,
        'feather_radius': 5,
        'padding': 15
    }
    print("[INFO] Parâmetros de Refinamento (Frequency Separation):")
    for k, v in freq_params.items():
        print(f"       {k} = {v}")
    print()

    # Modelos tipicamente usam RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pipeline = LamaFrequencyHybrid(**freq_params)

    # Execução e marcação de tempo
    start_time = time.time()
    try:
        resultado_rgb = pipeline.process(image_rgb, mask)
    except Exception as e:
        print(f"\\n[ERRO FATAL] Falha durante a execução do pipeline: {e}", file=sys.stderr)
        return
    end_time = time.time()

    total_time = end_time - start_time
    
    # Salvar output
    resultado_bgr = cv2.cvtColor(resultado_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, resultado_bgr)

    print("\\n--------------------------------------------------")
    print("                 RESULTADOS                       ")
    print("--------------------------------------------------")
    print(f"✅ Execução Finalizada")
    print(f"⏱️ Tempo total (LaMa ONNX + Plugin) : {total_time:.3f} segundos")
    print(f"💾 Arquivo salvo em                 : {output_path}")

if __name__ == "__main__":
    main()
