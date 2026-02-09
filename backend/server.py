#server.py
#Connect Python to API

#WARNING: a lot in here is not correct or left with filler values as substitutions until the correct
        #extentions/values/proper returns are fleshed out until then DO NOT RUN WILL NOT COMPILE

import time
import math
#from ctypes.wintypes import tagMSG
#from http.client import responses
import backend.error
import numpy as np
#import json
import requests
from libraries.GlobalVariables import (API_BASE, POS_X_BOUND, POS_Z_BOUND, NEG_Z_BOUND,
                                       MAX_DURATION_SEC)

#Helper Functions

#for arrow keys
# def getCurrentPosition(timeout = 2.0):
#     print("getCurrentPosition")
#     try:
#         response = requests.get(f"{API_BASE}api/v2/instrument/state/stage/position", timeout=timeout)
#         return response.json()
#
#     except Exception as e:
#         print("Error getting current position")


def apiHealth(timeout=2.0) -> bool:
    try:
        response = requests.get(f"{API_BASE}api/v2", timeout=timeout)
        response.raise_for_status()
        return response.status_code == 200
    except requests.RequestException:
        return False


def checkCords(x, y, z) -> bool:
    print("checkCords")

    d = math.sqrt(x**2 + y**2)
    if d <= POS_X_BOUND:
        if NEG_Z_BOUND >= z >= POS_Z_BOUND:
            return True
        else:
            return False
    else:
        return False


#def moveArrows():

def get_position(timeout=8.0) -> dict:
    """Returns current stage position from OpenFlexure."""
    r = requests.get(f"{API_BASE}api/v2/instrument/state/stage/position", timeout=timeout)
    r.raise_for_status()
    pos = r.json()
    pos["x"] = -pos["x"]
    return pos

def moveButton(x: int, y: int, z: int, timeout = 60.0):
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


def captureImg(payload: dict, timeout = 2.0): #-> jpeg?
    """take image and save to local pi"""
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
    """returns a list of all saved images on the local pi"""
    print("listCaptures")
    try:
        response = requests.get(f"{API_BASE}api/v2/actions/camera/get", timeout=timeout)
        response.raise_for_status()
        return response.json()

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Camera error: could not list captures")


def mjpeg_stream_url():
    try:
        return f"{API_BASE}api/v2/streams/mjpeg"
    except requests.exceptions.ConnectionError:
        print("Camera error: could not stream mjpeg")


def captureVideo(fpm: int, payload: dict, duration: float = MAX_DURATION_SEC) -> list:
    print("getVideo")
    spf: float = 60 / fpm

    video: list = []
    start_time = time.time()
    i = 0

    while time.time() - start_time < duration:
        video.append(captureImg(payload))
        # video.append(f"img{i}")
        # i += 1
        # time.sleep(spf)

    return video


def download():
    """download img api call"""
    print("download")

if __name__ == "__main__":
    listCaptures()


