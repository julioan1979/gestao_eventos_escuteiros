"""Cache helpers for data retrieval from Airtable."""
from __future__ import annotations

import streamlit as st

from .airtable_client import read_all


@st.cache_data(ttl=300)
def get_cached_data(table: str):
    return read_all(table)


def invalidate_cache() -> None:
    """Clear all cached Airtable reads to reflect recent mutations."""

    st.cache_data.clear()
