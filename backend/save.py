#save.py
#saves img and vid files locally

from pathlib import Path
import os
from contextlib import chdir

import requests

from libraries.GlobalVariables import API_BASE


def create_local_path() -> str:
    os.mkdir("images")
    path = Path.cwd()

    with chdir(f"{path}/images"):
        print(f"Created local path: {path}")

    return f"{path}/images"

def download_image(capture_id):
    capture_id = get_capture(capture_id)



def get_capture(capture_id, timeout=2.0):
    r = requests.get(f"{API_BASE}api/v2/captures/{capture_id}", timeout=timeout)
    r.raise_for_status()
    return r.json()