#save.py
#saves img and vid files locally

from pathlib import Path
import os
from contextlib import chdir


def create_local_path() -> Path:
    os.mkdir("Images")
    path = Path.cwd()

    with chdir(f"{path}/Images"):
        print(f"Created local path: {path}")

    return path

