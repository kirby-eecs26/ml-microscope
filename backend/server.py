#server.py
#Connect Python to API

#WARNING: a lot in here is not correct or left with filler values as substitutions until the correct
        #extentions/values/proper returns are fleshed out until then DO NOT RUN WILL NOT COMPILE

import time
import math
#from ctypes.wintypes import tagMSG
#from http.client import responses

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



def moveButton(x: int, y: int, z: int, timeout = 2.0):
    print("move")
    try:
        if checkCords(x, y, z):
            payload = {
                "x": x,
                "y": y,
                "z": z,
                "absolute": True
            }

            print("Cords moved")
            response = requests.post(f"{API_BASE}api/v2/actions/stage/move", json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()

        else:
            print("Cords not moved")
            raise Exception("Cords not moved")

    except Exception as e:
        print("Cords not moved")


def captureImg(payload: dict, timeout = 2.0): #-> jpeg?
    """take image and save to local pi"""
    print("getImg")
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


def captureVideo(frames: int, payload: dict, duration: float = MAX_DURATION_SEC) -> list:
    print("getVideo")
    spf: float = 3600 / frames

    video: list = []

    for i in np.arange(0, duration, spf):
        video.append(captureImg(payload))  # wrong func call
        time.sleep(spf)

    return video


def download():
    """download img api call"""
    print("download")


