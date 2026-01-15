import streamlit as st
from pathlib import Path

def load_css():
    base_dir = Path(__file__).resolve().parent

    css_files = [
        base_dir / "assets" / "poe_ninja.css",
        base_dir / "assets" / "opportunities.css",
    ]

    css_content = ""
    for css_path in css_files:
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css_content += f.read() + "\n"

    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="PoE 2 Economy",
    layout="wide",
)

load_css()

st.title("💰 Path of Exile 2 – Economy Dashboard")

st.markdown("""
Bienvenue sur le dashboard économique PoE2.

👉 Utilise le menu à gauche pour naviguer :
- **Overview** : vue globale par type
- **Opportunities** : vue des opportunités
""")