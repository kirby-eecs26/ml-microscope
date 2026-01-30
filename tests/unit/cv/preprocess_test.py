# ======================================================================
# preprocess_test.py
#
# Test module for preprocess.py
#
# Input: Color JPEG files
# Output: B&W JPEG files
# ======================================================================

import os
import numpy as np

from image_io import load_input_image, save_input_data, save_output_image
#from backend.preprocess import preprocess

BASE_DIR = "tests/unit/cv"

INPUT_DATA_DIR = f"{BASE_DIR}/input/data"
INPUT_IMG_DIR = f"{BASE_DIR}/input/img"
INPUT_DTYPE = np.uint8
INPUT_CHANNELS = 3
INPUT_RANGE = (0, 255)

OUTPUT_DATA_DIR = f"{BASE_DIR}/output/data"
OUTPUT_IMG_DIR = f"{BASE_DIR}/output/img"
OUTPUT_DTYPE = np.float32
OUTPUT_CHANNELS = 1
OUTPUT_RANGE = (0.0, 1.0)

IMG_HEIGHT = 2464
IMG_WIDTH = 3280


# ======================================================================
#
# Create preprocessor.py input RGB .npy file from JPEG file.
#
# ======================================================================

# TODO: Replace single image test with batch processing.

input_img_name = "input01.jpeg"

input_img_path = os.path.join(INPUT_IMG_DIR, input_img_name)

data_path = os.path.join(
    INPUT_DATA_DIR, os.path.splitext(input_img_name)[0] + ".npy"
)

rgb_tensor = load_input_image(input_img_path)

# Validate rgb_tensor
assert rgb_tensor.shape == (IMG_HEIGHT, IMG_WIDTH, 3), (
    f"Invalid shape={rgb_tensor.shape}; "
    f"Expected shape=({IMG_HEIGHT}, {IMG_WIDTH}, 3)"
)
assert rgb_tensor.dtype == np.uint8, (
    f"Invalid dtype={rgb_tensor.dtype}; Expected dtype=uint8"
)

save_input_data(rgb_tensor, data_path)

# ======================================================================
#
# Test preprocess.py module.
#
# ======================================================================

output_data_name = "output01.npy"


# ======================================================================
#
# Convert preprocessor.py output to JPEG file for validation
#
# ======================================================================

out_data_path = os.path.join(OUTPUT_DATA_DIR, output_data_name)

out_data_path = os.path.join(OUTPUT_DATA_DIR, output_data_name)
output_img_path = os.path.join(
    OUTPUT_IMG_DIR, os.path.splitext(output_data_name)[0] + ".jpeg"
)

gray_tensor = np.load(out_data_path)

save_output_image(gray_tensor, output_img_path)