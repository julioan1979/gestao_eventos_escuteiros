from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import streamlit as st

from data.airtable_client import create_record, read_all, update_record
from data.cache_utils import invalidate_cache
from utils.layout import render_footer, render_header


def _require_admin() -> None:
    if not st.session_state.get("autenticado"):
        st.warning("É necessário iniciar sessão para aceder a esta página.")
        st.stop()
    if st.session_state.get("perfil") != "Administrador":
        st.warning("Acesso restrito aos administradores.")
        st.stop()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def main() -> None:
    _require_admin()

    render_header("🗓️ Eventos", "Gestão de eventos disponíveis")

    eventos = read_all("Eventos")

    if eventos:
        st.subheader("Eventos existentes")
        for evento in eventos:
            with st.expander(evento.get("Nome", evento.get("id"))):
                nome = st.text_input("Nome", value=evento.get("Nome", ""), key=f"nome_{evento['id']}")
                data_default = _parse_date(evento.get("Data"))
                data = st.date_input(
                    "Data", value=data_default or date.today(), key=f"data_{evento['id']}"
                )
                local = st.text_input("Local", value=evento.get("Local", ""), key=f"local_{evento['id']}")
                ativo = st.checkbox("Ativo", value=evento.get("Ativo", False), key=f"ativo_{evento['id']}")
                if st.button("Guardar", key=f"save_{evento['id']}"):
                    update_record(
                        "Eventos",
                        evento["id"],
                        {
                            "Nome": nome,
                            "Data": str(data) if data else None,
                            "Local": local,
                            "Ativo": ativo,
                        },
                    )
                    invalidate_cache()
                    if ativo:
                        st.session_state["evento_ativo_id"] = evento["id"]
                    st.success("Evento atualizado.")
                    st.rerun()
                if st.button("Definir como evento ativo", key=f"set_{evento['id']}"):
                    st.session_state["evento_ativo_id"] = evento["id"]
                    st.success("Evento selecionado na sessão atual.")
    else:
        st.info("Sem eventos configurados.")

    st.subheader("Novo evento")
    with st.form("novo_evento"):
        nome = st.text_input("Nome do evento")
        data = st.date_input("Data")
        local = st.text_input("Local")
        ativo = st.checkbox("Ativo", value=True)
        submitted = st.form_submit_button("Criar evento")

    if submitted:
        if not nome:
            st.error("Indique o nome do evento.")
        else:
            record = create_record(
                "Eventos",
                {
                    "Nome": nome,
                    "Data": str(data),
                    "Local": local,
                    "Ativo": ativo,
                },
            )
            invalidate_cache()
            if ativo:
                st.session_state["evento_ativo_id"] = record.get("id")
            st.success("Evento criado com sucesso.")
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
