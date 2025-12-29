**AI-Assisted Home & Building Inspection**

This repository is a self-contained example of an AI-assisted inspection workspace that:
- ingests a small sample inspection dataset (structured CSV + labeled images),
- classifies/tags potential defects (simple heuristic classifier included),
- aggregates findings into per-room and per-property risk scores,
- produces plain-language inspection summaries,
- provides a Snowflake integration helper and example SQL (including guidance for Snowflake Cortex / AI SQL usage).

**What's included**
- `app/streamlit_app.py` — Streamlit UI to load data, run classification, view aggregated results, and upload to Snowflake.
- `app/snowflake_client.py` — helper to write classification results to Snowflake using environment variables.
- `data/sample_properties.csv` — sample structured dataset.
- `data/images/` — placeholder notes; you can put labeled images here, filenames with keywords (e.g., `kitchen_1_leak.jpg`).
- `snowflake/snowflake_setup.sql` — SQL DDL and example AI-SQL snippets (account features dependent).
- `requirements.txt` — Python dependencies.

**Quick start (local)**
1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run app/streamlit_app.py
```

3. Follow the UI to load `data/sample_properties.csv` and (optionally) place images into `data/images/`.

**Snowflake integration**

Streamlit Cloud note
---------------------
- This repository provides two requirement lists:
	- `requirements.txt` — minimal dependencies for running on Streamlit Community Cloud (recommended for quick public deploy).
	- `requirements-full.txt` — full dependencies including `snowflake-connector-python` and `python-dotenv` for local usage or servers that support building native extensions.

If Streamlit Cloud fails installing dependencies, use `requirements.txt` (the app is designed to run without Snowflake in that mode). To enable Snowflake upload you must install the full requirements locally or run the app on a server where you can install `requirements-full.txt`.

**Publish to GitHub**
Use these commands (PowerShell):

```powershell
git init
git add .
git commit -m "Initial AI inspection workspace"
# Create remote and push (replace URL)
git remote add origin https://github.com/<your-user>/<your-repo>.git
git branch -M main
git push -u origin main
```

If you have the GitHub CLI installed you can also:

```powershell
gh repo create <your-user>/<your-repo> --public --source=. --push
```

**Notes & next steps**
- This prototype uses filename heuristics to classify images. For production, replace classification with a call to Snowflake Cortex/AI SQL, an external vision model (Clip, torchvision, or an inference endpoint), or an MLOps flow.
- Dynamic Tables, Streams & Tasks examples are included in `snowflake/snowflake_setup.sql` as guidance for implementing periodic re-evaluation in Snowflake.

If you'd like, I can:
- run quick local smoke tests, or
- implement a simple image classifier using a small pretrained model (requires larger dependency additions), or
- prepare GitHub Actions to run tests on push.

