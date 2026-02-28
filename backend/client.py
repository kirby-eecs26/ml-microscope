# client.py
# Connect FE (Vue) to Python (FastAPI)

from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import Query
from backend.logging_store import list_events, add_message
# Count ml imports
import os
import time
import uuid
import numpy as np
import cv2
from fastapi.responses import FileResponse

from backend.count import count_from_rgb
from backend.server import get_video_path

from backend.motion import analyze_motion, MotionConfig

from backend import server
import sys
import uvicorn
import shutil

ANALYSIS_DIR = Path(__file__).resolve().parent / "analysis_outputs"
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

SAVED_VIDEOS_DIR = Path(__file__).resolve().parent / "saved_videos"
SAVED_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_CACHE: dict[str, dict] = {}
ANALYSIS_TTL_SEC = 60 * 60  # 1 hour

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

class TagsRequest(BaseModel):
    tags: list[str] = []

class VideoStartRequest(BaseModel):
    fpm: int
    max_frames: int = 300
    max_h: int = 1080

class VideoStopRequest(BaseModel):
    recording_id: str

class VideoAnalyzeRequest(BaseModel):
    type: str = "motion_tracking"
    mode: str = "ml_kmeans"
    config: dict | None = None

class SaveVideoAnalysisRequest(BaseModel):
    analysis: dict = {}


# -----------------------
# API routes
# -----------------------
@app.get("/health")
@app.head("/health")
def health():
    return {"ok": True, "message": "Backend running"}

@app.get("/microscope/health")
def microscope_health():
    if server.apiHealth():
        return {"ok": True, "message": "Microscope reachable"}
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
    
@app.post("/video/start")
def video_start(req: VideoStartRequest):
    try:
        info = server.start_video_recording(
            fpm=req.fpm,
            max_frames=req.max_frames,
            max_h=req.max_h
        )
        return {"ok": True, **info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video start failed: {e}")


@app.post("/video/stop")
def video_stop(req: VideoStopRequest):
    try:
        info = server.stop_video_recording(req.recording_id)
        return {"ok": True, **info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video stop failed: {e}")


@app.get("/video/{recording_id}/status")
def video_status(recording_id: str):
    try:
        return server.get_video_status(recording_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/video/{video_id}/download")
def download_video(video_id: str):
    saved_path = SAVED_VIDEOS_DIR / f"{video_id}.mp4"
    if saved_path.exists():
        return FileResponse(
            str(saved_path),
            media_type="video/mp4",
            filename=f"{video_id}.mp4",
            headers={"Content-Disposition": f'inline; filename="{video_id}.mp4"'},
        )
    try:
        path = server.get_video_path(video_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        path,
        media_type="video/mp4",
        filename=f"{video_id}.mp4",
        headers={"Content-Disposition": f'inline; filename="{video_id}.mp4"'},
    )

@app.post("/video/analyze/{video_id}")
def analyze_video_route(video_id: str, req: VideoAnalyzeRequest):
    try:
        if req.type not in ("motion_tracking", "motion_tracking_ml"):
            raise HTTPException(status_code=400, detail="Unsupported analysis type")

        path = server.get_video_path(video_id)

        cfg = MotionConfig()
        if req.config:
            for k, v in req.config.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)

        mode = req.mode or "ml_kmeans"
        result = analyze_motion(path, cfg=cfg, mode=mode)
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analyze failed: {e}")
    
@app.put("/video/{video_id}/analysis")
def save_video_analysis(video_id: str, req: SaveVideoAnalysisRequest):
    try:
        import json
        meta_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        if not meta_path.exists():
            raise HTTPException(status_code=404, detail="Video metadata not found (is it saved?)")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["analysis"] = req.analysis or {}
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return {"ok": True, "video": meta}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save video analysis failed: {e}")
    

@app.get("/videos")
def list_videos():
    try:
        out = []
        for p in SAVED_VIDEOS_DIR.glob("*.json"):
            try:
                import json
                meta = json.loads(p.read_text(encoding="utf-8"))
                vid = meta.get("id")
                if not vid:
                    continue
                mp4_path = SAVED_VIDEOS_DIR / f"{vid}.mp4"
                if not mp4_path.exists():
                    continue
                out.append(meta)
            except Exception:
                pass
        out.sort(key=lambda x: x.get("time", ""), reverse=True)
        return {"videos": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List videos failed: {e}")

@app.post("/video/{video_id}/save")
def save_video(video_id: str, req: SaveCaptureRequest):
    try:
        src = server.get_video_path(video_id)
        if not src or not os.path.exists(src):
            raise HTTPException(status_code=404, detail="Temp video not found")
        dst = SAVED_VIDEOS_DIR / f"{video_id}.mp4"
        shutil.copy2(src, dst)
        server.delete_video_recording(video_id)
        base_name = (req.filename or f"video_{video_id}").strip()
        ann = dict(req.annotations or {})
        if req.notes:
            ann["Notes"] = req.notes
        meta = {
            "id": video_id,
            "name": base_name,
            "path": str(dst),
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "format": "mp4",
            "annotations": ann,
            "tags": [t for t in (req.tags or []) if t and t != "temporary"],
        }
        meta_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            import json
            json.dump(meta, f, indent=2)
        return {"ok": True, "video": meta}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save video failed: {e}")
    

   
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
        if req.tags is not None:
            tags = [t for t in (req.tags or []) if t and t != "temporary"]
            if len(tags) > 0:
                tags_url = f"{server.API_BASE}api/v2/captures/{capture_id}/tags"
                r2 = requests.put(tags_url, json=tags, timeout=15)
                r2.raise_for_status()
        return {"ok": True, "annotations": ann, "tags": req.tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update metadata failed: {e}")
    
@app.put("/captures/{capture_id}/tags")
def set_capture_tags(capture_id: str, req: TagsRequest):
    try:
        tags = [str(t).strip() for t in (req.tags or [])]
        tags = [t for t in tags if t and t != "temporary"]

        tags_url = f"{server.API_BASE}api/v2/captures/{capture_id}/tags"
        r = requests.put(tags_url, json=tags, timeout=15)
        r.raise_for_status()

        return {"ok": True, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update tags failed: {e}")


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
    
@app.post("/zip/build")
def zip_build():
    try:
        caps = server.listCaptures()
        ids = [c["id"] for c in (caps or []) if "id" in c]

        url = f"{server.API_BASE}api/v2/extensions/org.openflexure.zipbuilder/build"
        r = requests.post(url, json=ids, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zip build failed: {e}")


@app.get("/actions/{action_id}")
def action_status(action_id: str):
    try:
        url = f"{server.API_BASE}api/v2/actions/{action_id}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action fetch failed: {e}")
    
@app.get("/zip/get/{zip_id}")
def zip_get(zip_id: str):
    try:
        url = f"{server.API_BASE}api/v2/extensions/org.openflexure.zipbuilder/get/{zip_id}"
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()

        headers = {
            "Content-Disposition": f'attachment; filename="captures_{zip_id}.zip"'
        }
        content_type = r.headers.get("Content-Type", "application/zip")
        return StreamingResponse(r.raw, media_type=content_type, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zip download failed: {e}")
    
@app.post("/captures/{capture_id}/analyze")
def analyze_capture(capture_id: str):
    try:
        meta = requests.get(f"{server.API_BASE}api/v2/captures/{capture_id}", timeout=10)
        meta.raise_for_status()
        name = meta.json().get("name", "capture.jpeg")

        img_url = f"{server.API_BASE}api/v2/captures/{capture_id}/download/{name}"
        r = requests.get(img_url, timeout=30)
        r.raise_for_status()

        data = np.frombuffer(r.content, dtype=np.uint8)
        bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if bgr is None:
            raise Exception("OpenCV could not decode image bytes")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        result = count_from_rgb(rgb, debug=True)
        overlay_bgr = result.overlay_bgr
        if overlay_bgr is None:
            raise Exception("Overlay not generated (debug=True required)")
        out_name = f"{capture_id}_{uuid.uuid4().hex}.jpg"
        out_path = ANALYSIS_DIR / out_name
        ok = cv2.imwrite(str(out_path), overlay_bgr)
        if not ok:
            raise Exception("Failed to write overlay image")

        ANALYSIS_CACHE[capture_id] = {
            "overlay_path": str(out_path),
            "created": time.time(),
            "count": int(result.count),
        }

        return {
            "ok": True,
            "blobCount": int(result.count),
            "overlayImageUrl": f"/analysis/{capture_id}/overlay",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyze failed: {e}")
    
@app.get("/analysis/{capture_id}/overlay")
def get_overlay(capture_id: str):
    item = ANALYSIS_CACHE.get(capture_id)
    if not item:
        raise HTTPException(status_code=404, detail="No analysis found for this capture")
    path = item["overlay_path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Overlay file missing")
    return FileResponse(path, media_type="image/jpeg")

@app.delete("/captures/{capture_id}/tags/{tag}")
def delete_capture_tag(capture_id: str, tag: str):
    url = f"http://microscope.local:5000/api/v2/captures/{capture_id}/tags"

    # OpenFlexure expects the payload to be a JSON array, e.g. ["c"]
    resp = requests.delete(url, json=[tag], timeout=10)

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Delete tag failed: {resp.text}",
        )

    try:
        return resp.json()
    except Exception:
        return {"ok": True}
    
@app.delete("/video/{video_id}")
def delete_video(video_id: str):
    try:
        mp4_path = SAVED_VIDEOS_DIR / f"{video_id}.mp4"
        json_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        deleted_any = False
        if mp4_path.exists():
            mp4_path.unlink()
            deleted_any = True
        if json_path.exists():
            json_path.unlink()
            deleted_any = True
        if deleted_any:
            return {"ok": True, "deleted": True, "where": "saved_videos"}
        ok = server.delete_video_recording(video_id)
        return {"ok": bool(ok), "deleted": bool(ok), "where": "video_outputs_or_recordings"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video delete failed: {e}")
    
@app.get("/api/v2/events/logging")
def get_logging(level: str = Query("ALL")):
    items = list_events(level)
    items.reverse()
    return items

@app.get("/logging")
def logging():
    try:
        url = f"{server.API_BASE}api/v2/events/logging"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging fetch failed: {e}")

@app.post("/api/v2/events/logging/test")
def test_logging():
    add_message("Test log event from ML microscope backend", levelname="INFO", filename="client.py", lineno=1)
    return {"ok": True}

@app.delete("/analysis/{capture_id}")
def clear_analysis(capture_id: str):
    item = ANALYSIS_CACHE.pop(capture_id, None)
    if not item:
        return {"ok": True, "deleted": False}
    path = item.get("overlay_path")
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    return {"ok": True, "deleted": True}


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
        if full_path.startswith((
            "api",
            "health", "microscope", "move", "position", "center",
            "captures", "capture", "live", "analyze",
            "zip", "actions",
            "analysis",
            "video", "videos",
        )):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    print("[INFO] Vue dist not found:", FRONTEND_DIST)


if __name__ == "__main__":
    # run the API when exe is launched
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")