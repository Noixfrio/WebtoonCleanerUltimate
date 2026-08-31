import os
import numpy as np
import cv2
import onnxruntime as ort

def lama_inpaint(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Executa inpainting usando o modelo LaMa ONNX na CPU e valida as entradas conformes as especificações.
    """
    if image is None or mask is None:
        raise ValueError("Imagem ou máscara recebidas estão vazias.")
        
    if not np.any(mask):
        return image.copy()
        
    # Validar converter imagem para formato RGB com 3 canais
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("A imagem deve estar no formato RGB com 3 canais.")
        
    # Garantir que a máscara tenha apenas 1 canal
    if len(mask.shape) >= 3:
        if mask.shape[2] > 1:
            mask = mask[:, :, 0]
        else:
            mask = mask.squeeze()
            
    # Carregar modelo ONNX
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    model_path = os.path.join(project_root, 'assets', 'lama.onnx')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Erro: Modelo LaMa não existe no caminho {model_path}.")
        
    # Usar ONNX Runtime já disponível na CPU
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    
    # Identificar Bounding Box da máscara para recorte ROI
    y_indices, x_indices = np.where(mask > 0)
    if len(y_indices) == 0:
        return image.copy()
        
    y_min, y_max = np.min(y_indices), np.max(y_indices)
    x_min, x_max = np.min(x_indices), np.max(x_indices)
    
    # Adicionar padding proporcional para contexto da IA (ex: 20% do tamanho da área)
    H, W = image.shape[:2]
    h_mask, w_mask = y_max - y_min, x_max - x_min
    padding_h = int(h_mask * 0.3) + 20
    padding_w = int(w_mask * 0.3) + 20
    
    # Garantir que o ROI seja quadrado ou pelo menos equilibrado para o modelo 512x512
    roi_y_min = max(0, y_min - padding_h)
    roi_y_max = min(H, y_max + padding_h)
    roi_x_min = max(0, x_min - padding_w)
    roi_x_max = min(W, x_max + padding_w)
    
    # Extrair ROI
    roi_image = image[roi_y_min:roi_y_max, roi_x_min:roi_x_max].copy()
    roi_mask = mask[roi_y_min:roi_y_max, roi_x_min:roi_x_max].copy()
    
    H_roi, W_roi = roi_image.shape[:2]
    
    # Redimensionar apenas o ROI para o tamanho do modelo
    target_size = 512
    roi_resized = cv2.resize(roi_image, (target_size, target_size), interpolation=cv2.INTER_AREA)
    mask_resized = cv2.resize(roi_mask, (target_size, target_size), interpolation=cv2.INTER_NEAREST)

    # Converter para tensores
    img_tensor = roi_resized.astype(np.float32) / 255.0
    img_tensor = np.transpose(img_tensor, (2, 0, 1))
    img_tensor = np.expand_dims(img_tensor, 0)
    
    mask_tensor = mask_resized.astype(np.float32) / 255.0
    if len(mask_tensor.shape) == 2:
        mask_tensor = np.expand_dims(mask_tensor, 0)
    mask_tensor = np.expand_dims(mask_tensor, 0)
    
    input_names = [inp.name for inp in session.get_inputs()]
    ort_inputs = {
        input_names[0]: img_tensor,
        input_names[1]: mask_tensor
    }
    
    # Inferência
    ort_outs = session.run(None, ort_inputs)
    output_tensor = ort_outs[0]
    
    # Pós-processamento do ROI
    output_roi = np.clip(output_tensor[0], 0, 255).astype(np.uint8)
    output_roi = np.transpose(output_roi, (1, 2, 0))
    
    # Redimensionar ROI de volta para o tamanho do recorte original
    output_roi = cv2.resize(output_roi, (W_roi, H_roi), interpolation=cv2.INTER_CUBIC)
    
    # Integrar ROI de volta na imagem original
    result_image = image.copy()
    result_image[roi_y_min:roi_y_max, roi_x_min:roi_x_max] = output_roi
        
    return result_image
