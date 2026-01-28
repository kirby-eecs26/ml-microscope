#client.py
#Connect FE to Python

import requests
from connect import apiConnect, camConnect

API_BASE = "http://microscope.local:5000/"

def health():
    if not apiConnect():
        raise RuntimeError("Microscope API not available")
    if not camConnect():
        raise RuntimeError("Microscope camera not available")

def mjpeg_stream_url():
    return f"{API_BASE}api/v2/streams/mjpeg"

def list_captures(timeout=5.0):
    r = requests.get(f"{API_BASE}api/v2/captures", timeout=timeout)
    r.raise_for_status()
    return r.json()

def capture_image(payload: dict, timeout=10.0):
    # payload includes filename, temporary, use_video_port, bayer, annotations, tags
    r = requests.post(f"{API_BASE}api/v2/actions/camera/capture", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print(list_captures()[:1])