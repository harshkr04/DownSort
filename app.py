import os
import sys
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from classifier import CATEGORY_META, PYPDF_AVAILABLE, PIL_AVAILABLE
from organizer import (
    scan_folder,
    execute_organization,
    undo_organization_session,
    load_history
)

app = FastAPI(title="DownSort API", description="Local Downloads & File Organizer")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DEFAULT_DOWNLOADS = os.path.normpath(os.path.expanduser(r"~\Downloads"))

# Request Models
class ScanRequest(BaseModel):
    folder_path: Optional[str] = None

class FileAction(BaseModel):
    filepath: str
    target_folder: str

class OrganizeRequest(BaseModel):
    folder_path: str
    actions: List[FileAction]
    mode: Optional[str] = "move"

class UndoRequest(BaseModel):
    session_id: str


@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "default_folder": DEFAULT_DOWNLOADS,
        "pypdf_available": PYPDF_AVAILABLE,
        "pil_available": PIL_AVAILABLE,
        "version": "1.0.0"
    }


@app.get("/api/categories")
def get_categories():
    categories = []
    for cat, meta in CATEGORY_META.items():
        categories.append({
            "id": cat,
            "label": meta["label"],
            "icon": meta["icon"],
            "color": meta["color"]
        })
    return {"categories": categories}


@app.post("/api/scan")
def scan_directory(req: ScanRequest):
    folder = req.folder_path or DEFAULT_DOWNLOADS
    folder = os.path.abspath(folder)

    if not os.path.exists(folder):
        raise HTTPException(status_code=400, detail=f"Directory does not exist: {folder}")
    if not os.path.isdir(folder):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder}")

    try:
        results = scan_folder(folder)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/organize")
def organize_files(req: OrganizeRequest):
    folder = os.path.abspath(req.folder_path)
    if not os.path.exists(folder):
        raise HTTPException(status_code=400, detail=f"Directory does not exist: {folder}")

    actions = [{"filepath": a.filepath, "target_folder": a.target_folder} for a in req.actions]
    try:
        result = execute_organization(folder, actions, mode=req.mode or "move")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def get_history():
    return {"history": load_history()}


@app.post("/api/undo")
def undo_session(req: UndoRequest):
    try:
        res = undo_organization_session(req.session_id)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Undo failed"))
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve static frontend files
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "DownSort API running. Frontend index.html not found."})
