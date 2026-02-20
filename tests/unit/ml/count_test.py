import cv2
from backend.count import count_from_rgb

img = cv2.imread("tests/unit/ml/output14.jpeg")
if img is None:
    raise RuntimeError("Could not load image")

rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

result = count_from_rgb(rgb, debug=True, min_area=900)

print("Blob count:", result.count)
print("Areas (first 10):", result.areas[:10])

cv2.imwrite("tests/unit/ml/debug_mask.png", result.mask_u8)
cv2.imwrite("tests/unit/ml/debug_overlay.png", result.overlay_bgr)
