import json
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "poe2_all_details.json"

@st.cache_data
def load_all_details():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)