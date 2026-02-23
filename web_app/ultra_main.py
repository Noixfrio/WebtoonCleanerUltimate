# web_app/ultra_main.py

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import io
import gc
import uuid
import numpy as np
import cv2
import logging
import base64
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ultra IA Sandbox (Experimental)")

# Ensure directories exist
templates = Jinja2Templates(directory="web_app/templates")
OUTPUT_DIR = "processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("web_app/static", exist_ok=True)

# Mount static files
app.mount("/processed", StaticFiles(directory=OUTPUT_DIR), name="processed")
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")

class UltraInpaintRequest(BaseModel):
    image: str # Base64 da imagem
    mask: str  # Base64 da máscara
    use_frequency_separation: bool = True

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Usaremos um template dedicado para a porta 5001
    return templates.TemplateResponse("ultra_index.html", {"request": request})

@app.post("/api/ultra_inpaint")
async def api_ultra_inpaint(req: UltraInpaintRequest):
    try:
        from core.advanced_inpaint import ultra_inpaint_area
        
        # Decode image
        img_data = req.image.split(',')[1] if ',' in req.image else req.image
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Decode máscara
        mask_bytes = base64.b64decode(req.mask.split(',')[1])
        nparr_mask = np.frombuffer(mask_bytes, np.uint8)
        mask_raw = cv2.imdecode(nparr_mask, cv2.IMREAD_UNCHANGED)
        
        if len(mask_raw.shape) == 3 and mask_raw.shape[2] == 4:
            mask_gray = mask_raw[:, :, 3] # Canal Alpha
        elif len(mask_raw.shape) == 3:
            mask_gray = cv2.cvtColor(mask_raw, cv2.COLOR_BGR2GRAY)
        else:
            mask_gray = mask_raw
            
        # Garantir binário conforme original app.py
        _, mask_gray = cv2.threshold(mask_gray, 10, 255, cv2.THRESH_BINARY)

        if img is None or mask_gray is None:
            return JSONResponse(status_code=400, content={"error": "Dados inválidos"})

        logger.info(f"Ultra Inpaint Sandbox Request: {img.shape}")
        
        # Executar Inpaint Híbrido
        cleaned = await asyncio.to_thread(ultra_inpaint_area, img, mask_gray, req.use_frequency_separation)
        
        # Encode result
        _, buffer = cv2.imencode('.png', cleaned)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        
        return {"result": f"data:image/png;base64,{encoded_img}"}
        
    except Exception as e:
        logger.error(f"Erro Ultra IA Sandbox: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
