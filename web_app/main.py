# web_app/main.py

import os
import io
import gc
import uuid
import zipfile
import asyncio
import numpy as np
import cv2
import time
import logging
import subprocess
import base64
import traceback
from pydantic import BaseModel

from fastapi import FastAPI, UploadFile, File, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from core.pipeline import MangaCleanerPipeline
from core.font_manager import WebtoonFontManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Webtoon Cleaner Ultimate")

# Ensure directories exist
templates = Jinja2Templates(directory="web_app/templates")
OUTPUT_DIR = "processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("assets/fonts", exist_ok=True)
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files for previews and processed images
app.mount("/processed", StaticFiles(directory=OUTPUT_DIR), name="processed")
app.mount("/assets/fonts", StaticFiles(directory="assets/fonts"), name="fonts")
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")

pipeline = MangaCleanerPipeline()
font_manager = WebtoonFontManager()

# In-memory session tracking
sessions = {}

class FrontendError(BaseModel):
    message: str
    trace: str

class OCRRequest(BaseModel):
    image: str

class UltraInpaintRequest(BaseModel):
    image: str # Base64 da imagem (recorte ou full)
    mask: str  # Base64 da máscara

class AutoCleanRequest(BaseModel):
    image: str # Base64 da imagem full

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{session}")
async def websocket_progress(websocket: WebSocket, session: str):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(0.5)
            if session in sessions:
                await websocket.send_json(sessions[session])
                if sessions[session]["status"] == "done":
                    break
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.post("/start")
async def start_process(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(OUTPUT_DIR, session_id)
    os.makedirs(session_folder, exist_ok=True)
    
    # Save files to disk immediately to prevent FastAPI from closing the UploadFile after the request ends
    input_paths = []
    for f in files:
        content = await f.read()
        input_file_path = os.path.join(session_folder, "input_" + f.filename)
        with open(input_file_path, "wb") as out_file:
            out_file.write(content)
        input_paths.append((input_file_path, f.filename))

    sessions[session_id] = {
        "total": len(files),
        "processed": 0,
        "status": "processing",
        "cancel": False,
        "files": [f.filename for f in files]
    }

    background_tasks.add_task(process_task, input_paths, session_id)

    return {"session": session_id}

async def process_task(input_paths, session_id):
    session_folder = os.path.join(OUTPUT_DIR, session_id)
    
    try:
        for file_path, filename in input_paths:
            if sessions.get(session_id, {}).get("cancel"):
                sessions[session_id]["status"] = "cancelled"
                logger.info(f"Session {session_id} cancelled.")
                return

            image = cv2.imread(file_path, cv2.IMREAD_COLOR)

            if image is None:
                logger.warning(f"Invalid image: {filename}")
                sessions[session_id]["processed"] += 1
                continue

            # Use a thread para não bloquear o Event Loop do FastAPI (que faria o WebSocket travar em "Aguardando...")
            result = await asyncio.to_thread(
                pipeline.process_webtoon_streaming,
                image, 
                job_id=f"ws_{session_id}_{filename}"
            )

            # Save preview pair
            before_path = os.path.join(session_folder, "before_" + filename)
            after_path = os.path.join(session_folder, "after_" + filename)

            cv2.imwrite(before_path, image)
            cv2.imwrite(after_path, result)

            sessions[session_id]["processed"] += 1
            
            # Explicit memory cleanup per file
            del image
            del result
            gc.collect()

        sessions[session_id]["status"] = "done"
        logger.info(f"Session {session_id} completed successfully.")

    except Exception as e:
        logger.exception(f"Error in background task {session_id}")
        if session_id in sessions:
            sessions[session_id]["status"] = f"error: {str(e)}"

@app.post("/cancel/{session}")
def cancel_process(session: str):
    if session in sessions:
        sessions[session]["cancel"] = True
        return {"status": "cancelling"}
    return {"status": "not_found"}

@app.get("/download/{session}")
def download_zip(session: str):
    session_folder = os.path.join(OUTPUT_DIR, session)
    if not os.path.exists(session_folder):
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename in os.listdir(session_folder):
            if filename.startswith("after_"):
                zip_file.write(
                    os.path.join(session_folder, filename),
                    arcname=filename.replace("after_", "")
                )

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=manga_clean_{session[:8]}.zip"}
    )

@app.get("/health")
def health():
    return {"status": "ultimate_active"}

@app.get("/api/fonts")
def list_fonts():
    try:
        from core.font_manager import WebtoonFontManager
        manager = WebtoonFontManager()
        return manager.list_fonts()
    except Exception as e:
        logger.error(f"Erro ao listar fontes: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/auto_clean_page")
async def api_auto_clean_page(req: AutoCleanRequest):
    try:
        # Decode image
        img_data = req.image.split(',')[1] if ',' in req.image else req.image
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JSONResponse(status_code=400, content={"error": "Imagem inválida"})

        # Executar Limpeza de Balões do Pipeline
        result = await asyncio.to_thread(
            pipeline.process_webtoon_streaming,
            img, 
            job_id=f"auto_clean_{uuid.uuid4().hex[:8]}"
        )
        
        # Encode result
        _, buffer = cv2.imencode('.png', result)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        
        return {"result": f"data:image/png;base64,{encoded_img}"}
        
    except Exception as e:
        logger.error(f"Erro Auto Clean Page: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/detect_balloons")
async def api_detect_balloons(req: AutoCleanRequest):
    try:
        # Decode image
        img_data = req.image.split(',')[1] if ',' in req.image else req.image
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JSONResponse(status_code=400, content={"error": "Imagem inválida"})

        # Preprocessar e detectar
        ocr_ready = pipeline._preprocess_for_ocr(img)
        results = pipeline.detector.ocr.readtext(ocr_ready)
        
        balloons = []
        for (bbox, text, prob) in results:
            if prob >= 0.05:
                balloons.append({
                    "box": [[float(p[0]), float(p[1])] for p in bbox],
                    "text": text,
                    "confidence": float(prob)
                })
        
        return {"balloons": balloons}
        
    except Exception as e:
        logger.error(f"Erro Detect Balloons: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/log_error")
def log_frontend_error(err: FrontendError):
    with open("frontend_errors.txt", "a") as f:
        f.write(f"FRONTEND ERROR: {err.message}\n{err.trace}\n---\n")
    return {"status": "logged"}

@app.post("/api/ocr_region")
def ocr_region(req: OCRRequest):
    try:
        from core.detector import TextDetector
        
        # O base64 vem como "data:image/png;base64,iVBORw0KGgo..."
        encoded_data = req.image.split(',')[1] if ',' in req.image else req.image
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JSONResponse(status_code=400, content={"error": "Imagem inválida para OCR"})

        detector = TextDetector()
        results = detector.detect(img, job_id="manual_ocr")
        
        # Concatena todos os blocos de texto encontrados
        text_lines = [box["text"] for box in results]
        combined_text = "\n".join(text_lines)

        return {"text": combined_text}
    except Exception as e:
        logger.error(f"Erro no OCR Manual: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

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
            logger.error("Falha ao decodificar imagem ou máscara")
            return JSONResponse(status_code=400, content={"error": "Dados de imagem ou máscara inválidos"})

        logger.info(f"Recebido pedido Ultra Inpaint: img={img.shape}, mask={mask_gray.shape}, mask_max={np.max(mask_gray)}")
        
        # Executar Inpaint Híbrido Avançado
        cleaned = await asyncio.to_thread(ultra_inpaint_area, img, mask_gray)
        logger.info("Processamento Ultra Inpaint concluído")
        
        # Encode result
        _, buffer = cv2.imencode('.png', cleaned)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        
        return {"result": f"data:image/png;base64,{encoded_img}"}
        
    except Exception as e:
        logger.error(f"Erro no Ultra Inpaint API: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# IMPORTAÇÃO DOS SERVIÇOS EXPERIMENTAIS (Se existirem)
@app.post("/api/import-font")
async def import_font(file: UploadFile = File(...)):
    if not (file.filename.endswith(".ttf") or file.filename.endswith(".otf")):
        return JSONResponse(status_code=400, content={"error": "Apenas .ttf e .otf são suportados"})
    
    # Save temp file to import
    temp_path = os.path.join("/tmp", file.filename)
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        font_manager.import_font(temp_path)
        return {"status": "success", "font": file.filename}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
