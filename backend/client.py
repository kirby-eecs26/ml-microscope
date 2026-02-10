# client.py
# Connect FE (Vue) to Python (FastAPI)

from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import server

app = FastAPI(title="ML Microscope Backend")

# NOTE:
# - In dev, your Vue runs at http://localhost:5173 and calls this backend at http://localhost:8000
# - In prod (Pi), this backend will also serve the built Vue app from dist/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for dev; for prod you can tighten this
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
    filename: str
    temporary: bool = False
    use_video_port: bool = False
    bayer: bool = False
    annotations: dict = {}
    tags: list = []


# -----------------------
# API routes
# -----------------------
@app.get("/health")
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
        cap = server.getImg(payload)
        return {"ok": True, "capture": cap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# ---------------------------
# Serve built Vue app (dist/)
# ---------------------------
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "src" / "microscope-frontend" / "dist"
ASSETS_DIR = FRONTEND_DIST / "assets"

if FRONTEND_DIST.exists():
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Don't swallow API routes
        if full_path.startswith(("health", "move", "position", "center", "captures", "capture", "live")):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    print("[INFO] Vue dist not found. (This is normal in dev when running Vite.)")