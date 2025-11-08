"""Helpers for interacting with Airtable tables used in the project."""
from __future__ import annotations

import os
from collections.abc import Mapping
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pyairtable import Table
import streamlit as st


@lru_cache(maxsize=1)
def _get_airtable_credentials() -> Tuple[str, str]:
    """Return the Airtable API credentials declared in ``st.secrets``."""

    airtable_config: Mapping[str, Any] | None = None
    try:
        airtable_config = st.secrets["airtable"]
    except Exception:  # pragma: no cover - runtime configuration guard
        airtable_config = None

    api_key: Optional[str] = None
    base_id: Optional[str] = None

    if isinstance(airtable_config, Mapping):
        api_key = airtable_config.get("api_key")
        base_id = airtable_config.get("base_id")

    api_key = os.getenv("AIRTABLE_API_KEY", api_key or "") or None
    base_id = os.getenv("AIRTABLE_BASE_ID", base_id or "") or None

    if not api_key or not base_id:  # pragma: no cover - runtime configuration guard
        raise RuntimeError(
            "Credenciais Airtable em falta. Configure st.secrets['airtable'] com"
            " 'api_key' e 'base_id' ou defina as variáveis de ambiente"
            " AIRTABLE_API_KEY e AIRTABLE_BASE_ID."
        )

    return str(api_key), str(base_id)


def get_table(name: str) -> Table:
    """Return a :class:`~pyairtable.Table` instance for ``name``."""
    api_key, base_id = _get_airtable_credentials()
    return Table(api_key, base_id, name)


def _normalize(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Attach the record id to the fields dict for easier downstream usage."""
    normalised: List[Dict[str, Any]] = []
    for record in records:
        fields = dict(record.get("fields", {}))
        record_id = record.get("id")
        if record_id:
            fields["id"] = record_id
        normalised.append(fields)
    return normalised


def read_all(name: str, **kwargs: Any) -> List[Dict[str, Any]]:
    """Read all records from ``name`` applying optional Airtable query kwargs."""
    table = get_table(name)
    return _normalize(table.all(**kwargs))


def create_record(name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return get_table(name).create(data)


def update_record(name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return get_table(name).update(record_id, data)


def delete_record(name: str, record_id: str) -> Dict[str, Any]:
    return get_table(name).delete(record_id)


def find_first(name: str, formula: Optional[str] = None) -> Optional[Dict[str, Any]]:
    table = get_table(name)
    records = table.all(max_records=1, filterByFormula=formula)
    normalised = _normalize(records)
    return normalised[0] if normalised else None
