from __future__ import annotations

import streamlit as st

from data.airtable_client import create_record, read_all, update_record
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


def _match_event(value, evento_id: str) -> bool:
    if isinstance(value, list):
        return evento_id in value
    return value == evento_id


def main() -> None:
    _require_login()
    evento_id = _require_evento()

    render_header("💶 Recebimentos", "Gestão de pagamentos de pedidos")

    pedidos = read_all("Pedidos")
    ementas = read_all("Ementas")
    ementas_map = {ementa.get("id"): ementa.get("Nome") for ementa in ementas}
    pendentes = [
        pedido
        for pedido in pedidos
        if _match_event(pedido.get("Evento"), evento_id) and not pedido.get("Pago")
    ]

    if not pendentes:
        st.info("Não existem pedidos pendentes de pagamento para este evento.")
        render_footer()
        return

    st.subheader("Pedidos pendentes")
    for pedido in pendentes:
        valor = pedido.get("Valor", 0)
        ementa_nome = pedido.get("Ementa")
        if isinstance(ementa_nome, list) and ementa_nome:
            ementa_nome = ementas_map.get(ementa_nome[0], ementa_nome[0])
        else:
            ementa_nome = ementas_map.get(ementa_nome, ementa_nome)
        with st.expander(
            f"Pedido {pedido.get('id')} - {ementa_nome} ({pedido.get('Quantidade')} unidades)"
        ):
            st.write(f"Valor devido: € {valor}")
            if st.button("Registar recebimento", key=f"receber_{pedido['id']}"):
                create_record(
                    "Recebimentos",
                    {
                        "Pedido": [pedido["id"]],
                        "Evento": [evento_id],
                        "Valor": valor,
                    },
                )
                update_record("Pedidos", pedido["id"], {"Pago": True})
                invalidate_cache()
                st.success("Recebimento registado!")
                st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
