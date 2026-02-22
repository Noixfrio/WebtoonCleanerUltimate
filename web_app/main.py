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

    sessions[session_id] = {
        "total": len(files),
        "processed": 0,
        "status": "processing",
        "cancel": False,
        "files": [f.filename for f in files]
    }

    background_tasks.add_task(process_task, files, session_id)

    return {"session": session_id}

async def process_task(files, session_id):
    session_folder = os.path.join(OUTPUT_DIR, session_id)
    
    try:
        for file in files:
            if sessions.get(session_id, {}).get("cancel"):
                sessions[session_id]["status"] = "cancelled"
                logger.info(f"Session {session_id} cancelled.")
                return

            contents = await file.read()
            np_arr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if image is None:
                logger.warning(f"Invalid image: {file.filename}")
                sessions[session_id]["processed"] += 1
                continue

            # Use the streaming pipeline for Webtoon length safety
            result = pipeline.process_webtoon_streaming(
                image, 
                job_id=f"ws_{session_id}_{file.filename}"
            )

            # Save preview pair
            before_path = os.path.join(session_folder, "before_" + file.filename)
            after_path = os.path.join(session_folder, "after_" + file.filename)

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
