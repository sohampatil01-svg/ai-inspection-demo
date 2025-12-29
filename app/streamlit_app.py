import streamlit as st
import pandas as pd
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app.snowflake_client import SnowflakeClient
from app.image_classifier import classify_image

st.set_page_config(page_title="AI-Assisted Inspection", layout="wide")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "sample_properties.csv"

LABEL_KEYWORDS = {
    "crack": 0.6,
    "leak": 1.0,
    "damp": 0.9,
    "mold": 1.0,
    "exposed_wiring": 1.2,
    "wiring": 1.2,
    "ok": 0.0
}

DEFAULT_WEIGHT = 0.5


def heuristic_label_from_filename(filename: str):
    name = filename.lower()
    for key in LABEL_KEYWORDS.keys():
        if key in name:
            return key
    # check substrings
    if "wire" in name:
        return "exposed_wiring"
    if "damp" in name or "stain" in name:
        return "damp"
    if "crack" in name:
        return "crack"
    # fallback: if filename contains leak or water
    if "leak" in name or "water" in name:
        return "leak"
    return "ok"


def label_score(label: str):
    return float(LABEL_KEYWORDS.get(label, DEFAULT_WEIGHT))


def compute_risk(agg_labels_counts):
    """Given dict of label->count, compute a simple risk score and category"""
    # risk score: sum(count * severity) normalized by rooms (simple)
    total = 0.0
    for label, cnt in agg_labels_counts.items():
        severity = LABEL_KEYWORDS.get(label, DEFAULT_WEIGHT)
        total += cnt * severity
    return total


def plain_language_summary(property_name, summary_by_room):
    # summary_by_room: dict room_name -> {labels:count}
    overall_counts = {}
    room_with_major = 0
    room_total = len(summary_by_room)
    for room, info in summary_by_room.items():
        for label, cnt in info.items():
            overall_counts[label] = overall_counts.get(label, 0) + cnt
        # consider major if has leak/damp/exposed_wiring/mold
        if any(l in info for l in ("leak", "damp", "exposed_wiring", "mold")):
            room_with_major += 1

    # determine top problems
    top = sorted(overall_counts.items(), key=lambda x: -x[1])[:5]
    top_str = ", ".join(f"{k} in {v} images" for k, v in top)

    # risk level
    score = compute_risk(overall_counts)
    if score >= 3:
        level = "High risk"
    elif score >= 1.5:
        level = "Medium risk"
    else:
        level = "Low risk"

    summary = f"{level}: {top_str}; major issues in {room_with_major}/{room_total} rooms."
    return summary, score


st.title("AI-Assisted Home & Building Inspection (Prototype)")

st.sidebar.header("Data & Settings")
uploaded = st.sidebar.file_uploader("Upload CSV (optional)", type=["csv"])
use_images = st.sidebar.checkbox("Use images in `data/images` for labelling (heuristic)", value=True)

if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv(CSV_PATH)

st.sidebar.markdown(f"Loaded rows: `{len(df)}`")

st.header("Raw dataset")
st.dataframe(df)

st.markdown("---")

st.header("Run classification & scoring")
if st.button("Classify now"):
    # classify each row (use filename heuristic)
    results = []
    per_room = {}
    for _, row in df.iterrows():
        fn = str(row.get("image_filename", "")).strip()
        label = "ok"
        score = 0.0
        if use_images and fn:
            img_path = IMAGES_DIR / fn
            if img_path.exists():
                try:
                    label, score = classify_image(str(img_path))
                except Exception:
                    label = heuristic_label_from_filename(fn)
                    score = label_score(label)
            else:
                # fallback to filename heuristic if image file missing
                label = heuristic_label_from_filename(fn)
                score = label_score(label)
        else:
            # fallback to notes-based classification
            notes = str(row.get("notes", "")).lower()
            label = "ok"
            for key in LABEL_KEYWORDS.keys():
                if key in notes:
                    label = key
                    break
            score = label_score(label)
        results.append({
            "property_id": int(row["property_id"]),
            "property_name": row["property_name"],
            "room_id": int(row["room_id"]),
            "room_name": row["room_name"],
            "image_filename": fn,
            "label": label,
            "score": score,
            "notes": row.get("notes", "")
        })
        # aggregate per room
        per_room.setdefault(row["room_name"], {})
        per_room[row["room_name"]][label] = per_room[row["room_name"]].get(label, 0) + 1

    results_df = pd.DataFrame(results)
    st.subheader("Classification results")
    st.dataframe(results_df)

    # aggregation per property
    agg = results_df.groupby(["property_id", "property_name"]).agg(
        total_findings=("label", "count"),
        avg_score=("score", "mean")
    ).reset_index()
    st.subheader("Aggregated per property")
    st.dataframe(agg)

    # produce plain-language summary per property
    st.subheader("Plain-language summary")
    for (pid, pname), group in results_df.groupby(["property_id", "property_name"]):
        summary_by_room = {}
        for _, r in group.iterrows():
            summary_by_room.setdefault(r["room_name"], {})
            summary_by_room[r["room_name"]][r["label"]] = summary_by_room[r["room_name"]].get(r["label"], 0) + 1
        summary_text, score = plain_language_summary(pname, summary_by_room)
        st.markdown(f"**{pname}** (score {score:.2f}): {summary_text}")

    st.markdown("---")
    st.subheader("Visualize image thumbnails (if available)")
    cols = st.columns(4)
    for i, row in results_df.iterrows():
        fn = row["image_filename"]
        if not fn:
            continue
        img_path = IMAGES_DIR / fn
        col = cols[i % 4]
        with col:
            if img_path.exists():
                img = Image.open(img_path)
                st.image(img, caption=f"{row['room_name']} — {row['label']}")
            else:
                # create placeholder
                img = Image.new("RGB", (300, 200), color=(240, 240, 240))
                d = ImageDraw.Draw(img)
                d.text((10, 10), f"{fn} (missing)", fill=(0, 0, 0))
                st.image(img, caption=f"{row['room_name']} — {row['label']} (image missing)")

    st.markdown("---")
    st.subheader("Upload results to Snowflake")
    if st.button("Upload to Snowflake"):
        sf = SnowflakeClient()
        try:
            sf.ensure_table()
            insert_rows = []
            for _, r in results_df.iterrows():
                insert_rows.append((
                    int(r["property_id"]),
                    r["property_name"],
                    int(r["room_id"]),
                    r["room_name"],
                    r["image_filename"],
                    r["label"],
                    float(r["score"]),
                    r.get("notes", "")
                ))
            ok = sf.insert_findings(insert_rows)
            if ok:
                st.success("Uploaded results to Snowflake table `INSPECTION_FINDINGS`")
        except Exception as e:
            st.error(f"Snowflake upload failed: {e}")

else:
    st.info("Press 'Classify now' to run heuristic classification and scoring.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built for demo/prototyping. Replace heuristics with ML or Snowflake Cortex for production.")
