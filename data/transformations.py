"""Utility transformations used across dashboards and pages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd


@dataclass
class DashboardData:
    total_pedidos: int
    total_valor: float
    pedidos_por_ementa: pd.DataFrame
    pedidos_por_tipo: pd.DataFrame


def _to_dataframe(records: Iterable[Dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def _filter_by_event(df: pd.DataFrame, event_id: Optional[str]) -> pd.DataFrame:
    if df.empty or not event_id:
        return df
    if "Evento" in df.columns:
        mask = df["Evento"].apply(lambda value: event_id in value if isinstance(value, list) else value == event_id)
        return df.loc[mask].copy()
    return df


def _ensure_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0)


def _first_value(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def build_dashboard_data(
    pedidos: Iterable[Dict],
    ementas: Iterable[Dict],
    tipos_cliente: Iterable[Dict],
    event_id: Optional[str],
) -> DashboardData:
    pedidos_df = _to_dataframe(pedidos)
    pedidos_df = _filter_by_event(pedidos_df, event_id)

    if "Ementa" in pedidos_df.columns:
        pedidos_df["Ementa"] = pedidos_df["Ementa"].apply(_first_value)
    if "TipoCliente" in pedidos_df.columns:
        pedidos_df["TipoCliente"] = pedidos_df["TipoCliente"].apply(_first_value)

    if "Valor" in pedidos_df.columns:
        pedidos_df["Valor"] = _ensure_numeric(pedidos_df["Valor"])
    if "Quantidade" in pedidos_df.columns:
        pedidos_df["Quantidade"] = _ensure_numeric(pedidos_df["Quantidade"])

    total_pedidos = int(pedidos_df["Quantidade"].sum()) if "Quantidade" in pedidos_df else len(pedidos_df)
    total_valor = float(pedidos_df["Valor"].sum()) if "Valor" in pedidos_df.columns else 0.0

    ementas_df = _to_dataframe(ementas)
    tipos_df = _to_dataframe(tipos_cliente)

    pedidos_por_ementa = pedidos_df.copy()
    if not pedidos_por_ementa.empty and "Ementa" in pedidos_por_ementa.columns:
        pedidos_por_ementa = pedidos_por_ementa.groupby("Ementa")["Valor"].sum().reset_index()
        if "Nome" in ementas_df.columns:
            pedidos_por_ementa = pedidos_por_ementa.merge(
                ementas_df[["id", "Nome"]], left_on="Ementa", right_on="id", how="left"
            )
            pedidos_por_ementa.drop(columns=["id"], inplace=True)
            pedidos_por_ementa.rename(columns={"Nome": "Ementa"}, inplace=True)

    pedidos_por_tipo = pedidos_df.copy()
    if not pedidos_por_tipo.empty and "TipoCliente" in pedidos_por_tipo.columns:
        pedidos_por_tipo = pedidos_por_tipo.groupby("TipoCliente")["Valor"].sum().reset_index()
        if "Nome" in tipos_df.columns:
            pedidos_por_tipo = pedidos_por_tipo.merge(
                tipos_df[["id", "Nome"]], left_on="TipoCliente", right_on="id", how="left"
            )
            pedidos_por_tipo.drop(columns=["id"], inplace=True)
            pedidos_por_tipo.rename(columns={"Nome": "Tipo"}, inplace=True)

    return DashboardData(
        total_pedidos=total_pedidos,
        total_valor=total_valor,
        pedidos_por_ementa=pedidos_por_ementa,
        pedidos_por_tipo=pedidos_por_tipo,
    )
