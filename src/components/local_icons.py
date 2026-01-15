from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]  # => src/
ICON_DIR = BASE_DIR / "image"

def normalize_details_id(details_id: str) -> str:
    """
    Normalisation pour noms de fichiers Windows.
    - remplace ':' par '-'
    - remplace '/' par '-'
    - trim
    """
    return details_id.strip().replace(":", "-").replace("/", "-")


@st.cache_data
def icon_data_uri(details_id: str) -> str | None:
    filename = normalize_details_id(details_id) + ".png"
    png_path = ICON_DIR / filename
    if not png_path.exists():
        return None

    b64 = base64.b64encode(png_path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"
