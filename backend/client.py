# client.py
# Connect FE (Vue) to Python (FastAPI)

from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import server
import sys
import uvicorn

app = FastAPI(title="ML Microscope Backend")

# - In dev, Vue runs at http://localhost:5173 and calls this backend at http://localhost:8000
# - In prod (Pi), this backend will also serve the built Vue app from dist/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Request models
# -----------------------
class MoveAbsRequest(BaseModel):
    x: int
    y: int
    z: int


class CaptureRequest(BaseModel):
    filename: str = "capture"
    temporary: bool = False
    use_video_port: bool = False
    bayer: bool = False
    annotations: dict = {}
    tags: list = []

class AnalyzeRequest(BaseModel):
    id: str

class SaveCaptureRequest(BaseModel):
    filename: str | None = None
    notes: str | None = None
    annotations: dict = {}
    tags: list[str] = []


# -----------------------
# API routes
# -----------------------
@app.get("/health")
@app.head("/health")
def health():
    if server.apiHealth():
        return {"ok": True, "message": "Microscope API reachable"}
    raise HTTPException(status_code=503, detail="Microscope API not reachable")


@app.get("/live")
def live():
    return {"mjpeg_url": server.mjpeg_stream_url()}


@app.get("/live/stream")
def live_stream():
    url = server.mjpeg_stream_url()
    try:
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "multipart/x-mixed-replace")
        return StreamingResponse(r.raw, media_type=content_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live stream failed: {e}")


@app.get("/captures")
def captures():
    try:
        data = server.listCaptures()
        return {"captures": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture")
def capture(req: CaptureRequest):
    try:
        payload = req.model_dump()
        cap = server.captureImg(payload)
        return {"ok": True, "capture": cap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/captures/{capture_id}/image")
def get_capture_image(capture_id: str):
    try:
        meta = requests.get(f"{server.API_BASE}api/v2/captures/{capture_id}", timeout=10)
        meta.raise_for_status()
        name = meta.json().get("name", "capture.jpeg")
        url = f"{server.API_BASE}api/v2/captures/{capture_id}/download/{name}"
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "image/jpeg")
        return StreamingResponse(r.raw, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch capture image failed: {e}")
    
@app.put("/captures/{capture_id}/metadata")
def update_capture_metadata(capture_id: str, req: SaveCaptureRequest):
    try:
        ann = dict(req.annotations or {})
        if req.notes:
            ann["Notes"] = req.notes
        if req.filename:
            ann["DisplayName"] = req.filename

        ann_url = f"{server.API_BASE}api/v2/captures/{capture_id}/annotations"
        r1 = requests.put(ann_url, json=ann, timeout=15)
        r1.raise_for_status()

        tags = [t for t in (req.tags or []) if t and t != "temporary"]
        tags_url = f"{server.API_BASE}api/v2/captures/{capture_id}/tags"
        r2 = requests.put(tags_url, json=tags, timeout=15)
        r2.raise_for_status()

        return {"ok": True, "annotations": ann, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update metadata failed: {e}")


@app.post("/move")
def move(req: MoveAbsRequest):
    try:
        action = server.moveButton(req.x, req.y, req.z)
        return {"ok": True, "action": action}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/position")
def position():
    try:
        pos = server.get_position()
        return {"position": pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/center")
def center():
    # "Go to (0,0,0)" — NOT re-zeroing scale
    try:
        action = server.moveButton(0, 0, 0)
        pos = server.get_position()
        return {"ok": True, "action": action, "position": pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/captures/{capture_id}")
def delete_capture(capture_id: str):
    try:
        ok = server.delete_capture(capture_id)
        return {"ok": ok}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # TODO: replace with real output
    return {
        "ok": True,
        "blobCount": 89,
        "overlayImageUrl": None,  # later could be "/analysis/{id}/overlay.png"
        "maskImageUrl": None
    }


# ---------------------------
# Serve built Vue app (dist/)
# ---------------------------

def get_frontend_dist() -> Path:
    """
    Works in dev (repo) and when frozen (PyInstaller).
    We'll copy Vue dist into: <exe_dir>/frontend_dist
    """
    if getattr(sys, "frozen", False):
        # running as exe
        exe_dir = Path(sys.executable).resolve().parent
        return exe_dir / "frontend_dist"
    else:
        # running from source
        return Path(__file__).resolve().parents[1] / "src" / "microscope-frontend" / "dist"


FRONTEND_DIST = get_frontend_dist()
ASSETS_DIR = FRONTEND_DIST / "assets"

if FRONTEND_DIST.exists():
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith(("health", "move", "position", "center", "captures", "capture", "live", "analyze")):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    print("[INFO] Vue dist not found:", FRONTEND_DIST)


if __name__ == "__main__":
    # run the API when exe is launched
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")