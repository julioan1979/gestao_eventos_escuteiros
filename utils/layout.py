"""Common layout helpers used across Streamlit pages."""
from __future__ import annotations

import pathlib
from typing import Optional

import streamlit as st


def load_styles() -> None:
    css_path = pathlib.Path(__file__).parent / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: Optional[str] = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_footer() -> None:
    st.markdown("---")
    st.caption("Aplicação de gestão de eventos dos Escuteiros.")
