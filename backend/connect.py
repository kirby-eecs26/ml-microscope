#connect.py
#Establish api connection

import requests
import error
import json #?? precaution
from libraries import GlobalVariables
print("connect.py is running")

API_BASE = "http://microscope.local:5000/" #we can either put the last "/" here or at
                                            # hte beginning of the extensions,

def apiConnect(timeout = 2.0):
    """plan: take in the microscope ip? for connection and connect to the API.
    prints conformation if 200 returns raises; error if not"""
    try:
        response = requests.get(f"{API_BASE}api/v2", timeout=timeout)

        if response.status_code == 200:
            print("200 connection :)")
            return True
        else:
            raise error.APIConnectionError(response.status_code)

    except error.APIConnectionError as e:
        print(e.message)
        return False

    except requests.RequestException as e:
        print("Microscope not found or could not connect")
        return False


def camConnect(timeout = 2.0):
    """plan: take in the microscope ip? for connection and conforms camera functionality.
    prints conformation if (success code) returns; raises error if not"""
    try:
        response = requests.get(
            f"{API_BASE}api/v2/streams/mjpeg", timeout=timeout, stream=True)

        if response.status_code == 200: #change for correct camrea respons
            print("camera connection :)")
            return True
        else:
            raise error.CameraConnectionError(response.status_code)

    except error.CameraConnectionError as e:
        print(e.message)
        return False

    except requests.RequestException as e:
        print("Microscope camera not found or malfunction")
        return False


def disconnect():
    """plan: take in the microscope ip for connection and disconnect to the API.
    prints conformation if (success code) returns; raises error if not"""
    try:
        response = requests.get(f"{API_BASE}api/v2/actions/system/shutdown/", timeout=2.0)

        if response.status_code == 200:
            print("disconnected :)")
            return True
        else:
            raise error.APIDisconnectionError(response.status_code)

    except error.APIDisconnectionError as e:
        print("Could not disconnect :(" + e.message)
        return False


if __name__ == "__main__":
    apiConnect()
    camConnect()
