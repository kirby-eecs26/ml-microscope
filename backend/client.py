#client.py
#Connect FE to Python

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from . import server
from fastapi.responses import StreamingResponse
import requests

# Allow Vue server to call this backend
app = FastAPI(title="ML Microscope Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#FASTAPI uses these for checking requests, do not delete classes
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


@app.get("/health")
def health():
    if server.apiHealth():
        return {"ok": True, "message": "Microscope API reachable"}
    else:
        raise HTTPException(
            status_code=503,
            detail="Microscope API not reachable"
        )

#return live cam view
@app.get("/live")
def live():
    return {"mjpeg_url": server.mjpeg_stream_url()}

@app.get("/live/stream")
def live_stream():
    url = server.mjpeg_stream_url()  # e.g. http://<pi>/api/v2/streams/mjpeg
    try:
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()

        # IMPORTANT: forward the real MJPEG content-type (with correct boundary)
        content_type = r.headers.get("Content-Type", "multipart/x-mixed-replace")

        return StreamingResponse(
            r.raw,  # stream raw bytes directly
            media_type=content_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live stream failed: {e}")

#return all image captures
@app.get("/captures")
def captures():
    try:
        data = server.listCaptures()
        return {"captures": data}
    except Exception as e:
        raise

#return single image capture
@app.post("/capture")
def capture(req: CaptureRequest):
    try:
        payload = req.model_dump()
        cap = server.getImg(payload)
        return {"ok": True, "capture": cap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#move action
@app.post("/move")
def move(req: MoveAbsRequest):
    try:
        action = server.moveButton(req.x, req.y, req.z)
        return {"ok": True, "action": action}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
