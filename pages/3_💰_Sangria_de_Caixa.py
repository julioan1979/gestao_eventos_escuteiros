from __future__ import annotations

import streamlit as st

from data.airtable_client import create_record
from data.cache_utils import invalidate_cache
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

    render_header("💰 Sangria de Caixa", "Registo de levantamentos de caixa")

    with st.form("form_sangria"):
        valor = st.number_input("Valor da sangria (€)", min_value=0.0, step=5.0)
        responsavel = st.text_input("Responsável")
        observacoes = st.text_area("Observações")
        submitted = st.form_submit_button("Registar sangria")

    if submitted:
        if valor <= 0 or not responsavel:
            st.error("Preencha o valor e o responsável pela sangria.")
        else:
            create_record(
                "Sangria de Caixa",
                {
                    "Evento": [evento_id],
                    "Valor": valor,
                    "Responsável": responsavel,
                    "Observações": observacoes,
                },
            )
            invalidate_cache()
            st.success("Sangria registada com sucesso.")
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
