import sys
import os
from pathlib import Path

def get_resource_path(relative_path):
    """ Resolve caminhos para recursos, verificando locais locais e empacotados. """
    if getattr(sys, 'frozen', False):
        # No PyInstaller, os dados ficam no mesmo diretório do executável ou em _MEIPASS
        base_path = Path(sys.executable).parent
        
        # Verificar se estamos no modo Directory (pasta dist/ToonixEditor)
        # onde os arquivos ficam ao lado do executável
        candidate = base_path / relative_path
        if candidate.exists():
            return candidate
            
        # Fallback para _MEIPASS (caso mude para Onefile no futuro)
        if hasattr(sys, '_MEIPASS'):
            candidate = Path(sys._MEIPASS) / relative_path
            if candidate.exists():
                return candidate
    
    # Modo desenvolvimento
    base_path = Path(__file__).parent.parent
    return base_path / relative_path
