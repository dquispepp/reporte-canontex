"""
Servidor MCP que expone los datos de CRO/Clarity (data/clarity/) y de
Atrasos (data/atrasos/) como herramientas consultables en vivo desde
Claude.ai (Projects CRO y Atrasos) o Claude Code.

Correr local (pruebas):
    python src/mcp_cro_server.py

Expone Streamable HTTP en http://0.0.0.0:8420/mcp
"""

import json
import os
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

BASE_DIR = Path(__file__).resolve().parent.parent
CRO_DIR = BASE_DIR / "data" / "clarity"
ATRASOS_DIR = BASE_DIR / "data" / "atrasos"

# Permite el host publico de Render (por default el SDK MCP solo acepta
# localhost, como proteccion anti DNS-rebinding).
ALLOWED_HOST = os.environ.get("MCP_ALLOWED_HOST", "reporte-canontex.onrender.com")

mcp = FastMCP(
    "canontex-data",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        allowed_hosts=["127.0.0.1:*", "localhost:*", ALLOWED_HOST],
        allowed_origins=["http://127.0.0.1:*", "http://localhost:*", f"https://{ALLOWED_HOST}"],
    ),
)


def _read_csv(name: str, data_dir: Path = CRO_DIR) -> pd.DataFrame:
    path = data_dir / name
    if not path.exists():
        raise FileNotFoundError(f"No existe {name} en {data_dir}")
    return pd.read_csv(path, encoding="utf-8-sig")


def _df_to_records(df: pd.DataFrame, tail: int | None = None) -> list[dict]:
    if tail:
        df = df.tail(tail)
    return json.loads(df.to_json(orient="records", force_ascii=False))


@mcp.tool()
def get_cro_metadata() -> dict:
    """Metadata de la última actualización de los datos CRO: fecha de corte,
    periodo cubierto, fuentes (GA4, OMS, Clarity) y descripción de cada archivo.
    Consulta esto primero para saber qué tan frescos están los datos."""
    meta_path = CRO_DIR / "_meta_actualizacion.json"
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
def get_gopersonal_diario(dias: int = 30) -> list[dict]:
    """Funnel diario del canal gopersonal (personalizacion/leads, source/medium
    de GA4 que contiene 'gopersonal'): sesiones, add to cart, checkouts,
    compras GA4, revenue y tasa de conversion.
    Args:
        dias: cuántos días recientes devolver (default 30).
    """
    df = _read_csv("gopersonal_diario.csv")
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_gopersonal_eventos() -> list[dict]:
    """Eventos GA4 del canal gopersonal del mes en curso (page_view, add_to_cart,
    begin_checkout, generate_lead, purchase, etc.) con cantidad de eventos y
    usuarios únicos, ordenados de mayor a menor volumen."""
    df = _read_csv("gopersonal_eventos.csv")
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
    path = CRO_DIR / "clarity_historial.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Atrasos (data/atrasos/)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_atrasos_metadata() -> dict:
    """Metadata de la última actualización del reporte de atrasos: fecha de
    corte, fuente (OMS + WMS + FedEx + BigTicket) y descripción de cada
    archivo. Consulta esto primero para saber qué tan fresco es el dato."""
    meta_path = ATRASOS_DIR / "_meta_actualizacion.json"
    return json.loads(meta_path.read_text(encoding="utf-8"))


@mcp.tool()
def get_atrasos_tendencia(dias: int = 30) -> list[dict]:
    """Serie histórica diaria de KPIs de atrasos: total de pedidos abiertos,
    atrasados, % atrasados, % OTIF, días de atraso promedio, pedidos sin
    WMS, reservas sin OV y venta futura.
    Args:
        dias: cuántos días recientes devolver (default 30).
    """
    df = _read_csv("atrasos_tendencia.csv", ATRASOS_DIR)
    return _df_to_records(df, tail=dias)


@mcp.tool()
def get_atrasos_por_diagnostico() -> list[dict]:
    """Desglose de pedidos atrasados por diagnóstico (ej. 'En tienda,
    esperando retiro cliente', 'Quiebre SAP', etc.) con cantidad de
    pedidos, días de atraso promedio y máximo."""
    df = _read_csv("atrasos_por_diagnostico.csv", ATRASOS_DIR)
    return _df_to_records(df)


@mcp.tool()
def get_atrasos_por_courier() -> list[dict]:
    """Rendimiento de atrasos por transportista: cantidad de pedidos
    atrasados, días de atraso promedio y máximo por courier."""
    df = _read_csv("atrasos_por_courier.csv", ATRASOS_DIR)
    return _df_to_records(df)


@mcp.tool()
def get_atrasos_por_tienda() -> list[dict]:
    """Retiros pendientes/atrasados por tienda (región): cantidad de
    pedidos, días de atraso promedio y máximo."""
    df = _read_csv("atrasos_por_tienda.csv", ATRASOS_DIR)
    return _df_to_records(df)


@mcp.tool()
def get_atrasos_por_tipo_despacho() -> list[dict]:
    """Pedidos atrasados por tipo de despacho (ej. Cross Docking, Despacho
    Directo, Retiro en Tienda) con cantidad y días promedio."""
    df = _read_csv("atrasos_por_tipo_despacho.csv", ATRASOS_DIR)
    return _df_to_records(df)


@mcp.tool()
def get_atrasos_top50() -> list[dict]:
    """Detalle de los 50 pedidos más atrasados: envío, orden de compra,
    canal, estado, tipo de despacho, transportista, días de atraso,
    diagnóstico, región y fechas de transacción/compromiso."""
    df = _read_csv("atrasos_detalle_top50.csv", ATRASOS_DIR)
    return _df_to_records(df)


@mcp.tool()
def get_atrasos_historial() -> dict:
    """Historial diario acumulado de KPIs de atrasos en formato JSON
    (mismo dato que get_atrasos_tendencia pero como snapshot histórico)."""
    path = ATRASOS_DIR / "atrasos_historico.json"
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8420))
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
