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


def checkCords(x, y, z) -> bool:
    """
    takes in x,,yz coordinates and checks that the points are in the circular
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


def mjpeg_stream_url():
    try:
        return f"{API_BASE}api/v2/streams/mjpeg"
    except requests.exceptions.ConnectionError:
        print("Camera error: could not stream mjpeg")


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
        # video.append(f"img{i}")
        # i += 1
        # time.sleep(spf)

    return video

def delete_capture(capture_id: str) -> bool:
    url = f"{API_BASE}api/v2/captures/{capture_id}"
    r = requests.delete(url, timeout=10)

    if r.status_code in (200, 204):
        return True
    raise RuntimeError(f"Delete failed: {r.status_code} {r.text}")


# def download():
#     """download img api call"""
#     print("download")

# if __name__ == "__main__":
#     listCaptures()
#

