from pathlib import Path
import sys
# Ensure project root is on sys.path so `app` package can be imported when running the script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from app.image_classifier import classify_image
import csv

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "sample_properties.csv"


def main():
    rows = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            fn = r.get('image_filename')
            if not fn:
                continue
            img_path = IMAGES_DIR / fn
            label, score = classify_image(str(img_path))
            print(f"{fn}: -> {label} (score={score})")
            rows.append((fn, label, score))
    print('\nSummary:')
    counts = {}
    for _, l, _ in rows:
        counts[l] = counts.get(l, 0) + 1
    for k, v in counts.items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
