#server.py
#Connect Python to API

#WARNING: a lot in here is not correct or left with filler values as substitutions until the correct
        #extentions/values/proper returns are fleshed out until then DO NOT RUN WILL NOT COMPILE

import time
import math
import backend.error
import requests
import cv2
import os
import uuid
import threading
from pathlib import Path
import subprocess
from libraries.GlobalVariables import (API_BASE, POS_X_BOUND, POS_Z_BOUND, NEG_Z_BOUND,
                                       MAX_DURATION_SEC)

VIDEO_DIR = Path(__file__).resolve().parent / "video_outputs"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS: dict[str, dict] = {}

#Helper Functions

#for arrow keys



def apiHealth(timeout=2.0) -> bool:
    """
    requests api health diagnostics that checks that motors or in order and that the
    api has stable connection, raises error if connection and/or microscope unstable
    todo: add error to log
    :param timeout:
    :return: bool of good api health or not
    """
    try:
        response = requests.get(f"{API_BASE}api/v2", timeout=timeout)
        response.raise_for_status()

        return response.status_code == 200
    except requests.RequestException:
        return False


# LENS MOVEMENT
def checkCords(x, y, z) -> bool:
    """
    takes in x,y,z coordinates and checks that the points are in the circular
    bounds of the microscope case and stops before it hits the slide or
    z gets to low in bounds
    :param x: x axis cord
    :param y: y axis cord
    :param z: z axis cord (-z is closer to microscope, +z is further from microscope)
    :return: bool of new coordinates are in bounds or not
    """
    print("checkCords")

    d = math.sqrt(x**2 + y**2)
    if d <= POS_X_BOUND:
        if NEG_Z_BOUND >= z >= POS_Z_BOUND:
            return True
        else:
            return False
    else:
        return False

def get_position(timeout=8.0) -> dict:
    """
    Returns current stage position from OpenFlexure. raises error if api call wrong then catches
    todo: add exceptions to logging
    :param timeout:
    :return: dicts of the xyz coordinate positions
    """
    r = requests.get(f"{API_BASE}api/v2/instrument/state/stage/position", timeout=timeout)
    r.raise_for_status()
    pos = r.json()
    pos["x"] = -pos["x"]
    return pos

# def check_step(cords: dict):
# """plan: directions moving add it to temp cord check in or out of bounds return true if in bounds. false if out of bounds"""
#     if


# def moveArrows():
#     """
#     moving postion with arrow keys on step at a time
#     checks step will not be out of bounds the sends movement call to teh api for execution
#     if error raise and catch
#     todo: logging of errors
#     """
#     print("moveArrows")
#     try:
#         if :
#             payload = {
#                 "x": new_cords.x,
#                 "y": new_cords.y,
#                 "z": new_cords.z,
#                 "absolute": False
#             }
#
#

def moveButton(x: int, y: int, z: int, timeout = 60.0):
    """
    check new move coordinates are in bounds then request api to move lense and camera to
    new position, if coords not in bounds raise exception, if response status is an error raise
    exception, catch exeptions and put in log
    todo: add exceptions to logging
    :param x:
    :param y:
    :param z:
    :param timeout:
    :return: json response
    """
    x = -x
    print("moveButton")
    try:
        if checkCords(x, y, z):
            payload = {
                "x": x,
                "y": y,
                "z": z,
                "absolute": True
            }

            response = requests.post(f"{API_BASE}api/v2/actions/stage/move", json=payload, timeout=timeout)
            response.raise_for_status()

            print("Cords moved")
            return response.json()

        else:
            raise backend.error.MoveMicroscopeError()

    except (Exception, backend.error.MoveMicroscopeError) as e:
        print(e.__str__())

# IMAGE
def captureImg(payload: dict, timeout = 2.0):
    """
    take image and save to local pi
    return latest image dict
    :param payload:
    :param timeout:
    :return: image dict
    """
    print("captureImg")
    try:
        response = requests.post(f"{API_BASE}api/v2/actions/camera/capture", json=payload, timeout=timeout)
        response.raise_for_status()

        captureList = requests.get(f"{API_BASE}api/v2/captures", timeout=timeout)
        captureList.raise_for_status()
        allcaptures = captureList.json()
        print(allcaptures[-1])

        return allcaptures[-1] #returns dict of last picture taken

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Camera error: could not take img")


def listCaptures(timeout = 2.0):
    """
    returns a list of all saved image dicts on the local pi
    :param timeout:
    :return: list of dicts
    """
    print("listCaptures")
    try:
        response = requests.get(f"{API_BASE}api/v2/captures", timeout=timeout)
        response.raise_for_status()
        return response.json()

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Camera error: could not list captures")


# LIVE FEED
def mjpeg_stream_url():
    try:
        return f"{API_BASE}api/v2/streams/mjpeg"
    except requests.exceptions.ConnectionError:
        print("Camera error: could not stream mjpeg")


# VIDEO
def captureVideo(fpm: int, payload: dict, duration: float = MAX_DURATION_SEC) -> list:
    """
    takes in pyload of image capture annotations and notes, fpm, and duration,
    takes an image every few seconds to fit in the frames per min time arg,
    default duration of 15 seconds.
    errors are handeled in the image capture function
    :param fpm:
    :param payload:
    :param duration: default 15 seconds
    :return: list of image dicts w/ annotations and image access links
    """
    print("getVideo")
    spf: float = 60 / fpm

    video: list = []
    start_time = time.time()
    i = 0

    while time.time() - start_time < min(duration, MAX_DURATION_SEC):
        video.append(captureImg(payload))

    return video


def _iter_mjpeg_frames(url: str, timeout=10):
    """
    Yields JPEG bytes from a MJPEG stream.
    """
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()

    buf = b""
    for chunk in r.iter_content(chunk_size=4096):
        if not chunk:
            continue
        buf += chunk
        a = buf.find(b"\xff\xd8")
        b = buf.find(b"\xff\xd9")
        if a != -1 and b != -1 and b > a:
            jpg = buf[a:b+2]
            buf = buf[b+2:]
            yield jpg


def _resize_keep_aspect(bgr, max_h=1080):
    """
    Helper for resizing video.
    """
    h, w = bgr.shape[:2]
    if h <= max_h:
        return bgr
    scale = max_h / float(h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _record_worker(recording_id: str, fpm: int, max_frames: int, max_h: int):
    stop_event = RECORDINGS[recording_id]["stop"]
    raw_path = RECORDINGS[recording_id]["path_raw"]
    final_path = RECORDINGS[recording_id]["path_final"]
    mjpeg_url = mjpeg_stream_url()
    interval = 60.0 / float(fpm)
    writer = None
    written = 0
    next_t = time.time()
    try:
        for jpg in _iter_mjpeg_frames(mjpeg_url):
            if stop_event.is_set():
                break
            now = time.time()
            if now < next_t:
                continue
            next_t = now + interval
            data = np.frombuffer(jpg, dtype=np.uint8)
            frame_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if frame_bgr is None:
                continue
            frame_bgr = _resize_keep_aspect(frame_bgr, max_h=max_h)
            if writer is None:
                h, w = frame_bgr.shape[:2]
                playback_fps = 10.0
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(str(raw_path), fourcc, playback_fps, (w, h))
            writer.write(frame_bgr)
            written += 1
            if written >= max_frames:
                break
    finally:
        if writer is not None:
            writer.release()
        meta = RECORDINGS[recording_id]["meta"]
        meta["frames_written"] = written
        meta["finished_at"] = time.time()
        meta["done"] = True
        try:
            _transcode_h264(str(raw_path), str(final_path))
            RECORDINGS[recording_id]["path"] = str(final_path)
            meta["transcoded"] = True
        except Exception as e:
            meta["transcoded"] = False
            meta["transcode_error"] = str(e)
            RECORDINGS[recording_id]["path"] = str(raw_path)


def _transcode_h264(src_path: str, dst_path: str):
    cmd = [
        "ffmpeg", "-y",
        "-i", src_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-movflags", "+faststart",
        dst_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def start_video_recording(fpm: int, max_frames: int = 300, max_h: int = 1080) -> dict:
    if fpm not in (30, 60):
        raise ValueError("Only 30 or 60 FPM allowed")

    recording_id = uuid.uuid4().hex
    out_path = VIDEO_DIR / f"{recording_id}_raw.mp4"
    final_path = VIDEO_DIR / f"{recording_id}.mp4"

    stop_event = threading.Event()
    RECORDINGS[recording_id] = {
        "stop": stop_event,
        "path_raw": str(out_path),
        "path_final": str(final_path),
        "meta": {
            "id": recording_id,
            "fpm": fpm,
            "max_frames": max_frames,
            "max_h": max_h,
            "started_at": time.time(),
            "done": False,
            "frames_written": 0,
        },
    }

    t = threading.Thread(target=_record_worker, args=(recording_id, fpm, max_frames, max_h), daemon=True)
    RECORDINGS[recording_id]["thread"] = t
    t.start()

    return {"id": recording_id, "path": str(out_path), "meta": RECORDINGS[recording_id]["meta"]}


def stop_video_recording(recording_id: str) -> dict:
    rec = RECORDINGS.get(recording_id)
    if not rec:
        raise KeyError("Unknown recording id")

    rec["stop"].set()
    t = rec.get("thread")
    if t:
        t.join(timeout=5.0)

    return {"ok": True, "id": recording_id, "meta": rec["meta"], "path": rec["path"]}


def get_video_path(recording_id: str) -> str:
    rec = RECORDINGS.get(recording_id)
    if not rec:
        raise KeyError("Unknown recording id")
    return rec["path"]


def get_video_status(recording_id: str) -> dict:
    rec = RECORDINGS.get(recording_id)
    if not rec:
        raise KeyError("Unknown recording id")
    return rec["meta"]


def delete_capture(capture_id: str) -> bool:
    url = f"{API_BASE}api/v2/captures/{capture_id}"
    r = requests.delete(url, timeout=10)

    if r.status_code in (200, 204):
        return True
    raise RuntimeError(f"Delete failed: {r.status_code} {r.text}")

# if __name__ == "__main__":
#     listCaptures()
#

# SETTINGS

# CAMERA SETTINGS
def settings(payload: dict, timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/instrument/settings", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} PI Camera Settings error")


# CALIBRATION
def full_autocalibrate(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.calibration.picamera/recalibrate", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} Auto Calibration Settings error")


def auto_gain_shutter_speed(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.calibration.picamera/auto_exposure_from_raw", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} PI Camera Settings error")


def auto_white_balance(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.calibration.picamera/auto_white_balance_from_raw", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} Calibration Settings error")


def auto_flat_field_correction(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.calibration.picamera/auto_lens_shading_table", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} Calibration Settings error")


def disable_flat_field_correction(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.calibration.picamera/flatten_lens_shading_table", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} Calibration Settings error")


# Camera/stage mapping
def autocalibrate_using_camera(timeout=2.0):
    try:
        r = requests.post(f"{API_BASE}api/v2/extensions/org.openflexure.camera-stage-mapping/calibrate_xy", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"{e} Calibration Settings error")