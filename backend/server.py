#server.py
#Connect Python to API

#WARNING: a lot in here is not correct or left with filler values as substitutions until the correct
        #extentions/values/proper returns are fleshed out until then DO NOT RUN WILL NOT COMPILE

import time
import numpy as np
import requests
from libraries.GlobalVariables import (API_BASE, XY_STEPSIZE, Z_STEPSIZE, NEG_X_BOUND,
                                       POS_X_BOUND, POS_Y_BOUND, NEG_Y_BOUND, POS_Z_BOUND, NEG_Z_BOUND)

#Helper Functions
def getCurrentPostion():
    print("getCurrentPostion")
    try:
        response = requests.get(f"{API_BASE}", )
        return response.json()

    except Exception as e:
        print("Error getting current postion")


# def x():
#     return getCurrentPostion()["x,y,z"] #return x cord
#
#
# def y():
#     return getCurrentPostion()["x,y,z"] #return y cord
#
#
# def z():
#     return getCurrentPostion()["x,y,z"] #return y cord
#
#
# #actual button functions to hw api
# def moveNegX():
#     """plan: get grid; if: point + step = out of bounds do nothing
#        (raise out of bounds error?? at least for test and logging);
#        else: try api move; raise error if issue"""
#     print("moveleft")
#     try:
#         if ((STEPSIZE + x()) < LEFTBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         # return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")
#
#
# def movePosX():
#     """plan: get grid; if: point + step = out of bounds do nothing
#            (raise out of bounds error?? at least for test and logging);
#            else: try api move; raise error if issue"""
#     print("moveright")
#     try:
#         if ((STEPSIZE + x()) > RIGHTBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         # return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")
#
#
# def moveNegY():
#     """plan: get grid; if: point + step = out of bounds do nothing
#            (raise out of bounds error?? at least for test and logging);
#            else: try api move; raise error if issue"""
#     print("movedown")
#     try:
#         if ((STEPSIZE + y()) < BOTTOMBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         # return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")
#
#
# def movePosY():
#     """plan: get grid; if: point + step = out of bounds do nothing
#            (raise out of bounds error?? at least for test and logging);
#            else: try api move; raise error if issue"""
#     print("moveup")
#     try:
#         if((STEPSIZE + y()) > TOPBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         #return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")
#
#
# #FORZ: need to know neg vs pos z cords actually interface with movement come back to these
# def movePosZ():
#     """plan: get grid; if: point + step = out of bounds do nothing
#        (raise out of bounds error?? at least for test and logging);
#        else: try api move; raise error if issue"""
#     print("moveleft")
#     try:
#         if ((STEPSIZE + x()) < LEFTBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         # return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")
#
# def moveNegZ():
#     """plan: get grid; if: point + step = out of bounds do nothing
#        (raise out of bounds error?? at least for test and logging);
#        else: try api move; raise error if issue"""
#     print("moveleft")
#     try:
#         if ((STEPSIZE + x()) < LEFTBOUND):
#             raise Exception("out of bounds")
#
#         response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
#         # return code? json?
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
#         print("Movement error: motor could not move or movement out of bounds")


def move():
    print("move")
    try:
        switch(getCurrentPostion()):


        response = requests.get(f"{API_BASE}", timeout=2.0)


def getImg(): #-> jpeg?
    print("getImg")
    try:
       response = requests.get(f"{API_BASE}(extention)", timeout=2.0)
       return response.json() #don't want to actually return json needs help for actual img return val

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Camera error: could not take img")


def getVideo(minutes: int, frames: int) -> list:
    print("getVideo")
    secs: int = minutes * 60
    fps: float = frames / secs

    video: list = []

    for i in np.arange(fps):
        time.sleep(fps)
        video.append(getImg())

    return video
