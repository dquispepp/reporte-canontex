"""Reglas de negocio: dias habiles, OTIF interno, atraso, familia, diagnostico y gestion.

No lee archivos: opera sobre el DataFrame consolidado (Reporte x WMS).
Migrar a MCP Hub no toca este modulo.
"""
import numpy as np
import pandas as pd
import holidays

_FERIADOS = np.array(
    sorted(holidays.Chile(years=range(2023, 2028)).keys()), dtype="datetime64[D]"
)

FAMILIA_MAP = {
    "common_shipping_type": "Ropa cama/baño",
    "berger_shipping_type": "Poltronas/alfombras",
    "mattress_shipping_type": "Colchonería/camas",
}

WMS_EN_PREPARACION = (
    "Pickeada", "En Oleada", "En Proceso", "En Andén", "Liberada",
    "En Predespacho", "En Vehículo",
)

MODALIDADES_CON_VENTANA = ("Despacho a Domicilio", "Retiro en Tienda", "Cross Docking")


def _to_d(fecha):
    if pd.isna(fecha):
        return None
    return np.datetime64(pd.Timestamp(fecha).date(), "D")


def sumar_habiles(fecha, n: int):
    d = _to_d(fecha)
    if d is None:
        return pd.NaT
    return pd.Timestamp(np.busday_offset(d, n, roll="forward", holidays=_FERIADOS))


def restar_habiles(fecha, n: int):
    d = _to_d(fecha)
    if d is None:
        return pd.NaT
    return pd.Timestamp(np.busday_offset(d, -n, roll="backward", holidays=_FERIADOS))


def habiles_entre(inicio, fin) -> float:
    a, b = _to_d(inicio), _to_d(fin)
    if a is None or b is None:
        return np.nan
    return int(np.busday_count(a, b, holidays=_FERIADOS))


def es_metropolitana(region) -> bool:
    return "metropolitana" in str(region).strip().lower()


def normalizar_transportista(t) -> str:
    if pd.isna(t) or str(t).strip() in ("", "-"):
        return "Sin transportista"
    s = str(t).strip()
    if "fedex" in s.lower():
        return "FedEx"
    return s


def familia(tipo_envio) -> str:
    return FAMILIA_MAP.get(str(tipo_envio).strip(), "Sin clasificar")


def fecha_despacho_esperada(fecha_compromiso, region):
    if pd.isna(fecha_compromiso):
        return pd.NaT
    return restar_habiles(fecha_compromiso, 1 if es_metropolitana(region) else 2)


def on_time_interno(fecha_despacho, fecha_esperada):
    """OTIF interno WMS: despachado dentro del compromiso. NaN si aun no despacha."""
    if pd.isna(fecha_esperada) or pd.isna(fecha_despacho):
        return np.nan
    return bool(fecha_despacho <= fecha_esperada)


def fin_ventana_cliente(tipo_despacho, fecha_compromiso):
    """Fecha limite para marcar el pedido como atrasado.
    Domicilio: fecha_compromiso + 2 dias hábiles (buffer negociado con el cliente).
    Resto (Fecha Pactada, Retiro en Tienda, Cross Docking): fecha_compromiso exacta.
    """
    if pd.isna(fecha_compromiso):
        return pd.NaT
    if str(tipo_despacho).strip() == "Despacho a Domicilio":
        return sumar_habiles(fecha_compromiso, 2)
    return fecha_compromiso


def sla_courier(tipo_despacho, fecha_entrega_real, fecha_compromiso) -> bool:
    """SLA Courier (ultima milla): mide si el courier entregó dentro de la ventana.
    Aplica solo a 'Despacho a Domicilio' (buffer +2 días) y 'Fecha Pactada' (exacto).
    NaN para otros tipos de despacho o cuando falta fecha de entrega real."""
    if pd.isna(fecha_entrega_real) or pd.isna(fecha_compromiso):
        return np.nan
    td = str(tipo_despacho).strip()
    if td == "Despacho a Domicilio":
        limite = sumar_habiles(fecha_compromiso, 2)
    elif td == "Fecha Pactada":
        limite = fecha_compromiso
    else:
        return np.nan
    return bool(pd.Timestamp(fecha_entrega_real).normalize() <= pd.Timestamp(limite).normalize())


def sla_ecommerce_72hrs(fecha_creacion, fecha_compromiso) -> bool:
    """SLA Ecommerce: al menos 72 hrs (3 días hábiles) entre creación WMS y compromiso.
    Mide si el canal Ecommerce le dio a bodega el tiempo suficiente para preparar+despachar.
    True = ventana suficiente, False = compromiso demasiado ajustado, NaN = N/A."""
    if pd.isna(fecha_creacion) or pd.isna(fecha_compromiso):
        return np.nan
    dias_habiles = habiles_entre(fecha_creacion, fecha_compromiso)
    return bool(dias_habiles >= 3)


def sla_operacion(fecha_despacho, fecha_compromiso, region) -> bool:
    """SLA Operación: desde despacho a compromiso en días hábiles.
    Metropolitana: 1 día hábil, Otras: 2 días hábiles.
    True = cumple, False = atrasa, NaN = N/A."""
    if pd.isna(fecha_despacho) or pd.isna(fecha_compromiso):
        return np.nan
    dias_habiles = habiles_entre(fecha_despacho, fecha_compromiso)
    target = 1 if es_metropolitana(region) else 2
    return bool(dias_habiles >= target)  # Debe tener al menos N días para cumplir (no debe ser negativo)


def diagnostico(row) -> str:
    er = str(row.get("estado", "")).strip()
    ew = str(row.get("estado_wms", "")).strip()
    td = str(row.get("tipo_despacho", "")).strip()
    sin_wms = bool(row.get("sin_ingreso_wms", False))
    fedex_cod = str(row.get("fedex_codigo", "")).strip()

    # Pedidos ya cerrados no necesitan diagnóstico (SLA Courier los evalúa aparte).
    if er in ("Entregado", "Anulado"):
        return ""

    # Quiebre confirmado en SAP (export sin guia): prevalece -> validar con SAC.
    if str(row.get("sap_quiebre", "")).strip():
        return "validar con SAC"

    # FedEx confirma entrega -> OMS/WMS desactualizado, prevalece.
    if fedex_cod == "DL" and er != "Entregado":
        return "Entregado por FedEx, actualizar OMS"

    if er == "Creado en OMS":
        if sin_wms:
            return "Investigar por qué no llegó al WMS"
        if ew == "Pendiente":
            return "Aún no sale, empujar operación"
        if ew == "Pausa por Quiebre":
            return "validar con SAC"
        if ew in WMS_EN_PREPARACION:
            return "Aún no sale, empujar operación"
        if ew == "Despachada":
            return "Aún no sale, empujar operación"
        return "Investigar por qué no llegó al WMS"

    if er == "Preparado":
        if ew == "Despachada":
            return "Courier tiene pedido, estado no actualizado en OMS"
        return "Revisar WMS: no despachado"

    if er in ("En Courier", "En Tránsito") and ew == "Despachada":
        return "En ruta (atraso courier)"

    if er == "Devuelto a Bodega":
        return "Courier no encontró destino"

    if er == "Rechazado":
        if td in ("Despacho a Domicilio", "Fecha Pactada"):
            return "Recontactar cliente"
        if td in ("Retiro en Tienda", "Cross Docking"):
            return "SAC devolución de dinero"
        return "REVISAR MANUAL"

    if er == "Listo Para Retiro":
        return "En tienda, esperando retiro cliente"

    return "REVISAR MANUAL"


def marca_gestion_retiro(row) -> tuple:
    er = str(row.get("estado", "")).strip()
    ew = str(row.get("estado_wms", "")).strip()
    sin_wms = bool(row.get("sin_ingreso_wms", False))
    if er == "Listo Para Retiro":
        return "TIENDA CONFIRMAR ENTREGA", "Verificar si ya se retiró"
    if er == "Preparado" and ew == "Despachada":
        return "TIENDA CONFIRMAR ENTREGA", "Tienda no actualizó a 'Listo Para Retiro'"
    if er == "Preparado" and ew != "Despachada":
        return "GESTIÓN PENDIENTE — REVISAR WMS", "No despachado, revisar por qué"
    if er == "Creado en OMS" and sin_wms:
        return "NO EXISTE EN WMS", "Investigar por qué no llegó al WMS"
    if er == "Rechazado":
        return "SAC DEVOLUCIÓN DINERO", "Cliente no retiró / venció plazo"
    return diagnostico(row), ""


def responsable_domicilio(row) -> tuple:
    er = str(row.get("estado", "")).strip()
    ew = str(row.get("estado_wms", "")).strip()
    sin_wms = bool(row.get("sin_ingreso_wms", False))
    if sin_wms:
        return "Investigar por qué no llegó al WMS", "No está en bodega"
    if ew != "Despachada":
        return "Aún no sale, empujar operación", "No despachado en WMS"
    if ew == "Despachada" and er == "Creado en OMS":
        return "Aún no sale, empujar operación", "Bodega despachó pero courier no lo tomó"
    if ew == "Despachada" and er == "Preparado":
        return "COURIER PICKUP", "Courier no retiró del andén"
    if ew == "Despachada" and er in ("En Courier", "En Tránsito"):
        return "COURIER RUTA", "Atraso en red del courier"
    if er == "Devuelto a Bodega":
        return "validar con SAC", "Entrega fallida, reprogramar"
    if er == "Rechazado":
        return "validar con SAC", "Coordinar nueva entrega / devolución"
    return "REVISAR MANUAL", ""


def aplicar_reglas(df: pd.DataFrame, hoy: pd.Timestamp) -> pd.DataFrame:
    df = df.copy()

    df["familia"] = df["tipo_envio"].apply(familia)
    df["transportista_norm"] = df["transportista"].apply(normalizar_transportista)
    df["fecha_despacho_esperada"] = df.apply(
        lambda r: fecha_despacho_esperada(r.get("fecha_compromiso"), r.get("region")), axis=1
    )
    df["on_time_interno"] = df.apply(
        lambda r: on_time_interno(r.get("fecha_despacho"), r["fecha_despacho_esperada"]), axis=1
    )
    df["fin_ventana"] = df.apply(
        lambda r: fin_ventana_cliente(r.get("tipo_despacho"), r.get("fecha_compromiso")), axis=1
    )
    # Atrasado: solo aplica a pedidos NO entregados aún. Entregados evalúan SLA Courier.
    _terminales = ("Entregado", "Anulado")
    df["atrasado"] = df.apply(
        lambda r: bool(
            pd.notna(r["fin_ventana"])
            and str(r.get("estado", "")).strip() not in _terminales
            and hoy > r["fin_ventana"]
        ), axis=1
    )
    df["dias_atraso"] = df.apply(
        lambda r: habiles_entre(r["fin_ventana"], hoy) if r["atrasado"] else np.nan, axis=1
    )

    # Fecha entrega real: prioridad OMS(estado=Entregado + fecha_ult_movimiento) > FedEx DL > BT Entregada
    def _fecha_entrega_real(r):
        if str(r.get("estado", "")).strip() == "Entregado" and pd.notna(r.get("fecha_ult_movimiento")):
            return r.get("fecha_ult_movimiento")
        if str(r.get("fedex_codigo", "")).strip() == "DL" and r.get("fedex_fecha"):
            return pd.to_datetime(r.get("fedex_fecha"), errors="coerce", utc=True).tz_localize(None) if pd.notna(r.get("fedex_fecha")) else pd.NaT
        if str(r.get("bt_estado", "")).strip() == "Entregada" and pd.notna(r.get("bt_fecha_ruta")):
            return r.get("bt_fecha_ruta")
        return pd.NaT
    df["fecha_entrega_real"] = df.apply(_fecha_entrega_real, axis=1)

    # SLA Ecommerce: 72 horas (3 días hábiles) creación WMS -> compromiso (ventana upstream)
    df["sla_ecommerce"] = df.apply(
        lambda r: sla_ecommerce_72hrs(r.get("fecha_creacion"), r.get("fecha_compromiso")), axis=1
    )

    # SLA Operación: despacho → compromiso (1 día metropolitana, 2 días otras regiones)
    df["sla_operacion"] = df.apply(
        lambda r: sla_operacion(r.get("fecha_despacho"), r.get("fecha_compromiso"), r.get("region")), axis=1
    )

    # SLA Courier: última milla, solo Domicilio (+2 días buffer) y Fecha Pactada (exacto)
    df["sla_courier"] = df.apply(
        lambda r: sla_courier(r.get("tipo_despacho"), r.get("fecha_entrega_real"), r.get("fecha_compromiso")), axis=1
    )

    df["diagnostico"] = df.apply(diagnostico, axis=1)

    gest = df.apply(marca_gestion_retiro, axis=1, result_type="expand")
    df["marca_gestion"], df["obs_retiro"] = gest[0], gest[1]
    resp = df.apply(responsable_domicilio, axis=1, result_type="expand")
    df["responsable"], df["obs_domicilio"] = resp[0], resp[1]

    return df
