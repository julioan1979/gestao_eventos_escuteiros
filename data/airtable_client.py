"""Helpers for interacting with Airtable tables used in the project."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from functools import lru_cache
import os
from typing import Mapping

from pyairtable import Table
import streamlit as st


class AirtableConfigError(RuntimeError):
    """Raised when the Airtable configuration cannot be loaded."""


def _read_secrets() -> Mapping[str, str]:
    """Return Airtable secrets stored in ``st.secrets`` if present."""

    try:
        airtable_section = st.secrets["airtable"]
    except KeyError:
        return {}

    # ``st.secrets`` behaves like a Mapping but does not expose ``dict`` methods
    # directly. Converting to ``dict`` ensures callers can rely on ``get``.
    return dict(airtable_section)


@lru_cache(maxsize=1)
def _get_config() -> Mapping[str, str]:
    """Resolve the Airtable configuration from secrets or the environment."""

    secrets = _read_secrets()
    api_key = secrets.get("api_key") or os.getenv("AIRTABLE_API_KEY")
    base_id = secrets.get("base_id") or os.getenv("AIRTABLE_BASE_ID")

    if not api_key or not base_id:
        raise AirtableConfigError(
            "Airtable credentials are not configured. Set them via Streamlit "
            "secrets (airtable.api_key / airtable.base_id) or environment "
            "variables AIRTABLE_API_KEY / AIRTABLE_BASE_ID."
        )

    return {"api_key": api_key, "base_id": base_id}


def get_table(name: str) -> Table:
    """Return a :class:`~pyairtable.Table` instance for ``name``."""
    config = _get_config()
    return Table(config["api_key"], config["base_id"], name)


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
