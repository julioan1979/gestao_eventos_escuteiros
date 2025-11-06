"""Helpers for interacting with Airtable tables used in the project."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from pyairtable import Table
import streamlit as st

API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]


def get_table(name: str) -> Table:
    """Return a :class:`~pyairtable.Table` instance for ``name``."""
    return Table(API_KEY, BASE_ID, name)


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
