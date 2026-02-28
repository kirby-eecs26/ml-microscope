# motion.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

import cv2
import numpy as np


@dataclass
class MotionConfig:
    # How many frames per second to sample from the video for analysis
    sample_fps: float = 10.0

    # Resize frames to speed up analysis (set None to disable)
    resize_max_width: Optional[int] = 640

    # Gaussian blur kernel size (must be odd)
    blur_ksize: int = 7

    # Pixel difference threshold (0-255) for motion mask
    diff_thresh: int = 20

    # Morphology to denoise the motion mask
    morph_open_iter: int = 1
    morph_close_iter: int = 2

    # Ignore tiny blobs in motion mask (in pixels)
    min_blob_area: int = 60

    # Convert motion_score -> label using this threshold (baseline)
    label_threshold: float = 0.02  # default: 2% of pixels moving on average

    # A "motile object" is a blob whose centroid moves more than this between frames (in px)
    # NOTE: This is only a proxy without real tracking.
    motile_blob_disp_thresh_px: float = 2.5


def _maybe_resize(frame_bgr: np.ndarray, max_w: Optional[int]) -> np.ndarray:
    if not max_w:
        return frame_bgr
    h, w = frame_bgr.shape[:2]
    if w <= max_w:
        return frame_bgr
    scale = max_w / float(w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(frame_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _to_gray_blur(frame_bgr: np.ndarray, blur_ksize: int) -> np.ndarray:
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    k = blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1
    return cv2.GaussianBlur(gray, (k, k), 0)


def _motion_mask(
    prev_g: np.ndarray,
    curr_g: np.ndarray,
    diff_thresh: int,
    open_iter: int,
    close_iter: int,
) -> np.ndarray:
    diff = cv2.absdiff(curr_g, prev_g)
    _, mask = cv2.threshold(diff, diff_thresh, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    if open_iter > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=open_iter)
    if close_iter > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=close_iter)
    return mask


def _extract_centroids(mask: np.ndarray, min_area: int) -> List[Tuple[float, float]]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cents: List[Tuple[float, float]] = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        M = cv2.moments(c)
        if M["m00"] <= 0:
            continue
        cx = float(M["m10"] / M["m00"])
        cy = float(M["m01"] / M["m00"])
        cents.append((cx, cy))
    return cents


def _nearest_neighbor_displacements(
    prev_pts: List[Tuple[float, float]],
    curr_pts: List[Tuple[float, float]],
) -> List[float]:
    if not prev_pts or not curr_pts:
        return []

    prev = np.array(prev_pts, dtype=np.float32)  # (N,2)
    curr = np.array(curr_pts, dtype=np.float32)  # (M,2)

    dists = np.linalg.norm(prev[:, None, :] - curr[None, :, :], axis=2)  # (N,M)
    nn = dists.min(axis=0)  # (M,)
    return nn.tolist()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def classify_motion_kmeans(
    motion_score: float,
    avg_speed_px_per_s: float,
    tracks: int,
) -> Dict[str, Any]:
    """
    Option A: "light ML"
    - Use KMeans(2) on a small synthetic dataset in feature space
      so no training data is required.
    - Then classify the observed feature vector by cluster.
    """
    # If sklearn isn't installed, return a graceful fallback.
    try:
        from sklearn.cluster import KMeans  # type: ignore
    except Exception as e:
        return {
            "method": "kmeans",
            "enabled": False,
            "reason": f"scikit-learn not available ({e})",
            "label": None,
        }

    # Feature vector
    X = np.array([[motion_score, avg_speed_px_per_s, float(tracks)]], dtype=np.float32)

    # Synthetic "training" points that roughly cover expected ranges.
    # (motion_score ~ 0..0.15), (avg_speed ~ 0..8 px/s), (tracks ~ 0..50)
    synth = np.array(
        [
            [0.000, 0.05, 0.0],   # very static
            [0.004, 0.20, 1.0],
            [0.010, 0.60, 5.0],   # low motion
            [0.020, 1.20, 10.0],  # borderline
            [0.040, 2.80, 18.0],  # motile
            [0.070, 4.50, 28.0],
            [0.110, 6.50, 40.0],  # very motile
        ],
        dtype=np.float32,
    )

    km = KMeans(n_clusters=2, n_init=10, random_state=0)
    km.fit(synth)

    pred = int(km.predict(X)[0])
    centers = km.cluster_centers_

    # Pick which cluster corresponds to "motile":
    # we assume the "motile" cluster has higher motion_score center.
    motile_cluster = int(np.argmax(centers[:, 0]))
    label = "MOTILE" if pred == motile_cluster else "STATIC"

    # Confidence-ish score: distance ratio to the two centers
    d0 = float(np.linalg.norm(X[0] - centers[0]))
    d1 = float(np.linalg.norm(X[0] - centers[1]))
    # smaller distance => higher confidence; clamp into [0,1]
    denom = (d0 + d1) if (d0 + d1) > 1e-9 else 1.0
    confidence = 1.0 - (min(d0, d1) / denom)

    return {
        "method": "kmeans",
        "enabled": True,
        "label": label,
        "pred_cluster": pred,
        "motile_cluster": motile_cluster,
        "cluster_centers": centers.tolist(),
        "distances": {"c0": d0, "c1": d1},
        "confidence": round(confidence, 4),
        "features": {
            "motion_score": float(X[0, 0]),
            "avg_speed_px_per_s": float(X[0, 1]),
            "tracks": int(round(X[0, 2])),
        },
    }


def analyze_motion(
    video_path: str,
    cfg: Optional[MotionConfig] = None,
    mode: str = "cv",  # "cv" or "ml_kmeans"
) -> Dict[str, Any]:
    """
    Analyze video motion and return an interpretable summary.

    CV baseline:
    - motion_score: avg fraction of pixels classified as moving
    - motility_ratio: fraction of blobs whose centroid displacement is above a threshold
      (proxy; not full tracking)
    - avg_speed_px_per_s: based on centroid displacement per frame * sample_fps
      (proxy; not full tracking)
    - tracks: approximate number of moving blobs detected per frame (avg)

    ML mode ("ml_kmeans"):
    - Uses k-means classification on the computed features.
    """
    cfg = cfg or MotionConfig()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    if fps <= 0:
        fps = 30.0

    step = max(int(round(fps / cfg.sample_fps)), 1)

    prev_g = None
    frame_idx = 0

    motion_scores: List[float] = []
    blob_counts: List[int] = []

    motile_blob_hits = 0
    motile_blob_total = 0
    disp_accum: List[float] = []

    prev_centroids: List[Tuple[float, float]] = []

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx % step != 0:
            frame_idx += 1
            continue

        frame = _maybe_resize(frame, cfg.resize_max_width)
        curr_g = _to_gray_blur(frame, cfg.blur_ksize)

        if prev_g is None:
            prev_g = curr_g
            prev_centroids = []
            frame_idx += 1
            continue

        mask = _motion_mask(
            prev_g,
            curr_g,
            cfg.diff_thresh,
            cfg.morph_open_iter,
            cfg.morph_close_iter,
        )

        motion_score = float(np.count_nonzero(mask)) / float(mask.size)
        motion_scores.append(motion_score)

        centroids = _extract_centroids(mask, cfg.min_blob_area)
        blob_counts.append(len(centroids))

        disps = _nearest_neighbor_displacements(prev_centroids, centroids)
        if disps:
            for d in disps:
                motile_blob_total += 1
                if d >= cfg.motile_blob_disp_thresh_px:
                    motile_blob_hits += 1
            disp_accum.extend(disps)

        prev_centroids = centroids
        prev_g = curr_g
        frame_idx += 1

    cap.release()

    motion_mean = float(np.mean(motion_scores)) if motion_scores else 0.0
    tracks_mean = float(np.mean(blob_counts)) if blob_counts else 0.0
    motility_ratio = (motile_blob_hits / motile_blob_total) if motile_blob_total > 0 else 0.0
    avg_disp = float(np.mean(disp_accum)) if disp_accum else 0.0
    avg_speed = avg_disp * cfg.sample_fps

    # CV baseline label
    cv_label = "MOTILE" if motion_mean >= cfg.label_threshold else "STATIC"

    analysis: Dict[str, Any] = {
        "type": "motion_tracking" if mode == "cv" else "motion_tracking_ml",
        "motility_ratio": round(motility_ratio, 4),
        "motion_score": round(motion_mean, 4),
        "avg_speed_px_per_s": round(avg_speed, 3),
        "tracks": int(round(tracks_mean)),
        "label": cv_label,  # may be overridden by ML mode
        "debug": {
            "mode": mode,
            "sample_fps": cfg.sample_fps,
            "diff_thresh": cfg.diff_thresh,
            "label_threshold": cfg.label_threshold,
            "min_blob_area": cfg.min_blob_area,
            "motile_blob_disp_thresh_px": cfg.motile_blob_disp_thresh_px,
            "resize_max_width": cfg.resize_max_width,
        },
    }

    if mode == "ml_kmeans":
        ml = classify_motion_kmeans(
            motion_score=_safe_float(motion_mean),
            avg_speed_px_per_s=_safe_float(avg_speed),
            tracks=int(round(tracks_mean)),
        )
        analysis["ml"] = ml

        # If ML is enabled, use its label; otherwise keep CV label.
        if ml.get("enabled") and ml.get("label"):
            analysis["label"] = ml["label"]

    return {"analysis": analysis}