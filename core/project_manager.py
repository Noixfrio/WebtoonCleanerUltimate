import os
import json
import zipfile
import hashlib
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .project_models import ProjectMetadata, PageState

class ProjectManager:
    def __init__(self, workspace_parent: Optional[str] = None):
        self.workspace_parent = Path(workspace_parent) if workspace_parent else Path.home() / ".wcu" / "workspace"
        self.workspace_parent.mkdir(parents=True, exist_ok=True)
        self.current_project: Optional[ProjectMetadata] = None
        self.current_path: Optional[Path] = None
        self.active_workspace: Optional[Path] = None

    def calculate_checksum(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def validate_checksum(self, project: ProjectMetadata) -> bool:
        stored_checksum = project.checksum
        project.checksum = ""
        recalculated = self.calculate_checksum(project.model_dump_json())
        project.checksum = stored_checksum
        return stored_checksum == recalculated

    def create_project(self, name: str, path: str) -> ProjectMetadata:
        project = ProjectMetadata(project_name=name)
        self.current_project = project
        self.current_path = Path(path)
        
        # Criar espaço de trabalho temporário
        self.active_workspace = self.workspace_parent / f"proj_{project.id}"
        self._init_workspace_folders(self.active_workspace)
        
        return project

    def _init_workspace_folders(self, base_path: Path):
        folders = ['assets/original', 'assets/processed', 'assets/cache', 'thumbnails', 'autosave']
        for folder in folders:
            (base_path / folder).mkdir(parents=True, exist_ok=True)

    def add_page(self, source_path: str) -> PageState:
        if not self.current_project or not self.active_workspace:
            raise RuntimeError("Nenhum projeto ativo.")
        
        source = Path(source_path)
        page_id = f"pg_{uuid.uuid4().hex[:8]}"
        dest_filename = f"{page_id}_{source.name}"
        dest_path = self.active_workspace / "assets/original" / dest_filename
        
        # Copiar para o workspace (Lazy Loading - original fica no disco, cópia no workspace)
        shutil.copy2(source, dest_path)
        
        page = PageState(
            id=page_id,
            original_path=f"assets/original/{dest_filename}"
        )
        self.current_project.pages.append(page)
        self.mark_dirty()
        return page

    def save_project(self, target_path: Optional[str] = None) -> bool:
        if not self.current_project or not self.active_workspace:
            return False
        
        final_path = Path(target_path) if target_path else self.current_path
        if not final_path:
            return False

        # Status Update
        self.current_project.last_opened = datetime.now()
        
        # Checksum
        self.current_project.checksum = ""
        self.current_project.checksum = self.calculate_checksum(self.current_project.model_dump_json())

        # Atomic Save
        tmp_path = final_path.with_suffix('.wcu.tmp')
        
        try:
            with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 1. project.json
                zf.writestr('project.json', self.current_project.model_dump_json(indent=4))
                
                # 2. Assets (Original, Processed, Thumbnails)
                for root, _, files in os.walk(self.active_workspace):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.active_workspace)
                        # Ignorar pasta de autosave no arquivo principal? Geralmente sim,
                        # mas o usuário pediu dentro. Vou incluir.
                        zf.write(file_path, arcname)

            # Swap atômico
            if final_path.exists():
                # No Windows, rename falha se destino existir. No Linux não.
                # Para ser multiplataforma:
                backup_path = final_path.with_suffix('.wcu.bak')
                final_path.rename(backup_path)
                tmp_path.rename(final_path)
                backup_path.unlink()
            else:
                tmp_path.rename(final_path)
            
            self.current_path = final_path
            self.current_project.is_dirty = False
            return True
            
        except Exception as e:
            if tmp_path.exists(): tmp_path.unlink()
            raise e

    def autosave(self):
        if not self.current_project or not self.active_workspace: return
        
        # Incrementa contador (1 a 5)
        self.current_project.autosave_version = (self.current_project.autosave_version % 5) + 1
        name = f"autosave_{self.current_project.autosave_version:02d}.json"
        
        # Salvamos apenas o JSON do estado no workspace (rápido!)
        autosave_path = self.active_workspace / "autosave" / name
        with open(autosave_path, 'w') as f:
            f.write(self.current_project.model_dump_json(indent=4))
        
        # Opcionalmente, salvamos uma cópia completa .wcu de emergência se o projeto for pequeno
        # Mas para "Professional", o autosave de estado é o prioritário.

    def load_project(self, path: str) -> ProjectMetadata:
        load_path = Path(path)
        if not load_path.exists(): raise FileNotFoundError(path)

        # Limpar workspace anterior se necessário
        
        with zipfile.ZipFile(load_path, 'r') as zf:
            data = zf.read('project.json').decode('utf-8')
            project = ProjectMetadata.model_validate_json(data)
            
            if not self.validate_checksum(project):
                raise ValueError("Checksum inválido! Arquivo corrompido.")

            # Extrair para o workspace ativo
            self.active_workspace = self.workspace_parent / f"proj_{project.id}"
            zf.extractall(self.active_workspace)
            
            self.current_project = project
            self.current_path = load_path
            return project

    def recover_project(self, path: str) -> Optional[ProjectMetadata]:
        """Procura por .tmp ou autosaves para recuperar."""
        base_path = Path(path)
        tmp_path = base_path.with_suffix('.wcu.tmp')
        
        if tmp_path.exists():
            print(f"[RECOVERY] Arquivo temporário encontrado: {tmp_path}")
            # Podemos tentar renomear ou carregar dele
            return self.load_project(str(tmp_path))
        
        # Se falhar, poderíamos checar a pasta de autosave interna do ZIP (se conseguirmos ler o zip)
        return None

    def mark_dirty(self):
        if self.current_project:
            self.current_project.is_dirty = True
