# ======================================================================
# image_io.py
#
# Helper module for preprocess_test.py
# Creates test input RGB NumPy tensors from color JPEG images.
# Creates optional NumPy and B&W JPEG output for validation.
#
# Input:  Color JPEG image or NumPy tensor
# Output: NumPy tensor (shape/dtype agnostic) or B&W JPEG image.
# ======================================================================

import os
import numpy as np
import cv2 # opencv-python-headless


# ======================================================================
# Load and Save JPEG files.
# ======================================================================

def load_input_image(img_path: str) -> np.ndarray:
    """
    Load a color JPEG image and return an RGB NumPy tensor.
    
    :param img_path: Path to input JPEG image
    :return: RGB img tensor (H, W, 3)
    """

    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"Image file not found: {img_path}")

    bgr = cv2.imread(img_path, cv2.IMREAD_COLOR) # (H, W, 3) uint8 BGR

    if bgr is None:
        raise ValueError(f"Failed to decode image: {img_path}")

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) # BGR -> RGB

    return rgb


def save_output_image(gray_f32: np.ndarray, out_path: str) -> None:
    """
    Export normalized grayscale NumPy tensor as B&W JPEG file.
    
    :param gray_f32: float32 tensor 
    :param out_path: Path to output JPEG file
    """

    # Validate float32 tensor
    assert gray_f32.ndim == 2, (
        f"Invalid shape={gray_f32.shape}; Expected 2D array"
    )
    assert gray_f32.dtype == np.float32, (
        f"Invalid dtype={gray_f32.dtype}; Expected dtype=float32"
    )
    assert 0.0 <= gray_f32.min() <= gray_f32.max() <= 1.0, (
        "Invalid value range; Expected range=[0.0, 1.0]"
    )
    
    # Convert from float32 [0.0, 1.0] to uint8 [0, 255]
    img_u8 = (gray_f32 * 255.0).round().astype(np.uint8)

    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    ok = cv2.imwrite(out_path, img_u8)
    assert ok, f"Failed to save image: {out_path}"


# ======================================================================
# Load and Save NumPy tensor .npy files.
# ======================================================================

def load_tensor_npy(path: str) -> np.ndarray:
    """
    Import a NumPy tensor from a .npy file.
    
    :param path: Path to input .npy file
    :return: Loaded NumPy array
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f".npy file not found: {path}")

    return np.load(path)


def save_tensor_npy(tensor: np.ndarray, out_path: str) -> None:
    """
    Export NumPy tensor to .npy file.
    
    :param tensor: NumPy array (shape/dtype agnostic)
    :param out_path: Path to output .npy file
    """

    out_dir = os.path.dirname(out_path)
    
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    np.save(out_path, tensor)


# ======================================================================
# JPEG file validation
# ======================================================================

def _is_image_file(name: str) -> bool:
    """
    Confirm whether a file is a JPEG.

    :param name: Filename
    """
    ext = os.path.splitext(name)[1].lower()
    return ext in (".jpg", ".jpeg")
