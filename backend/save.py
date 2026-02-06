#save.py
#saves img and vid files locally

from pathlib import Path
import os
from contextlib import chdir
import requests
from libraries.GlobalVariables import API_BASE

# def create_local_path() -> str:
#     os.mkdir("images")
#     path = Path.cwd()
#
#     with chdir(f"{path}/images"):
#         print(f"Created local path: {path}")
#
#     return f"{path}/images"

def get_download_path() -> Path | None:
    """find users home downloads folder or make one if does not exist
    :returns Path to folder where downloaded files are located"""

    try:
        path = Path.home() / "Downloads"
        path.mkdir(exist_ok=True) # incase home downloads dont exist
        return path

    except FileNotFoundError as e:
        print(f"{e.__str__()}: Downloads folder not found")


def download_image(capture_id):
    try:
        downloads = get_download_path()

        capture_data = get_capture(capture_id)
        capture_data.raise_for_status()

        img_link = f"{API_BASE}{capture_data.path}"
        img_data = requests.get(img_link)
        img_data.raise_for_status()

        download_img = f"{downloads}/{capture_data.name}"

        with open(download_img, "wb") as f:
            f.write(img_data.content)

    except requests.RequestException as e:
        print("Image request failed: Could not save image")

    except Exception as e:
        print(e.__str__())


def get_capture(capture_id, timeout=2.0):
    try:
        r = requests.get(f"{API_BASE}api/v2/captures/{capture_id}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print("Capture request failed: Could not download image")