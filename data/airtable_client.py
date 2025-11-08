"""Helpers for interacting with Airtable tables used in the project."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pyairtable import Table
import streamlit as st


@lru_cache(maxsize=1)
def _get_airtable_credentials() -> Tuple[str, str]:
    """Return the Airtable API credentials declared in ``st.secrets``."""

    try:
        airtable_config = st.secrets["airtable"]
    except Exception as error:  # pragma: no cover - runtime configuration guard
        raise RuntimeError(
            "Configuração Airtable não encontrada em st.secrets['airtable']."
        ) from error

    try:
        api_key = airtable_config["api_key"]
        base_id = airtable_config["base_id"]
    except KeyError as error:  # pragma: no cover - runtime configuration guard
        raise RuntimeError(
            "Configuração Airtable deve incluir as chaves 'api_key' e 'base_id'."
        ) from error

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
