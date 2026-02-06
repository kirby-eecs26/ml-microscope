#count.py
#Takes img and analyzes to return  cell count in img
#ML edit

import numpy as np
import cv2
from dataclasses import dataclass
from typing import List, Optional
from backend.preprocess import preprocess


@dataclass
class CountResult:
    count: int
    areas: List[int]
    mask_u8: Optional[np.ndarray] = None
    overlay_bgr: Optional[np.ndarray] = None


def count_blobs(
    gray: np.ndarray,
    threshold: Optional[float] = None,
    min_area: int = 120,        #===== Will need to change depending on image, 900 seems to work good so far====
    max_area: Optional[int] = None,        #===Limit the max area=====
    debug: bool = False
) -> CountResult:

    gray_u8 = (np.clip(gray, 0.0, 1.0) * 255).astype(np.uint8)
    blur = cv2.GaussianBlur(gray_u8, (5, 5), 0)

    if threshold is None:
        _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        t = int(threshold * 255)
        _, mask = cv2.threshold(blur, t, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)     #Ignore tiny specs
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    areas: List[int] = []
    count = 0
    #====Create the overlay====
    overlay = None
    if debug:
        overlay = cv2.cvtColor(gray_u8, cv2.COLOR_GRAY2BGR)

    for i in range(1, num):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue

        count += 1
        areas.append(area)
        #=======Draw boxes and count=====
        if debug and overlay is not None:
            x = int(stats[i, cv2.CC_STAT_LEFT])
            y = int(stats[i, cv2.CC_STAT_TOP])
            w = int(stats[i, cv2.CC_STAT_WIDTH])
            h = int(stats[i, cv2.CC_STAT_HEIGHT])
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                overlay, str(count),
                (x, max(0, y - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA
            )

    if debug:
        return CountResult(count=count, areas=areas, mask_u8=mask, overlay_bgr=overlay)
    return CountResult(count=count, areas=areas)


def count_from_rgb(
    rgb_u8: np.ndarray,
    threshold: Optional[float] = None,
    min_area: int = 120,
    max_area: Optional[int] = None,
    debug: bool = False
) -> CountResult:

    gray_f32 = preprocess(rgb_u8)  # (H,W) float32 in [0,1]
    return count_blobs(
        gray_f32,
        threshold=threshold,
        min_area=min_area,
        max_area=max_area,
        debug=debug,
    )