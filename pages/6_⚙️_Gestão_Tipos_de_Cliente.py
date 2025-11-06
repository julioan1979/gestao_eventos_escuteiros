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


def main() -> None:
    _require_admin()

    render_header("⚙️ Gestão de Tipos de Cliente", "Configuração de categorias de clientes")

    tipos = read_all("Tipos de Cliente")

    if tipos:
        st.subheader("Tipos existentes")
        for tipo in tipos:
            with st.expander(tipo.get("Nome", tipo.get("id"))):
                nome = st.text_input("Nome", value=tipo.get("Nome", ""), key=f"nome_{tipo['id']}")
                desconto = st.number_input(
                    "Desconto %",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(tipo.get("Desconto %", 0) or 0),
                    key=f"desc_{tipo['id']}",
                )
                cor = st.color_picker("Cor", value=tipo.get("Cor", "#000000"), key=f"cor_{tipo['id']}")
                if st.button("Guardar", key=f"save_{tipo['id']}"):
                    update_record(
                        "Tipos de Cliente",
                        tipo["id"],
                        {
                            "Nome": nome,
                            "Desconto %": desconto,
                            "Cor": cor,
                        },
                    )
                    invalidate_cache()
                    st.success("Tipo atualizado.")
                    st.rerun()
    else:
        st.info("Nenhum tipo de cliente configurado.")

    st.subheader("Novo tipo")
    with st.form("novo_tipo"):
        nome = st.text_input("Nome do tipo")
        desconto = st.number_input("Desconto %", min_value=0.0, max_value=100.0, value=0.0)
        cor = st.color_picker("Cor", value="#000000")
        submitted = st.form_submit_button("Criar tipo")

    if submitted:
        if not nome:
            st.error("Indique o nome do tipo de cliente.")
        else:
            create_record(
                "Tipos de Cliente",
                {
                    "Nome": nome,
                    "Desconto %": desconto,
                    "Cor": cor,
                },
            )
            invalidate_cache()
            st.success("Tipo de cliente criado.")
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
