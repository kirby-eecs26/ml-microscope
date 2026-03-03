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
import csv
import io
import json
from fastapi.responses import StreamingResponse
import time
import uuid
import numpy as np
import cv2
import re
import unicodedata
from zipfile import ZipFile, ZIP_DEFLATED
from fastapi.responses import FileResponse

from backend.count import count_from_rgb

from backend.motion import analyze_motion, MotionConfig, SENSITIVITY_PRESETS

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

VIDEO_OVERLAY_CACHE: dict[str, str] = {}

ZIP_DIR = Path(__file__).resolve().parent / "zips"
ZIP_DIR.mkdir(parents=True, exist_ok=True)

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
    sensitivity: str | None = None  # "low" | "medium" | "high"

class SaveVideoAnalysisRequest(BaseModel):
    analysis: dict = {}

class CameraSettingsRequest(BaseModel):
    exposure: int | None = None
    analogueGain: float | None = None
    digitalGain: float | None = None
    wbR: float | None = None
    wbB: float | None = None
    jpegQuality: int | None = None
    streamResolution: str | None = None
    cameraBitrate: str | None = None
    cameraFramerate: int | None = None

def _safe_filename(name: str, default: str) -> str:
    name = (name or "").strip()
    if not name:
        name = default
    name = unicodedata.normalize("NFKD", name)
    name = name.replace("\\", "_").replace("/", "_").replace(":", "_")
    name = re.sub(r"[^\w.\- ()]+", "_", name).strip()
    if not name:
        name = default
    return name

def _safe_json(obj) -> str:
    try:
        return json.dumps(obj or {}, ensure_ascii=False)
    except Exception:
        return "{}"

def _ensure_ext(filename: str, ext: str) -> str:
    ext = ext if ext.startswith(".") else f".{ext}"
    if filename.lower().endswith(ext.lower()):
        return filename
    return filename + ext


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

#Helper
def resolve_video_path(video_id: str) -> str:
    saved_mp4 = SAVED_VIDEOS_DIR / f"{video_id}.mp4"
    if saved_mp4.exists():
        return str(saved_mp4)
    return server.get_video_path(video_id)

@app.post("/video/analyze/{video_id}")
def analyze_video_route(video_id: str, req: VideoAnalyzeRequest):
    try:
        path = resolve_video_path(video_id)
        cfg = MotionConfig()
        if req.sensitivity:
            preset = SENSITIVITY_PRESETS.get(req.sensitivity.lower())
            if preset:
                for k, v in preset.items():
                    setattr(cfg, k, v)
        if req.config:
            for k, v in req.config.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
        mode = req.mode or "ml_kmeans"
        result = analyze_motion(path, cfg=cfg, mode=mode)
        overlay_name = f"{video_id}_tracks.mp4"
        overlay_path = str(ANALYSIS_DIR / overlay_name)
        from backend.motion import render_motion_tracks_overlay
        render_motion_tracks_overlay(path, overlay_path, cfg=cfg)
        VIDEO_OVERLAY_CACHE[video_id] = overlay_path
        print("[tracks] overlay_path:", overlay_path, "bytes:", os.path.getsize(overlay_path))
        return {
            "ok": True,
            **result,
            "overlayVideoUrl": f"/analysis/video/{video_id}/tracks",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analyze failed: {e}")
    
@app.get("/analysis/video/{video_id}/tracks")
def get_tracks_overlay(video_id: str):
    path = VIDEO_OVERLAY_CACHE.get(video_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Tracks overlay not found")
    return FileResponse(path, media_type="video/mp4")

@app.delete("/analysis/video/{video_id}/tracks")
def delete_tracks_overlay(video_id: str):
    path = VIDEO_OVERLAY_CACHE.pop(video_id, None)
    fallback_path = ANALYSIS_DIR / f"{video_id}_tracks.mp4"
    deleted = False
    try:
        if path and os.path.exists(path):
            os.remove(path)
            deleted = True
        elif fallback_path.exists():
            fallback_path.unlink()
            deleted = True
    except Exception:
        pass
    return {"ok": True, "deleted": deleted}
    
@app.put("/video/{video_id}/analysis")
def save_video_analysis(video_id: str, req: SaveVideoAnalysisRequest):
    try:
        import json
        meta_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        if not meta_path.exists():
            raise HTTPException(status_code=404, detail="Video metadata not found (is it saved?)")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["analysis"] = req.analysis or {}
        ann = dict(meta.get("annotations") or {})
        a = req.analysis or {}
        if "motility_ratio" in a:       ann["ML_MotilityRatio"] = float(a["motility_ratio"])
        if "motion_score" in a:         ann["ML_MotionScore"] = float(a["motion_score"])
        if "avg_speed_px_per_s" in a:   ann["ML_AvgSpeedPxPerS"] = float(a["avg_speed_px_per_s"])
        if "tracks" in a:               ann["ML_Tracks"] = int(a["tracks"])
        ann["ML_AnalyzedAt"] = a.get("analyzed_at") or time.strftime("%Y-%m-%dT%H:%M:%S")
        meta["annotations"] = ann
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
    
@app.put("/video/{video_id}/tags")
def set_video_tags(video_id: str, req: TagsRequest):
    try:
        import json
        meta_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        if not meta_path.exists():
            raise HTTPException(status_code=404, detail="Video metadata not found (is it saved?)")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        tags = [str(t).strip() for t in (req.tags or [])]
        tags = [t for t in tags if t and t != "temporary"]
        tags = list(dict.fromkeys(tags))

        meta["tags"] = tags
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return {"ok": True, "tags": tags}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update video tags failed: {e}")


@app.delete("/video/{video_id}/tags/{tag}")
def delete_video_tag(video_id: str, tag: str):
    try:
        import json
        meta_path = SAVED_VIDEOS_DIR / f"{video_id}.json"
        if not meta_path.exists():
            raise HTTPException(status_code=404, detail="Video metadata not found (is it saved?)")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        tags = [str(t).strip() for t in (meta.get("tags") or [])]
        tags = [t for t in tags if t and t != "temporary" and t != tag]

        meta["tags"] = tags
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return {"ok": True, "tags": tags}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete video tag failed: {e}")

   
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
        zip_id = uuid.uuid4().hex
        zip_path = (Path(__file__).resolve().parent / "zip_outputs")
        zip_path.mkdir(parents=True, exist_ok=True)
        out_zip = zip_path / f"gallery_{zip_id}.zip"
        caps = server.listCaptures() or []
        vids = []
        for p in SAVED_VIDEOS_DIR.glob("*.json"):
            try:
                import json
                meta = json.loads(p.read_text(encoding="utf-8"))
                vid = meta.get("id")
                if not vid:
                    continue
                mp4_path = SAVED_VIDEOS_DIR / f"{vid}.mp4"
                if mp4_path.exists():
                    vids.append(meta)
            except Exception:
                pass
        used_names = set()
        with ZipFile(out_zip, "w", compression=ZIP_DEFLATED) as z:
            for c in caps:
                cid = c.get("id")
                if not cid:
                    continue
                meta = requests.get(f"{server.API_BASE}api/v2/captures/{cid}", timeout=10)
                meta.raise_for_status()
                cap_name = meta.json().get("name", f"{cid}.jpeg")

                cap_name = _safe_filename(cap_name, f"{cid}.jpeg")
                arc = f"captures/{cap_name}"
                if arc in used_names:
                    arc = f"captures/{cid}_{cap_name}"
                used_names.add(arc)
                url = f"{server.API_BASE}api/v2/captures/{cid}/download/{cap_name}"
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                z.writestr(arc, r.content)

            for v in vids:
                vid = v.get("id")
                if not vid:
                    continue
                mp4_path = SAVED_VIDEOS_DIR / f"{vid}.mp4"
                if not mp4_path.exists():
                    continue
                human = _safe_filename(v.get("name"), f"video_{vid}")
                human = _ensure_ext(human, ".mp4")
                arc = f"videos/{human}"
                if arc in used_names:
                    arc = f"videos/{vid}_{human}"
                used_names.add(arc)
                z.write(str(mp4_path), arcname=arc)
        return {"ok": True, "id": zip_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zip build failed: {e}")
    
@app.get("/zip/get/{zip_id}")
def zip_get(zip_id: str):
    zip_path = Path(__file__).resolve().parent / "zip_outputs" / f"gallery_{zip_id}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Zip not found")
    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"gallery_{zip_id}.zip",
    )


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

@app.post("/settings/camera/apply")
def apply_camera_settings(req: CameraSettingsRequest):
    try:
        s = requests.get(f"{server.API_BASE}api/v2/instrument/settings", timeout=10)
        s.raise_for_status()
        full = s.json()
        cam = full.get("camera") or {}
        pic = cam.get("picamera") or {}
        res_map = {
            "higher": [832, 624],
            "normal": [640, 480],
        }
        bitrate_map = {
            "max": -1,
            "high": 25_000_000,
            "normal": 17_000_000,
            "low": 5_000_000,
            "verylow": 2_500_000,
        }
        if req.jpegQuality is not None:
            cam["jpeg_quality"] = int(req.jpegQuality)

        if req.streamResolution is not None:
            cam["stream_resolution"] = res_map.get(req.streamResolution, cam.get("stream_resolution", [832, 624]))

        if req.cameraBitrate is not None:
            cam["mjpeg_bitrate"] = bitrate_map.get(req.cameraBitrate, cam.get("mjpeg_bitrate", -1))
        pic["exposure_mode"] = "off"
        pic["awb_mode"] = "off"
        if req.exposure is not None:
            pic["shutter_speed"] = int(req.exposure)
        if req.analogueGain is not None:
            pic["analog_gain"] = float(req.analogueGain)
        if req.digitalGain is not None:
            pic["digital_gain"] = float(req.digitalGain)
        if req.cameraFramerate is not None:
            pic["framerate"] = float(req.cameraFramerate)
        if req.wbR is not None or req.wbB is not None:
            r = float(req.wbR if req.wbR is not None else (pic.get("awb_gains") or [1.0, 1.0])[0])
            b = float(req.wbB if req.wbB is not None else (pic.get("awb_gains") or [1.0, 1.0])[1])
            pic["awb_gains"] = [r, b]
        cam["picamera"] = pic
        full["camera"] = cam
        r = requests.put(f"{server.API_BASE}api/v2/instrument/settings", json=full, timeout=15)
        r.raise_for_status()
        return {"ok": True, "result": r.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apply camera settings failed: {e}")

@app.post("/settings/calibration/full_autocalibrate")
def calibration_full_autocalibrate():
    try:
        out = server.full_autocalibrate()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full auto-calibrate failed: {e}")


@app.post("/settings/calibration/auto_gain_shutter")
def calibration_auto_gain_shutter():
    try:
        out = server.auto_gain_shutter_speed()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto gain & shutter failed: {e}")


@app.post("/settings/calibration/auto_white_balance")
def calibration_auto_white_balance():
    try:
        out = server.auto_white_balance()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto white balance failed: {e}")


@app.post("/settings/calibration/auto_flat_field")
def calibration_auto_flat_field():
    try:
        out = server.auto_flat_field_correction()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto flat field failed: {e}")


@app.post("/settings/calibration/disable_flat_field")
def calibration_disable_flat_field():
    try:
        out = server.disable_flat_field_correction()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disable flat field failed: {e}")


@app.post("/settings/mapping/autocalibrate_using_camera")
def mapping_autocalibrate_using_camera():
    try:
        out = server.autocalibrate_using_camera()
        return {"ok": True, "result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping autocalibrate failed: {e}")
    
@app.get("/csv/gallery")
def csv_gallery():
    """
    Download a CSV containing all captures + saved videos, including:
    - id, type, name, time
    - notes
    - tags (semicolon-separated)
    - annotations (JSON string)
    - analysis (JSON string) when present
    """
    try:
        caps = server.listCaptures() or []
        videos = []
        for p in SAVED_VIDEOS_DIR.glob("*.json"):
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                vid = meta.get("id")
                if not vid:
                    continue
                mp4_path = SAVED_VIDEOS_DIR / f"{vid}.mp4"
                if not mp4_path.exists():
                    continue
                videos.append(meta)
            except Exception:
                pass
        def _time_key(x):
            return x.get("time", "") or ""
        videos.sort(key=_time_key, reverse=True)
        output = io.StringIO()
        writer = csv.writer(output)
        header = [
            "type",
            "id",
            "name",
            "time",
            "notes",
            "tags",
            "annotations_json",
            "analysis_json",
        ]
        writer.writerow(header)
        for c in caps:
            cid = c.get("id", "")
            name = c.get("name", "") or ""
            time_s = c.get("time", "") or ""

            ann = c.get("annotations") or {}
            notes = ann.get("Notes", "") if isinstance(ann, dict) else ""
            tags = c.get("tags") or []
            if not isinstance(tags, list):
                tags = []

            writer.writerow([
                "image",
                cid,
                name,
                time_s,
                notes,
                ";".join([str(t).strip() for t in tags if str(t).strip()]),
                json.dumps(ann, ensure_ascii=False),
                "",
            ])
        for v in videos:
            vid = v.get("id", "")
            name = v.get("name", "") or ""
            time_s = v.get("time", "") or ""

            ann = v.get("annotations") or {}
            notes = ann.get("Notes", "") if isinstance(ann, dict) else ""
            tags = v.get("tags") or []
            if not isinstance(tags, list):
                tags = []

            analysis = v.get("analysis") or {}

            writer.writerow([
                "video",
                vid,
                name,
                time_s,
                notes,
                ";".join([str(t).strip() for t in tags if str(t).strip()]),
                json.dumps(ann, ensure_ascii=False),
                json.dumps(analysis, ensure_ascii=False) if analysis else "",
            ])

        output.seek(0)
        csv_bytes = output.getvalue().encode("utf-8")

        filename = f"gallery_export_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }

        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv; charset=utf-8",
            headers=headers,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {e}")
    
@app.get("/export/csv")
def export_gallery_csv():
    """
    Export a CSV containing both captures (from OpenFlexure) and saved videos (from saved_videos/*.json).
    Includes annotations/tags/notes and any saved analysis.
    """
    rows = []
    try:
        caps = server.listCaptures() or []
    except Exception:
        caps = []

    for c in caps:
        ann = c.get("annotations") or {}
        tags = c.get("tags") or []
        rows.append({
            "type": "image",
            "id": c.get("id", ""),
            "name": c.get("name") or ann.get("DisplayName") or "capture",
            "time": c.get("time", ""),
            "format": c.get("format") or "jpeg",
            "notes": ann.get("Notes", ""),
            "tags": ";".join([str(t).strip() for t in tags if str(t).strip()]),
            "annotations_json": _safe_json(ann),
            "analysis_json": "", 
        })
    try:
        for p in SAVED_VIDEOS_DIR.glob("*.json"):
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                ann = meta.get("annotations") or {}
                tags = meta.get("tags") or []
                analysis = meta.get("analysis") or {}
                rows.append({
                    "type": "video",
                    "id": meta.get("id", ""),
                    "name": meta.get("name") or "video",
                    "time": meta.get("time", ""),
                    "format": meta.get("format") or "mp4",
                    "notes": ann.get("Notes", ""),
                    "tags": ";".join([str(t).strip() for t in tags if str(t).strip()]),
                    "annotations_json": _safe_json(ann),
                    "analysis_json": _safe_json(analysis),
                })
            except Exception:
                continue
    except Exception:
        pass
    fieldnames = [
        "type", "id", "name", "time", "format",
        "notes", "tags",
        "annotations_json", "analysis_json",
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    csv_text = buf.getvalue()
    headers = {"Content-Disposition": 'attachment; filename="gallery_export.csv"'}
    return StreamingResponse(iter([csv_text]), media_type="text/csv; charset=utf-8", headers=headers)


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
            "settings"
        )):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    print("[INFO] Vue dist not found:", FRONTEND_DIST)


if __name__ == "__main__":
    # run the API when exe is launched
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")