from __future__ import annotations

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


def _require_evento() -> str:
    evento_id = st.session_state.get("evento_ativo_id")
    if not evento_id:
        st.warning("Selecione um evento ativo no ecrã inicial.")
        st.stop()
    return evento_id


def _match_event(value, evento_id: str) -> bool:
    if isinstance(value, list):
        return evento_id in value
    return value == evento_id


def main() -> None:
    _require_admin()
    evento_id = _require_evento()

    render_header("⚙️ Gestão de Ementas", "Configuração de ementas do evento")

    ementas = read_all("Ementas")
    ementas_evento = [e for e in ementas if _match_event(e.get("Evento"), evento_id)]

    if ementas_evento:
        st.subheader("Ementas existentes")
        for ementa in ementas_evento:
            with st.expander(ementa.get("Nome", ementa.get("id"))):
                nome = st.text_input("Nome", value=ementa.get("Nome", ""), key=f"nome_{ementa['id']}")
                descricao = st.text_area(
                    "Descrição", value=ementa.get("Descrição", ""), key=f"desc_{ementa['id']}"
                )
                ativo = st.checkbox("Ativo", value=ementa.get("Ativo", False), key=f"ativo_{ementa['id']}")
                if st.button("Guardar alterações", key=f"save_{ementa['id']}"):
                    update_record(
                        "Ementas",
                        ementa["id"],
                        {
                            "Nome": nome,
                            "Descrição": descricao,
                            "Ativo": ativo,
                        },
                    )
                    invalidate_cache()
                    st.success("Ementa atualizada.")
                    st.rerun()
    else:
        st.info("Não existem ementas configuradas para este evento.")

    st.subheader("Nova ementa")
    with st.form("nova_ementa"):
        nome = st.text_input("Nome da ementa")
        descricao = st.text_area("Descrição")
        ativo = st.checkbox("Ativo", value=True)
        submitted = st.form_submit_button("Criar ementa")

    if submitted:
        if not nome:
            st.error("Indique o nome da ementa.")
        else:
            create_record(
                "Ementas",
                {
                    "Nome": nome,
                    "Descrição": descricao,
                    "Ativo": ativo,
                    "Evento": [evento_id],
                },
            )
            invalidate_cache()
            st.success("Ementa criada com sucesso.")
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
