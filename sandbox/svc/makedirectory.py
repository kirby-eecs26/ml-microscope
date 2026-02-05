from pathlib import Path
import os
from contextlib import chdir

# path = Path.cwd()
# path.mkdir(parents=True, exist_ok=True)
# path.rename(Path.cwd() / f"Images")

#os.mkdir("Images")
# print(f"Created local path: {path}")


path = Path.cwd()
imgpath = path / "Images"
print(imgpath)

with chdir(imgpath):
    print(f"Created local path: {path}")

print(f"Created local path: {path}")