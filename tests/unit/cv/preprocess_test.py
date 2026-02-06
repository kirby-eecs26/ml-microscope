# ======================================================================
# preprocess_test.py
#
# Test module for preprocess.py
# Creates RGB input tensors for preprocess.py testing. 
# Convert input to normalized grayscale output tensors.
# Optional exports for .npy files and grayscale JPEG files.
#
# Input: Color JPEG files
# Output: I/O tensors, .npy exports, and B&W JPEG files
# ======================================================================

#TODO: v2.0: Create output batches with different filter settings.
#TODO: v2.1: Replicate v2.0 tests with frontend arguments.

import os
import sys

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402
from image_io import load_input_image, save_tensor_npy, save_output_image, _is_image_file  # noqa: E402
from backend.preprocess import preprocess  # noqa: E402

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
# Validate input files and intiate batch testing loop.
# ======================================================================

# Confirm output target paths
os.makedirs(INPUT_IMG_DIR, exist_ok=True)
os.makedirs(INPUT_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

input_files = sorted( # Confirm JPEG input files
    f for f in os.listdir(INPUT_IMG_DIR)
    if os.path.isfile(os.path.join(INPUT_IMG_DIR, f)) and _is_image_file(f)
)

assert len(input_files) > 0, (
    f"No input images found in: {INPUT_IMG_DIR}"
)

for idx, input_img_name in enumerate(input_files, start=1):
    input_img_path = os.path.join(INPUT_IMG_DIR, input_img_name)

    output_tag = f"output{idx:02d}" # Set output filename

    # Print current file to console.
    print(f"[{idx}/{len(input_files)}] Processing: {input_img_name}")

    # ----------------------------------------------------------------------
    # Create and validate preprocessor.py input tensor from JPEG file.
    # ----------------------------------------------------------------------

    rgb_tensor = load_input_image(input_img_path)

    assert rgb_tensor.shape == (IMG_HEIGHT, IMG_WIDTH, INPUT_CHANNELS), (
        f"{input_img_name}: Invalid shape={rgb_tensor.shape}; "
        f"Expected shape=({IMG_HEIGHT}, {IMG_WIDTH}, {INPUT_CHANNELS})"
    )
    assert rgb_tensor.dtype == INPUT_DTYPE, (
        f"{input_img_name}: Invalid dtype={rgb_tensor.dtype}; Expected dtype={INPUT_DTYPE}"
    )
    assert INPUT_RANGE[0] <= rgb_tensor.min() <= rgb_tensor.max() <= INPUT_RANGE[1], (
    f"{input_img_name}: Invalid value range; Expected range={INPUT_RANGE}"
    )

    # Export rgb_tensor to .npy file for testing/debugging.
    input_data_path = os.path.join(
        INPUT_DATA_DIR, os.path.splitext(input_img_name)[0] + ".npy"
    )
    save_tensor_npy(rgb_tensor, input_data_path)

    # ----------------------------------------------------------------------
    # Test preprocess.py module and validate output.
    # ----------------------------------------------------------------------

    #gray_tensor = preprocess(rgb_tensor)

    gray_tensor = preprocess(
        rgb_tensor,
        denoise_radius=6,
        sharpen_radius=2,
        sharpen_magnitude=0.5,
        contrast=0.2,
    )

    assert gray_tensor.shape == (IMG_HEIGHT, IMG_WIDTH), (
        f"{output_tag}: Invalid shape={gray_tensor.shape}; "
        f"Expected shape=({IMG_HEIGHT}, {IMG_WIDTH})"
    )
    assert gray_tensor.dtype == OUTPUT_DTYPE, (
        f"{output_tag}: Invalid dtype={gray_tensor.dtype}; Expected dtype={OUTPUT_DTYPE}"
    )
    assert OUTPUT_RANGE[0] <= gray_tensor.min() <= gray_tensor.max() <= OUTPUT_RANGE[1], (
        f"{output_tag}: Invalid value range; Expected range={OUTPUT_RANGE}"
    )

    # ----------------------------------------------------------------------
    # Save preprocessor.py output as .npy and JPEG files for validation.
    # ----------------------------------------------------------------------

    output_data_path = os.path.join(OUTPUT_DATA_DIR, f"{output_tag}.npy")
    output_img_path = os.path.join(OUTPUT_IMG_DIR, f"{output_tag}.jpeg")

    save_tensor_npy(gray_tensor, output_data_path)
    save_output_image(gray_tensor, output_img_path)
 
print(f"Testing completed. Processed {len(input_files)} image(s).")
