from PIL import Image, ImageFilter, ImageDraw
import numpy as np
from typing import Tuple

# A small, dependency-light heuristic image classifier to detect common inspection defects.
# Returns (label, score) where label is one of: crack, leak, damp, mold, exposed_wiring, ok

LABELS = ["crack", "leak", "damp", "mold", "exposed_wiring", "ok"]
SEVERITY = {
    "crack": 0.6,
    "leak": 1.0,
    "damp": 0.9,
    "mold": 1.0,
    "exposed_wiring": 1.2,
    "ok": 0.0,
}


def _load_image_as_gray_np(path: str) -> np.ndarray:
    img = Image.open(path).convert("L")
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr


def _percent_dark(arr: np.ndarray, threshold=0.35) -> float:
    # proportion of pixels darker than threshold
    return float((arr < threshold).mean())


def _sobel_edge_strength(arr: np.ndarray) -> float:
    # simple sobel kernels for edge magnitude
    kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32)
    ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
    from scipy import ndimage
    gx = ndimage.convolve(arr, kx, mode='reflect')
    gy = ndimage.convolve(arr, ky, mode='reflect')
    mag = np.hypot(gx, gy)
    return float(mag.mean())


def classify_image(path: str) -> Tuple[str, float]:
    """Heuristic classification. Returns (label, score).

    Uses simple pixel stats and edge strength to identify likely defects.
    This is a prototype; replace with ML/Snowflake Cortex for production.
    """
    try:
        arr = _load_image_as_gray_np(path)
    except Exception:
        return "ok", 0.0

    dark_pct = _percent_dark(arr, threshold=0.4)
    # average brightness
    mean_b = float(arr.mean())

    # Edge detection (requires scipy.ndimage); if not available, approximate with PIL filter
    try:
        edge_strength = _sobel_edge_strength(arr)
    except Exception:
        # fallback: use PIL's FIND_EDGES filter
        try:
            img = Image.open(path).convert("L")
            edges = img.filter(ImageFilter.FIND_EDGES)
            edges_np = np.asarray(edges).astype(np.float32) / 255.0
            edge_strength = float(edges_np.mean())
        except Exception:
            edge_strength = 0.0

    # Heuristics
    # 1) Large dark area => damp or leak (if mean brightness low and dark pct high)
    if dark_pct > 0.08 and mean_b < 0.7:
        # distinguish damp vs leak by darkness and edge_strength (leaks often have irregular stain)
        if dark_pct > 0.2 or mean_b < 0.5:
            return "leak", SEVERITY["leak"]
        return "damp", SEVERITY["damp"]

    # 2) Strong edge strength with thin linear features => crack
    if edge_strength > 0.07 and edge_strength < 0.25:
        return "crack", SEVERITY["crack"]

    # 3) Very high edge strength and many bright thin lines => exposed wiring
    if edge_strength >= 0.25:
        # further differentiate by looking for bright thin line proportion
        img = Image.open(path).convert("L")
        arr2 = np.asarray(img).astype(np.float32) / 255.0
        bright_pct = float((arr2 > 0.85).mean())
        if bright_pct > 0.001:
            return "exposed_wiring", SEVERITY["exposed_wiring"]
        return "crack", SEVERITY["crack"]

    # 4) mold detection is hard; approximate by speckled darker pixels
    if dark_pct > 0.05 and edge_strength < 0.03:
        return "mold", SEVERITY["mold"]

    return "ok", SEVERITY["ok"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m app.image_classifier <image-path>")
    else:
        print(classify_image(sys.argv[1]))
