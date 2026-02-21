import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Mode
    DEBUG: bool = False
    WEB_MODE: bool = False
    
    # Memory Protection
    MAX_RAM_PERCENTAGE: float = 75.0  # Limit usage to 75% of available RAM
    SAFETY_MARGIN: float = 1.25       # 25% safety margin in formula
    MAX_IMAGE_PIXELS: int = 100_000_000  # 100MP limit
    
    # Inpaint & OCR Settings
    INPAINT_TIMEOUT: int = 60
    INPAINT_MAX_RETRIES: int = 3
    INPAINT_BACKOFF_FACTOR: float = 2.0
    OCR_CONFIDENCE_THRESHOLD: float = 0.5
    OCR_LANG: str = "ch"
    ENABLE_GPU: bool = False
    
    # Webtoon & General Pipeline
    TILE_OVERLAP: int = 64
    TILE_HEIGHT: int = 2048
    TILE_SEAM_THRESHOLD: float = 15.0
    
    # Web Specific
    WEB_MAX_UPLOAD_MB: int = 20
    
    # Logging
    LOG_FILE: str = "app.log"
    ERROR_LOG_FILE: str = "error.log"
    LOG_LEVEL: str = "INFO"

    # Pydantic Configuration to support .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
