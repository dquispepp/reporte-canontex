"""
Servidor MCP que expone los datos de CRO/Clarity (data/clarity/) como
herramientas consultables en vivo desde Claude.ai (Project CRO) o Claude Code.

Correr local (pruebas):
    python src/mcp_cro_server.py

Expone Streamable HTTP en http://0.0.0.0:8420/mcp
"""

import json
import os
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "clarity"

mcp = FastMCP("canontex-cro", stateless_http=True)


def _read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"No existe {name} en data/clarity/")
    return pd.read_csv(path, encoding="utf-8-sig")


def _df_to_records(df: pd.DataFrame, tail: int | None = None) -> list[dict]:
    if tail:
        df = df.tail(tail)
    return json.loads(df.to_json(orient="records", force_ascii=False))


@mcp.tool()
def get_metadata() -> dict:
    """Metadata de la última actualización de los datos CRO: fecha de corte,
    periodo cubierto, fuentes (GA4, OMS, Clarity) y descripción de cada archivo.
    Consulta esto primero para saber qué tan frescos están los datos."""
    meta_path = DATA_DIR / "_meta_actualizacion.json"
    return json.loads(meta_path.read_text(encoding="utf-8"))


@mcp.tool()
def get_ventas_resumen(dias: int = 14) -> list[dict]:
    """Venta diaria cruzada GA4 + OMS: sesiones, add to cart, checkouts,
    compras, revenue, tasa de conversión, pedidos OMS por estado.
    Args:
        dias: cuántos días recientes devolver (default 14).
    """
    df = _read_csv("ventas_resumen.csv")
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_ga4_conversion_diario(dias: int = 14) -> list[dict]:
    """Serie diaria de conversión GA4: sesiones, add to cart, checkouts,
    compras, revenue y tasas de conversión por etapa.
    Args:
        dias: cuántos días recientes devolver (default 14).
    """
    df = _read_csv("ga4_conversion_diario.csv")
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_funnel_mensual() -> list[dict]:
    """Funnel comparativo mes actual vs mismo mes año anterior
    (sesiones, ATC, checkout, compras) con variación %."""
    df = _read_csv("funnel_mensual.csv")
    return _df_to_records(df)


@mcp.tool()
def get_ga4_funnel() -> list[dict]:
    """Funnel GA4 del mes actual vs mes anterior por etapa, con % de
    conversión de cada etapa y variación %."""
    df = _read_csv("ga4_funnel.csv")
    return _df_to_records(df)


@mcp.tool()
def get_abandono_carrito(dias: int = 14) -> list[dict]:
    """Abandono de carrito diario por etapa del funnel: sesión->ATC,
    ATC->checkout, checkout->compra, con % de abandono en cada paso.
    Args:
        dias: cuántos días recientes devolver (default 14).
    """
    df = _read_csv("ventas_abandono_carrito.csv")
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_clarity_friccion_por_etapa() -> list[dict]:
    """Fricción UX (Microsoft Clarity) por etapa del sitio: % rage clicks,
    % dead clicks, % quickback, % scroll y tiempo activo, con sesiones."""
    df = _read_csv("clarity_funnel.csv")
    return _df_to_records(df)


@mcp.tool()
def get_clarity_paginas_friccion(top: int = 15) -> list[dict]:
    """Top páginas con mayor fricción UX según Microsoft Clarity, ordenadas
    por Score de Fricción descendente.
    Args:
        top: cuántas páginas devolver (default 15).
    """
    df = _read_csv("clarity_paginas.csv")
    df = df.sort_values("Score Friccion", ascending=False).head(top)
    return _df_to_records(df)


@mcp.tool()
def get_oms_pedidos_diario(dias: int = 14) -> list[dict]:
    """Pedidos OMS por día: total, entregados, anulados, en proceso,
    despacho a domicilio vs retiro en tienda.
    Args:
        dias: cuántos días recientes devolver (default 14).
    """
    df = _read_csv("oms_pedidos_diario.csv")
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_clarity_historial() -> dict:
    """Historial diario acumulado de Clarity (snapshots por fecha) para ver
    evolución de la fricción UX en el tiempo."""
    path = DATA_DIR / "clarity_historial.json"
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8420))
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
