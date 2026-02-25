#save.py
#saves img and vid files locally

from pathlib import Path
import requests
from libraries.GlobalVariables import API_BASE
import csv

def get_download_path() -> Path | None:
    """find users home downloads folder or make one if does not exist
    :return: Path to folder where downloaded files are located"""

    try:
        path = Path.home() / "Downloads"
        path.mkdir(exist_ok=True) # incase home downloads dont exist
        return path

    except FileNotFoundError as e:
        print(f"{e.__str__()}: Downloads folder not found")

def download_analysis(capture_id):
    """
    takes in a name for the new download file and a path to the local analysis csv file and copies
    data (saves) file data to users home download folder
    :param file_name:
    :param file_data:
    :return:
    """
    try:
        downloads_folder = get_download_path()
        capture_data = get_capture(capture_id)
        capture_data.raise_for_status()

        new_file = f"{downloads_folder}/{capture_data.name}.csv"
        annotations = []
        annotations.append(capture_data.annotations)
        headers = []

        for key, value in annotations[0].items():
            headers.append(key)

        # with file_data.open("r", encoding = "utf-8") as src:
        #     text = src.read()

        with new_file.open("w", encoding = "utf-8", newline = '') as dst:
            writer = csv.DictWriter(dst, fieldnames = headers)
            writer.writeheader()
            writer.writerows(annotations)

    except Exception as e:
        print("file failed to download")


def download_image(capture_id):
    """
    takes the capture id and gets images from the local pi then copies (saves) the image data
    to the users home downloads file
    catch exceptions and add them to logging
    todo: add exceptions to logging
    :param capture_id:
    :return: N/A
    """
    try:
        downloads_folder = get_download_path()

        capture_data = get_capture(capture_id)
        capture_data.raise_for_status()

        img_link = f"{API_BASE}{capture_data.path}"
        img_data = requests.get(img_link)
        img_data.raise_for_status()

        download_img = f"{downloads_folder}/{capture_data.name}"

        with open(download_img, "wb") as f:
            f.write(img_data.content)

    except requests.RequestException as e:
        print("Image request failed: Could not save image")

    except Exception as e:
        print(e.__str__())


def get_capture(capture_id, timeout=2.0):
    """ DOES NOT WORK
    takes in capture id to get image from the local pi then returns image
    todo: fix get image access not using right access link or api calls, add exception handling to logging
    :param capture_id:
    :param timeout:
    :return:
    """
    try:
        r = requests.get(f"{API_BASE}api/v2/captures/{capture_id}", timeout=timeout)
        r.raise_for_status()
        return r.json()

    except requests.RequestException as e:
        print("Capture request failed: Could not download image")