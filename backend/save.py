#save.py
#saves img and vid files locally

from pathlib import Path
import os
from contextlib import chdir


def create_local_path() -> str:
    os.mkdir("images")
    path = Path.cwd()

    with chdir(f"{path}/images"):
        print(f"Created local path: {path}")

    return f"{path}/images"

def download_image():
    i = 0