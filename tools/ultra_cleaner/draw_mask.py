# Ferramenta Manual de Desenho de Máscara
# Não commitar (Uso local apenas)

import cv2
import numpy as np
import os
import sys

# Parâmetros de desenho
drawing = False
brush_size = 15

def draw_mask_callback(event, x, y, flags, param):
    """
    Callback para registrar ações do mouse e desenhar tanto na pre-visualização (vermelho)
    quanto na máscara de saída (branco sobre fundo preto).
    """
    global drawing
    
    image_display, mask = param
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        cv2.circle(image_display, (x, y), brush_size, (0, 0, 255), -1)
        cv2.circle(mask, (x, y), brush_size, 255, -1)
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.circle(image_display, (x, y), brush_size, (0, 0, 255), -1)
            cv2.circle(mask, (x, y), brush_size, 255, -1)
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(image_display, (x, y), brush_size, (0, 0, 255), -1)
        cv2.circle(mask, (x, y), brush_size, 255, -1)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, 'input.png')
    mask_path = os.path.join(current_dir, 'mask.png')
    
    if not os.path.exists(input_path):
        print(f"ERRO: A imagem 'input.png' não foi encontrada em: {current_dir}")
        sys.exit(1)
        
    # Carregar imagem original
    image = cv2.imread(input_path)
    if image is None:
        print("ERRO: Falha ao carregar 'input.png' pelo OpenCV.")
        sys.exit(1)
        
    # Criar uma cópia para exibição com o desenho em vermelho
    image_display = image.copy()
    
    # Criar a máscara em escala de cinza, vazia (preta) e do mesmo tamanho
    H, W = image.shape[:2]
    mask = np.zeros((H, W), dtype=np.uint8)
    
    window_name = 'Draw Mask - (S)alvar ou (ESC)Cancelar'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Associar o callback do mouse
    cv2.setMouseCallback(window_name, draw_mask_callback, param=(image_display, mask))
    
    print("--------------------------------------------------")
    print("      FERRAMENTA EXPERIMENTAL: DRAW MASK        ")
    print("--------------------------------------------------")
    print("[MOU_ESQUERDO] Clicar e arrastar para desenhar")
    print("[S]            Salvar máscara (mask.png) e sair")
    print("[ESC]          Sair sem salvar")
    print("--------------------------------------------------\\n")
    
    while True:
        cv2.imshow(window_name, image_display)
        
        # Pega a tecla e filtra bits superiores para compatibilidade cross-platform
        key = cv2.waitKey(20) & 0xFF
        
        if key == 27: # Tecla ESC
            print("[INFO] Fechado. Nenhuma máscara foi salva.")
            break
        elif key == ord('s') or key == ord('S'):
            cv2.imwrite(mask_path, mask)
            print(f"✅ Sucesso! Máscara salva em: {mask_path}")
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
