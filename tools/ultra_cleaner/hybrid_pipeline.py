import numpy as np
from lama_wrapper import lama_inpaint
from frequency_refinement import FrequencySeparationPlugin

class LamaFrequencyHybrid:
    """
    Pipeline híbrido combinando LaMa ONNX Inpainting com Refinamento de Frequência.
    """
    
    def __init__(self, **freq_params):
        # Instanciar o plugin de frequência com os parâmetros fornecidos ou padrões
        self.freq_plugin = FrequencySeparationPlugin(**freq_params)

    def process(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Executa os dois passos do pipeline de forma sequencial, sem efeitos colaterais.
        """
        # Checar condição de máscara vazia/inexistente
        if mask is None or not np.any(mask):
            return image if image is not None else None
            
        # Step 1: Inferência com modelo LaMa Onnx
        step1_result = lama_inpaint(image, mask)
        
        # Step 2: Refinamento de Textura (Frequency Separation)
        step2_result = self.freq_plugin.process(step1_result, mask)
        
        return step2_result
