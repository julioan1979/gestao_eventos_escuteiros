from __future__ import annotations

import pandas as pd
import streamlit as st

from data.airtable_client import create_record, read_all
from data.cache_utils import get_cached_data, invalidate_cache
from utils.forms import pedido_form
from utils.layout import render_footer, render_header


def _require_login() -> None:
    if not st.session_state.get("autenticado"):
        st.warning("É necessário iniciar sessão para aceder a esta página.")
        st.stop()


def _require_evento() -> str:
    evento_id = st.session_state.get("evento_ativo_id")
    if not evento_id:
        st.warning("Selecione um evento ativo no ecrã inicial.")
        st.stop()
    return evento_id


def _filter_event(records, evento_id: str):
    filtrados = []
    for record in records:
        evento = record.get("Evento")
        if isinstance(evento, list) and evento_id in evento:
            filtrados.append(record)
        elif evento == evento_id:
            filtrados.append(record)
    return filtrados


def _resolve_nome(value, mapping):
    if isinstance(value, list):
        if not value:
            return ""
        return mapping.get(value[0], value[0])
    return mapping.get(value, value)


def main() -> None:
    _require_login()
    evento_id = _require_evento()

    render_header("📋 Pedidos", "Registo de pedidos de clientes")

    eventos = get_cached_data("Eventos")
    tipos = get_cached_data("Tipos de Cliente")
    ementas = get_cached_data("Ementas")
    precos = get_cached_data("Preços")

    novo_pedido = pedido_form(
        eventos=eventos,
        tipos=tipos,
        ementas=_filter_event(ementas, evento_id),
        precos=_filter_event(precos, evento_id),
        default_event_id=evento_id,
    )
    if novo_pedido:
        create_record("Pedidos", novo_pedido)
        invalidate_cache()
        st.success("Pedido registado com sucesso!")
        st.rerun()

    pedidos = read_all("Pedidos")
    pedidos = _filter_event(pedidos, evento_id)

    if pedidos:
        ementas_map = {ementa.get("id"): ementa.get("Nome") for ementa in ementas}
        tipos_map = {tipo.get("id"): tipo.get("Nome") for tipo in tipos}
        linhas = []
        for pedido in pedidos:
            linha = {
                "Data": pedido.get("Data"),
                "Ementa": _resolve_nome(pedido.get("Ementa"), ementas_map),
                "Tipo": _resolve_nome(pedido.get("TipoCliente"), tipos_map),
                "Quantidade": pedido.get("Quantidade"),
                "Valor": pedido.get("Valor"),
                "Pago": pedido.get("Pago"),
            }
            linhas.append(linha)
        df = pd.DataFrame(linhas)
        df = df[[col for col in ["Data", "Ementa", "Tipo", "Quantidade", "Valor", "Pago"] if col in df.columns]]
        st.subheader("Pedidos do evento")
        st.dataframe(df.sort_values(by=df.columns[0], ascending=False) if not df.empty else df)
    else:
        st.info("Sem pedidos registados para este evento.")

    render_footer()


if __name__ == "__main__":
    main()
