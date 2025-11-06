import streamlit as st
from pyairtable import Table

from data.airtable_client import read_all
from utils.layout import load_styles, render_footer, render_header

st.set_page_config(page_title="Gestão de Eventos Escuteiros", page_icon="🍂", layout="wide")
load_styles()


def _reset_session() -> None:
    for key in [
        "autenticado",
        "perfil",
        "utilizador",
        "utilizador_id",
        "eventos_permitidos",
        "evento_ativo_id",
    ]:
        if key in st.session_state:
            del st.session_state[key]


if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False


def _escape_formula_value(value: str) -> str:
    """Escape single quotes to keep Airtable formulas syntactically valid."""

    return str(value).replace("'", "\\'")


if not st.session_state["autenticado"]:
    render_header("🔐 Login")
    email = st.text_input("Email").strip()
    senha = st.text_input("Password", type="password").strip()

    if st.button("Entrar"):
        if not email or not senha:
            st.warning("Preencha email e password.")
        else:
            users_table = Table(
                st.secrets["airtable"]["api_key"],
                st.secrets["airtable"]["base_id"],
                "Utilizadores",
            )
            formula = (
                "AND("
                f"{{Email}}='{_escape_formula_value(email)}', "
                f"{{Password}}='{_escape_formula_value(senha)}', "
                "{Ativo}=TRUE())"
            )
            try:
                users = users_table.all(filterByFormula=formula, max_records=1)
            except Exception as error:  # pragma: no cover - Streamlit runtime feedback
                st.error("Não foi possível validar as credenciais no Airtable.")
                st.caption(str(error))
            else:
                if users:
                    record = users[0]
                    fields = record.get("fields", {})
                    st.session_state.update(
                        {
                            "autenticado": True,
                            "perfil": fields.get("Perfil"),
                            "utilizador": fields.get("Nome", "Utilizador"),
                            "utilizador_id": record.get("id"),
                            "eventos_permitidos": fields.get("Eventos", []),
                        }
                    )
                    eventos = read_all("Eventos")
                    ativo = None
                    if st.session_state["eventos_permitidos"]:
                        for evento in eventos:
                            if evento.get("id") in st.session_state["eventos_permitidos"]:
                                ativo = evento.get("id")
                                break
                    if not ativo:
                        for evento in eventos:
                            if evento.get("Ativo"):
                                ativo = evento.get("id")
                                break
                    if ativo:
                        st.session_state["evento_ativo_id"] = ativo
                    st.success(
                        f"Bem-vindo, {st.session_state['utilizador']} ({st.session_state['perfil']})"
                    )
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
else:
    st.sidebar.success("Escolhe uma página.")
    st.sidebar.caption(f"Utilizador: {st.session_state['utilizador']}")
    st.sidebar.caption(f"Perfil: {st.session_state['perfil']}")

    if st.sidebar.button("Terminar sessão"):
        _reset_session()
        st.rerun()

    render_header("🍂 Gestão de Eventos Escuteiros", "Centro de controlo")

    eventos = read_all("Eventos")

    ativos_permitidos = [
        evento
        for evento in eventos
        if evento.get("Ativo") and (
            not st.session_state.get("eventos_permitidos")
            or evento.get("id") in st.session_state.get("eventos_permitidos", [])
        )
    ]

    if ativos_permitidos:
        nomes = {evento.get("Nome", evento.get("id")): evento.get("id") for evento in ativos_permitidos}
        default = st.session_state.get("evento_ativo_id")
        default_label = None
        if default:
            for nome, eid in nomes.items():
                if eid == default:
                    default_label = nome
                    break
        label = st.selectbox(
            "Evento Ativo",
            list(nomes.keys()),
            index=list(nomes.keys()).index(default_label) if default_label else 0,
        )
        st.session_state["evento_ativo_id"] = nomes[label]
        st.info(f"Evento selecionado: {label}")
    else:
        st.warning("Nenhum evento ativo disponível.")

    st.markdown(
        """
        ### Próximos passos
        * Utilize o menu lateral para navegar entre as páginas.
        * Os operadores podem registar pedidos e recebimentos.
        * Os administradores têm acesso adicional à gestão de ementas, tipos de cliente, eventos e utilizadores.
        """
    )

    render_footer()
