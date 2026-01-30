# ======================================================================
# preprocess.py
#
# Image preprocessing module v1.0
# Converts input tensor from color JPEG to normalized grayscale tensor.
#
# Input:  (H x W x 3) uint8 RGB pixel data
# Output: (H x W) float32 normalized grayscale pixel data
# ======================================================================

import numpy as np

# TODO: v2.0: Add denoise, normalize, and sharpen filters
# TODO: v2.1: Add method arguments to adjust filter thresholds

def preprocess(rgb_u8: np.ndarray) -> np.ndarray:
    """
    Convert an RGB uint8 tensor to normalized grayscale float32.
    
    :param rgb_u8: RGB unit8 tensor (H, W, 3)
    :return: Grayscale tensor (H, W), normalized to [0.0, 1.0]
    """

    # Validate rgb_u8 tensor
    if rgb_u8.ndim != 3 or rgb_u8.shape[2] != 3:
        raise ValueError(
        f"Invalid shape={rgb_u8.shape}; Expected shape=(H, W, 3)"
    )
    if rgb_u8.dtype != np.uint8:
        raise ValueError(
        f"Invalid dtype={rgb_u8.dtype}; Expected dtype=uint8"
    )

    # Convert to grayscale float32
    rgb_f32 = rgb_u8.astype(np.float32)

    # Desaturate pixel values using NTSC standards
    # gray = 0.299 R + 0.587 G + 0.114 B
    gray_f32 = (
        0.299 * rgb_f32[:, :, 0] +
        0.587 * rgb_f32[:, :, 1] +
        0.114 * rgb_f32[:, :, 2]
    )

    # Normalize values: [0, 255] -> [0.0, 1.0] 
    gray_f32 = gray_f32 / 255.0

    # Clamp outlying values
    gray_f32 = np.clip(gray_f32, 0.0, 1.0).astype(np.float32)

    return gray_f32
