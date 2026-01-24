#server.py
#Connect Python to API

import time
import numpy as np
import requests
from libraries.GlobalVariables import API_BASE, STEPSIZE


def moveLeft():
    """plan: get grid; if: point + step = out of bounds do nothing
       (raise out of bounds error?? at least for test and logging);
       else: try api move; raise error if issue"""
    print("moveleft")
    #if ()

def moveRight():
    """plan: get grid; if: point + step = out of bounds do nothing
           (raise out of bounds error?? at least for test and logging);
           else: try api move; raise error if issue"""
    print("moveright")

def moveDown():
    """plan: get grid; if: point + step = out of bounds do nothing
           (raise out of bounds error?? at least for test and logging);
           else: try api move; raise error if issue"""
    print("movedown")

def moveUp():
    """plan: get grid; if: point + step = out of bounds do nothing
           (raise out of bounds error?? at least for test and logging);
           else: try api move; raise error if issue"""
    print("moveup")

def getImg() -> jpeg:
    print("getImg")
    try:
        response = requests.get(f"{API_BASE}(extention)", timeout=2.0)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Camera error: could not take img")


def getVideo(minutes: int, frames: int) -> list[jpeg]: #def not how this works
    print("getVideo")
    secs: int = minutes * 60
    fps: float = frames / secs

    video: list = []

    for i in np.arange(fps):
        time.sleep(fps)
        video.append(getImg())

    return video
