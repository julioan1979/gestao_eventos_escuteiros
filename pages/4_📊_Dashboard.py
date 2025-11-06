from __future__ import annotations

import plotly.express as px
import streamlit as st

from data.airtable_client import read_all
from data.cache_utils import get_cached_data
from data.transformations import build_dashboard_data
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


def main() -> None:
    _require_login()
    evento_id = _require_evento()

    render_header("📊 Dashboard", "Indicadores do evento")

    pedidos = read_all("Pedidos")
    ementas = get_cached_data("Ementas")
    tipos = get_cached_data("Tipos de Cliente")

    dados = build_dashboard_data(pedidos, ementas, tipos, evento_id)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de pedidos", dados.total_pedidos)
    with col2:
        st.metric("Valor total", f"€ {dados.total_valor:,.2f}")

    if not dados.pedidos_por_ementa.empty:
        fig = px.bar(dados.pedidos_por_ementa, x="Ementa", y="Valor", title="Total por ementa")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de ementas para apresentar.")

    if not dados.pedidos_por_tipo.empty:
        fig = px.pie(dados.pedidos_por_tipo, names="Tipo", values="Valor", title="Distribuição por tipo de cliente")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados por tipo de cliente para apresentar.")

    render_footer()


if __name__ == "__main__":
    main()
