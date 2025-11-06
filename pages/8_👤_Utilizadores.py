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

    render_header("👤 Utilizadores", "Gestão de acessos à aplicação")

    utilizadores = read_all("Utilizadores")
    eventos = read_all("Eventos")
    evento_options = {evento.get("Nome", evento.get("id")): evento.get("id") for evento in eventos}

    if utilizadores:
        st.subheader("Utilizadores existentes")
        for utilizador in utilizadores:
            with st.expander(utilizador.get("Nome", utilizador.get("Email"))):
                nome = st.text_input("Nome", value=utilizador.get("Nome", ""), key=f"nome_{utilizador['id']}")
                email = st.text_input("Email", value=utilizador.get("Email", ""), key=f"email_{utilizador['id']}")
                novo_password = st.text_input(
                    "Password (deixe em branco para manter)", type="password", key=f"pwd_{utilizador['id']}"
                )
                perfis = ["Operador", "Administrador"]
                perfil_atual = utilizador.get("Perfil") if utilizador.get("Perfil") in perfis else "Operador"
                perfil = st.selectbox(
                    "Perfil",
                    perfis,
                    index=perfis.index(perfil_atual),
                    key=f"perfil_{utilizador['id']}",
                )
                ativo = st.checkbox("Ativo", value=utilizador.get("Ativo", False), key=f"ativo_{utilizador['id']}")
                eventos_atribuidos = [
                    nome for nome, eid in evento_options.items() if eid in (utilizador.get("Eventos") or [])
                ]
                selecionados = st.multiselect(
                    "Eventos",
                    list(evento_options.keys()),
                    default=eventos_atribuidos,
                    key=f"eventos_{utilizador['id']}",
                )
                if st.button("Guardar", key=f"save_{utilizador['id']}"):
                    dados = {
                        "Nome": nome,
                        "Email": email,
                        "Perfil": perfil,
                        "Ativo": ativo,
                        "Eventos": [evento_options[nome] for nome in selecionados],
                    }
                    if novo_password:
                        dados["Password"] = novo_password
                    update_record("Utilizadores", utilizador["id"], dados)
                    invalidate_cache()
                    st.success("Utilizador atualizado.")
                    st.rerun()
    else:
        st.info("Sem utilizadores configurados.")

    st.subheader("Novo utilizador")
    with st.form("novo_utilizador"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        perfil = st.selectbox("Perfil", ["Operador", "Administrador"])
        ativo = st.checkbox("Ativo", value=True)
        selecionados = st.multiselect("Eventos", list(evento_options.keys()))
        submitted = st.form_submit_button("Criar utilizador")

    if submitted:
        if not (nome and email and password):
            st.error("Preencha nome, email e password.")
        else:
            create_record(
                "Utilizadores",
                {
                    "Nome": nome,
                    "Email": email,
                    "Password": password,
                    "Perfil": perfil,
                    "Ativo": ativo,
                    "Eventos": [evento_options[nome] for nome in selecionados],
                },
            )
            invalidate_cache()
            st.success("Utilizador criado com sucesso.")
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
