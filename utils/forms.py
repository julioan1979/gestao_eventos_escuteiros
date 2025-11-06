"""Reusable form helpers for Streamlit pages."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import streamlit as st


def _option_label(record: Dict[str, any], default_field: str = "Nome") -> str:
    name = record.get(default_field) or record.get("Email") or record.get("id")
    return str(name)


def select_event(events: Iterable[Dict[str, any]], event_id: Optional[str] = None) -> Optional[Dict[str, any]]:
    events = [event for event in events if event.get("Ativo")]
    if not events:
        st.warning("Não existem eventos ativos configurados.")
        return None

    options = {event.get("id"): _option_label(event) for event in events}
    default_index = 0
    if event_id and event_id in options:
        default_index = list(options.keys()).index(event_id)
    selected_label = st.selectbox("Evento", list(options.values()), index=default_index, key="evento_select")
    selected_id = [key for key, value in options.items() if value == selected_label][0]
    return next(event for event in events if event.get("id") == selected_id)


def pedido_form(
    *,
    eventos: Iterable[Dict[str, any]],
    tipos: Iterable[Dict[str, any]],
    ementas: Iterable[Dict[str, any]],
    precos: Iterable[Dict[str, any]],
    default_event_id: Optional[str],
) -> Optional[Dict[str, any]]:
    event = None
    if default_event_id:
        event = next((e for e in eventos if e.get("id") == default_event_id), None)

    if not event:
        event = select_event(eventos, default_event_id)
        if not event:
            return None

    tipos_map = {tipo.get("id"): _option_label(tipo) for tipo in tipos}
    ementas_map = {ementa.get("id"): _option_label(ementa) for ementa in ementas}

    if not tipos_map or not ementas_map:
        st.info("Configure as ementas e tipos de cliente antes de criar pedidos.")
        return None

    with st.form("form_pedido"):
        tipo_label = st.selectbox("Tipo de Cliente", list(tipos_map.values()))
        tipo_id = next(k for k, v in tipos_map.items() if v == tipo_label)

        ementa_label = st.selectbox("Ementa", list(ementas_map.values()))
        ementa_id = next(k for k, v in ementas_map.items() if v == ementa_label)

        quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)

        preco = _resolver_preco(precos, ementa_id, tipo_id, event.get("id"))
        st.metric("Preço Unitário", f"€ {preco:.2f}")

        submitted = st.form_submit_button("Registar Pedido")
        if submitted:
            if preco <= 0:
                st.error("Não existe preço configurado para a combinação selecionada.")
                return None
            return {
                "Evento": [event.get("id")],
                "TipoCliente": [tipo_id],
                "Ementa": [ementa_id],
                "Quantidade": quantidade,
                "Valor": quantidade * preco,
                "Pago": False,
            }
    return None


def _resolver_preco(precos: Iterable[Dict[str, any]], ementa_id: str, tipo_id: str, evento_id: Optional[str]) -> float:
    for preco in precos:
        if (
            _match_link(preco.get("Ementa"), ementa_id)
            and _match_link(preco.get("TipoCliente"), tipo_id)
            and (not evento_id or _match_event(preco.get("Evento"), evento_id))
        ):
            valor = preco.get("Preço (€)") or preco.get("Preco") or preco.get("Preço")
            try:
                return float(valor)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def _match_event(event_field: any, event_id: str) -> bool:
    if isinstance(event_field, list):
        return event_id in event_field
    return event_field == event_id


def _match_link(field_value: any, record_id: str) -> bool:
    if isinstance(field_value, list):
        return record_id in field_value
    return field_value == record_id
