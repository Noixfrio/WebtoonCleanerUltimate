from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class ProjectVersion(BaseModel):
    app: str = "2.5.0"
    format: str = "1.0"

class PageState(BaseModel):
    id: str
    original_path: str
    processed_path: Optional[str] = None
    konva_state: Dict[str, Any] = Field(default_factory=dict)
    ia_applied: bool = False
    history: List[Dict[str, Any]] = Field(default_factory=list)
    checksum: Optional[str] = None

class ProjectMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    versions: ProjectVersion = Field(default_factory=ProjectVersion)
    created_at: datetime = Field(default_factory=datetime.now)
    last_opened: datetime = Field(default_factory=datetime.now)
    is_dirty: bool = False
    autosave_version: int = 0
    checksum: str = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    pages: List[PageState] = Field(default_factory=list)
