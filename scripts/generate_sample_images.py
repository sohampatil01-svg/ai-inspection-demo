from PIL import Image, ImageDraw
import os
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
IMAGES_DIR = DATA_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

LABEL_MAP = {
    "ok": "ok",
    "exposed_wiring": "exposed_wiring",
    "wiring": "exposed_wiring",
    "leak": "leak",
    "damp": "damp",
    "crack": "crack",
    "mold": "mold",
}


def make_ok(path):
    img = Image.new("RGB", (800, 600), color=(240, 240, 235))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "OK - no issues", fill=(30, 30, 30))
    img.save(path)


def make_damp(path):
    img = Image.new("RGB", (800, 600), color=(230, 230, 230))
    draw = ImageDraw.Draw(img)
    # draw a dark irregular stain
    draw.ellipse((200, 200, 600, 420), fill=(90, 80, 70))
    draw.text((20, 20), "Damp stain", fill=(10, 10, 10))
    img.save(path)


def make_leak(path):
    img = Image.new("RGB", (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.ellipse((220, 120, 640, 380), fill=(70, 60, 55))
    draw.rectangle((300, 380, 420, 430), fill=(70, 60, 55))
    draw.text((20, 20), "Leak stain", fill=(10, 10, 10))
    img.save(path)


def make_crack(path):
    img = Image.new("RGB", (800, 600), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    # draw jagged thin line
    x = 100
    y = 100
    for i in range(20):
        x2 = x + 30
        y2 = y + (i % 2) * 6
        draw.line((x, y, x2, y2), fill=(10, 10, 10), width=2)
        x, y = x2, y2
    draw.text((20, 20), "Crack line", fill=(10, 10, 10))
    img.save(path)


def make_exposed_wiring(path):
    img = Image.new("RGB", (800, 600), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    # draw multiple thin bright lines
    draw.line((100, 50, 700, 50), fill=(255, 220, 20), width=3)
    draw.line((100, 80, 700, 140), fill=(255, 220, 20), width=2)
    draw.text((20, 20), "Exposed wiring", fill=(10, 10, 10))
    img.save(path)


def make_mold(path):
    img = Image.new("RGB", (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    # speckled dark spots
    import random
    for i in range(200):
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        r = random.randint(2, 6)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(60, 70, 50))
    draw.text((20, 20), "Mold-like speckles", fill=(10, 10, 10))
    img.save(path)


def synth_for_label(label, path):
    if label == "ok":
        make_ok(path)
    elif label in ("damp", "stain"):
        make_damp(path)
    elif label == "leak":
        make_leak(path)
    elif label == "crack":
        make_crack(path)
    elif label in ("exposed_wiring", "wiring"):
        make_exposed_wiring(path)
    elif label == "mold":
        make_mold(path)
    else:
        make_ok(path)


def main():
    csv_path = DATA_DIR / "sample_properties.csv"
    if not csv_path.exists():
        print("CSV not found:", csv_path)
        return
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            fn = r.get('image_filename')
            if not fn:
                continue
            path = IMAGES_DIR / fn
            # decide label from filename or notes
            lname = fn.lower()
            chosen = 'ok'
            for k in LABEL_MAP:
                if k in lname:
                    chosen = LABEL_MAP[k]
                    break
            # if notes mention keywords, prefer notes
            notes = (r.get('notes') or '').lower()
            for k in LABEL_MAP:
                if k in notes:
                    chosen = LABEL_MAP[k]
                    break
            synth_for_label(chosen, path)
            print('Wrote', path, 'as', chosen)


if __name__ == '__main__':
    main()
