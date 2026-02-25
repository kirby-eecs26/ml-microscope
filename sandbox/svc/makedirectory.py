from pathlib import Path
import requests
import os
import csv
from contextlib import chdir

# path = Path.cwd()
# # path.mkdir(parents=True, exist_ok=True)
# # path.rename(Path.cwd() / f"Images")
#
# os.mkdir("Images")
# print(f"Created local path: {path}")
#
#
# path = Path.cwd()
# imgpath = path / "Images"
# print(imgpath)
#
# with chdir(imgpath):
#     print(f"Created local path: {path}")
#
# print(f"Created local path: {path}")


# Works to make an empty txt file in users downloads :D
# then copy server file contexts to the users downloads
# still needs adjustments for the jpeg download to actually work
test_file = Path("C:/Users/ADRub/PycharmProjects/ml-microscope/sandbox/svc/test_file.txt")

downloads_path = Path.home() / "Downloads"
file_path = downloads_path / "new_test_file.txt"

# with test_file.open("r", encoding="utf-8") as src:
#     text = src.read()
#
# with file_path.open("w", encoding="utf-8") as dst:
#     dst.write(text)
#
#
# #for img download from http link
# test_img = "https://imgs.search.brave.com/jsMVnA-_wo6ijeniIUQwlGEQoryAdkf1uiLQwlTSdPw/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTMy/ODMzNjIwOS92ZWN0/b3IvcGxhbnQtY2Vs/bC1zdHJ1Y3R1cmUt/aWxsdXN0cmF0aW9u/LmpwZz9zPTYxMng2/MTImdz0wJms9MjAm/Yz02WUpCbWctb0xV/c1IyQUFnNzk3bjY1/b3RLUms0bVgyOTdY/WloxekJRdlk0PQ"
#
# response = requests.get(test_img)
# response.raise_for_status()
#
# # Get Downloads folder
# downloads = Path.home() / "Downloads"
#
# # File path
# file_path = downloads / "rando_plant_img.jpg"
#
# # Save JPEG
# with open(file_path, "wb") as f:
#     f.write(response.content)
#
# print(f"Saved to {file_path}")


#downloads_path = get_download_path()
test_csv = Path("C:/Users/ADRub/PycharmProjects/ml-microscope/sandbox/svc/testing.csv")
new_csv = downloads_path / f"test_csv.csv"
new_filetocsv = downloads_path / f"filetocsv.csv"


# FILE TO CSV DOWNLOAD
# text = []
#
# with test_file.open("r", encoding = "utf-8") as src:
#     data = src.readlines()
#
# for line in data:
#     text.append(line.strip("\n").split(" "))
#
# with new_filetocsv.open("w", encoding = "utf-8", newline = '') as dst:
#     writer = csv.writer(dst)
#     writer.writerows(text)


# CSV DOWNLOAD
# csv_text = []
# with test_csv.open("r", encoding = "utf-8", newline='') as src:
#     csvreader = csv.reader(src)
#     for row in csvreader:
#         csv_text.append(row)
#
#
# with new_csv.open("w", encoding = "utf-8", newline='') as dst:
#     writer = csv.writer(dst)
#     for row in csv_text:
#         writer.writerow(row)
#

new_dictfile = downloads_path / f"test_dictfile.csv"
test_dict = [{"hello": "world", "goodbye":"world"}, {"hello": "earth", "goodbye":"earth"}]
headers = []

for key, value in test_dict[0].items():
    headers.append(key)

print(headers)

with new_dictfile.open("w", encoding="utf-8", newline='') as dst:
    writer = csv.DictWriter(dst, fieldnames=headers)
    writer.writeheader()
    writer.writerows(test_dict)