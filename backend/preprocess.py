# ======================================================================
# preprocess.py
#
# Image preprocessing module v2.1
# v1.0: Converts input tensor from color JPEG to optimized grayscale.
# v2.0: Includes filters for brightness, contrast, denoise, and sharpen.
# v2.1: Accepts arguments for filter levels
#
# Input:  (H x W x 3) uint8 RGB pixel data
# Output: (H x W) float32 normalized grayscale pixel data
# ======================================================================

import numpy as np

def _box_blur(img_f32: np.ndarray, blur_radius: int) -> np.ndarray:
    """
    (k x k) box blur for a single-channel float32 image.

    :param img_f32: (H, W) float32
    :return: (H, W) float32 blurred
    """
    if img_f32.ndim != 2:
        raise ValueError(
            f"Invalid shape={img_f32.shape}; Expected shape=(H, W)"
        )
    if not isinstance(blur_radius, int):
        raise TypeError(
            f"Invalid blur_radius type={type(blur_radius)}; Expected int"
        )
    if not (0 <= blur_radius <= 10):
        raise ValueError(
            f"Invalid blur_radius={blur_radius}; Expected range [0, 10]"
        )
    if blur_radius == 0:
        return img_f32.astype(np.float32)

    # Kernel (k) size
    k = 2 * blur_radius + 1

    # Padding to handle borders
    padding = np.pad(img_f32, ((blur_radius, blur_radius), (blur_radius, blur_radius)), mode="edge").astype(np.float32)

    # integral image (ii) with a leading 0 row/col so window sums line up
    ii = np.pad(
        np.cumsum(np.cumsum(padding, axis=0), axis=1),
        ((1, 0), (1, 0)),
        mode="constant",
        constant_values=0.0
    )
    # Sum over (k x k) windows, output is (H, W)
    s = ii[k:, k:] - ii[:-k, k:] - ii[k:, :-k] + ii[:-k, :-k]

    out = s / (k * k)

    return out.astype(np.float32)


def _brightness_filter(img_f32: np.ndarray, brightness: float) -> np.ndarray:
    """
    Adjustable brightness/darkness filter

    :param img_f32: (H, W) float32
    :param brightness: Brightness strength [-1.0, 1.0]
        (-1.0) = very dark; 0.0 = no filter; 1.0 = very bright
    :return: (H, W) float32 with adjusted brightness/darkness
    """
    if not (-1.0 <= brightness <= 1.0):
        raise ValueError(
            f"Invalid brightness={brightness}; Expected range [-1.0, 1.0]"
        )
    return (img_f32 + brightness).astype(np.float32)


def _contrast_filter(img_f32: np.ndarray, contrast: float) -> np.ndarray:
    """
    Adjustable contrast filter, centered at image mean
    
    :param img_f32: (H, W) float32
    :param contrast: Constrast strength [-1.0, 1.0]
        (-1.0) = flat gray; 0.0 = no filter; 1.0 = high contrast
    :return: (H, W) float32 with contrast adjustment
    """
    if not (-1.0 <= contrast <= 1.0):
        raise ValueError(
            f"Invalid contrast={contrast}; Expected range [-1.0, 1.0]"
        )
    mean = img_f32.mean(dtype=np.float32)
    scale = 1.0 + contrast

    out = (img_f32 - mean) * scale + mean
    return out.astype(np.float32)


def _denoise_filter(img_f32: np.ndarray, denoise_radius: int) -> np.ndarray:
    """
    Adjustable denoise filter.

    :param img_f32: (H, W) float32
    :param denoise_radius: Denoise radius [0, 10]
        0 = no filter; 10 = very blurry
    :return: denoised (H, W) float32
    """
    if not isinstance(denoise_radius, int):
        raise TypeError(
            f"Invalid denoise type={type(denoise_radius)}; Expected int"
        )
    if not (0 <= denoise_radius <= 10):
        raise ValueError(
            f"Invalid denoise_radius={denoise_radius}; Expected range [0, 10]"
        )
    return _box_blur(img_f32, denoise_radius)


def _sharpen_filter(img_f32: np.ndarray, sharpen_magnitude: float, sharpen_radius: int) -> np.ndarray:
    """
    Docstring for _sharpen_filter
    
    :param img_f32: (H, W) float32
    :param sharpen_magnitude: Gain scalar [0.0, 1.0]
    :param sharpen_radius: Sharpness radius [0, 10]
        (magnitude = 0.0 & radius = 0) -> no filter
    :return: sharpened (H, W) float32

    Suggested usage:
    - Start with mag = 0.5 and radius = 2
    - Sweep magnitude value first
    - If needed, change radius, reset mag to 0.5, and repeat
    """
    GAIN = 5.0

    if not (0.0 <= sharpen_magnitude <= 1.0):
        raise ValueError(
            f"Invalid sharpen_magnitude={sharpen_magnitude}; Expected range [0.0, 1.0]"
        )
    if not (0 <= sharpen_radius <= 10):
        raise ValueError(
            f"Invalid sharpen_radius={sharpen_radius}; Expected range [0, 10]"
        )
    if sharpen_magnitude == 0.0 or sharpen_radius == 0:
        return img_f32.astype(np.float32)

    blur = _box_blur(img_f32, sharpen_radius)

    sharpen_gain = GAIN * sharpen_magnitude

    out = img_f32 + sharpen_gain * (img_f32 - blur)
    return out.astype(np.float32)


def preprocess(
    rgb_u8: np.ndarray,
    *,
    brightness: float = 0.0,
    contrast: float = 0.0,
    denoise_radius: int = 0,
    sharpen_magnitude: float = 0.0,
    sharpen_radius: int = 0,
) -> np.ndarray:
    """
    Convert an RGB uint8 tensor to an optimized grayscale float32.

    All filter parameters are optional and default to identity behavior.

    :param rgb_u8: RGB uint8 tensor (H, W, 3)
    :param brightness: Brightness offset [-1.0, 1.0]
    :param contrast: Contrast adjustment [-1.0, 1.0]
    :param denoise_radius: Denoise blur radius [0, 10]
    :param sharpen_magnitude: Sharpen gain [0.0, 1.0]
    :param sharpen_radius: Sharpen blur radius [0, 10]
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

    # Convert to RGB float32
    rgb_f32 = rgb_u8.astype(np.float32)

    # Desaturate pixel values using NTSC standards
    # gray = 0.299 R + 0.587 G + 0.114 B
    gray_f32 = (
        0.299 * rgb_f32[:, :, 0] +
        0.587 * rgb_f32[:, :, 1] +
        0.114 * rgb_f32[:, :, 2]
    ).astype(np.float32)

    # Normalize values: [0, 255] -> [0.0, 1.0] 
    gray_f32 = (gray_f32 / 255.0).astype(np.float32)

    # Clamp outlying values before applying filters
    gray_f32 = np.clip(gray_f32, 0.0, 1.0).astype(np.float32)

    # ----------------------------------------------------------------------
    # Apply filters: Denoise, sharpen, brightness, and contrast.
    # ----------------------------------------------------------------------

    denoised = _denoise_filter(gray_f32, denoise_radius)
    sharpened = _sharpen_filter(denoised, sharpen_magnitude, sharpen_radius)
    contrasted = _contrast_filter(sharpened, contrast)
    brightened = _brightness_filter(contrasted, brightness)

    # Clamp before final output
    preprocess_out = np.clip(brightened, 0.0, 1.0).astype(np.float32)

    return preprocess_out