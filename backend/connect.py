import requests
import error

#i put double spaces to distinguish between the functions

API_BASE = "http://microscope.local:5000/" #we can either put the last "/" here or at
                                            # hte beginning of the extensions, unsure which would be preferred

def apiConnect(ip, timeout = 2.0):
    """plan: take in the microscope ip for connection and connect to the API.
    prints conformation if 200 returns raises; error if not"""
    try:
        response = requests.get(f"{API_BASE}api/v2", timeout=timeout)

        if response.status_code == 200:
            print("200 connection :)")
        else:
            raise error.APIConnectionError(response.status_code)

    except error.APIConnectionError as e:
        print(e.message)


def camConnect(ip, timeout = 2.0):
    """plan: take in the microscope ip for connection and conforms camera functionality.
    prints conformation if (success code) returns; raises error if not"""
    try:
        response = requests.get(f"{API_BASE}api/v2/streams/mjpeg", timeout=timeout)

        if response.status_code == 200: #change for correct camrea respons
            print("camera connection :)")
        else:
            raise error.CameraConnectionError(response.status_code)

    except error.CameraConnectionError as e:
        print(e.message)


def disconnect(ip):
    """plan: take in the microscope ip for connection and disconnect to the API.
    prints conformation if (success code) returns; raises error if not"""
    try:
        response = requests.get(f"{API_BASE}", timeout=2.0) #path extention for disconnecting from the api & microscope

        if response.status_code == 200: #change for correct camrea respons
            print("disconnected :)")
        else:
            raise error.APIDisconnectionError(response.status_code)

    except error.APIDisconnectionError as e:
        print("Could not disconnect :(" + e.message)
