#connect.py
#Establish api connection

import requests
from backend import error

API_BASE = "http://microscope.local:5000/" #we can either put the last "/" here or at
                                            # hte beginning of the extensions,

def apiConnect(timeout = 2.0):
    """
    requests connection to the api with timeout limit, if times out -> raises error, checks
    response status -> is error raises an error, catch all errors but do not connection
    with connection
    :param timeout:
    :return:
    """
    try:
        response = requests.get(f"{API_BASE}api/v2", timeout=timeout)
        response.raise_for_status()

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
    """
    requests api camera diagnostic check, 200 returned code == valid connection
    if returned code or error raised in response status raise exception and catch
    todo: add errors to log
    :param timeout:
    :return:
    """
    try:
        response = requests.get(
            f"{API_BASE}api/v2/streams/mjpeg", timeout=timeout, stream=True)
        response.raise_for_status()

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
    """
    requests api to shut down/disconnect from the users app, if issue raised catch and add to log
    :return:
    """
    try:
        response = requests.get(f"{API_BASE}api/v2/actions/system/shutdown/", timeout=2.0)
        response.raise_for_status()

        if response.status_code == 200:
            print("disconnected :)")
            return True
        else:
            raise error.APIDisconnectionError(response.status_code)

    except error.APIDisconnectionError as e:
        print("Could not disconnect :(" + e.message)
        return False

#
# if __name__ == "__main__":
#     apiConnect()
#     camConnect()
