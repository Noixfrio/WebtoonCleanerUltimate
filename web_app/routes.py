import cv2
import numpy as np
import io
import os
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import StreamingResponse
from core.pipeline import MangaCleanerPipeline
from core.exceptions import InvalidImageError
from core.logger import logger
from werkzeug.utils import secure_filename

router = APIRouter()
pipeline = MangaCleanerPipeline()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB limit for Web

def validate_file(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidImageError(f"Extension {ext} not allowed. Supported: {ALLOWED_EXTENSIONS}")
    
    # We can't easily check size without reading, but FastAPI can be configured
    # Here we'll do a basic check after reading if needed

@router.post("/clean")
async def clean_image_endpoint(request: Request, file: UploadFile = File(...)):
    job_id = getattr(request.state, "job_id", "unknown")
    logger.info(f"Received clean request for {file.filename} [Job: {job_id}]")
    
    validate_file(file)
    
    # Read file into memory
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise InvalidImageError(f"File size exceeds limit of {MAX_FILE_SIZE / 1024**2}MB")
    
    # Convert to numpy array
    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise InvalidImageError("Could not decode image.")
        
    # Process through pipeline
    try:
        cleaned_image = pipeline.clean_image(image, job_id=job_id)
        
        # Encode back to PNG
        _, encoded_img = cv2.imencode(".png", cleaned_image)
        
        return StreamingResponse(
            io.BytesIO(encoded_img.tobytes()),
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="cleaned_{secure_filename(file.filename)}"'}
        )
    except Exception as e:
        # Pipeline errors are caught by middleware but we can log specific context here
        logger.error(f"Endpoint processing failure [Job: {job_id}]: {str(e)}")
        raise
