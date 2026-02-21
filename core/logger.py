import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config.settings import settings

class DisciplinedJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "funcName": record.funcName,
            "message": record.getMessage(),
        }
        
        # job_id when applicable
        if hasattr(record, "job_id"):
            log_record["job_id"] = record.job_id
            
        # Optional extra info
        if hasattr(record, "extra"):
            log_record.update(record.extra)
            
        return json.dumps(log_record)

def setup_disciplined_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    if logger.handlers:
        return logger

    formatter = DisciplinedJSONFormatter()
    
    # Console for real-time visibility (still JSON)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # app.log (Rotating, 10MB)
    app_handler = RotatingFileHandler(
        settings.LOG_FILE, 
        maxBytes=10*1024*1024, 
        backupCount=5, 
        encoding="utf-8"
    )
    app_handler.setFormatter(formatter)
    logger.addHandler(app_handler)
    
    # error.log (Rotating, 10MB, >= WARNING)
    error_handler = RotatingFileHandler(
        settings.ERROR_LOG_FILE, 
        maxBytes=10*1024*1024, 
        backupCount=5, 
        encoding="utf-8"
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

logger = setup_disciplined_logger("manga_cleaner_v2")
