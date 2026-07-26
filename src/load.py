"""Carga y consolidacion de fuentes (Reporte multi-CSV + WMS xlsx) y cruce.

Reporte es la fuente maestra: left join Reporte -> WMS.
Diseñado para migrar a MCP Hub reemplazando solo las funciones load_*.
"""
from pathlib import Path

import pandas as pd

import keys

BASE = Path(r"C:\Users\dquispe\OneDrive - Representaciones Canontex Ltda\Documentos\DOC DANI")
REPORTE_DIR = BASE / "Reporte"
WMS_DIR = BASE / "Reporte WMS"
SAP_DIR = BASE / "Reporte SAP"
OUTPUT_DIR = BASE

ESTADOS_TERMINALES = ("Entregado", "Anulado")
CANALES_INCLUIDOS = ("ECOMMERCE", "KIOSCO")
PREFIJO_TEB = "12"
PREFIJO_RESERVA = "13"
PREFIJO_OV = "17"

REPORTE_MAP = {
    "pedido": ["n pedido"],
    "cliente_nombre": ["nombre destinatario"],
    "telefono": ["telefono"],
    "correo": ["correo"],
    "region": ["region"],
    "comuna": ["comuna"],
    "sku": ["sku"],
    "producto": ["producto"],
    "fecha_trx": ["fecha trx"],
    "orden_compra": ["orden de compra"],
    "estado": ["estado"],
    "fecha_ult_movimiento": ["fecha ult movimiento", "fecha ultimo movimiento"],
    "n_doc": ["n doc"],
    "cantidad": ["cantidad"],
    "transportista": ["transportista"],
    "tracking": ["tracking"],
    "marca": ["marca"],
    "canal": ["canal de venta"],
    "tipo_envio": ["tipo de envio"],
    "num_envio": ["n de envio"],
    "fecha_entrega": ["fecha de entrega"],
    "tipo_despacho": ["tipo de despacho"],
    "tienda_retiro": ["tienda de retiro"],
    "metodo_pago": ["metodo de pago"],
}

WMS_MAP = {
    "orden_salida": ["ordensalida"],
    "tipo_wms": ["tipo"],
    "estado_wms": ["estado"],
    "nro_orden_cliente": ["nroordencliente"],
    "fecha_compromiso": ["fechacompromiso"],
    "nro_referencia2": ["nroreferencia2"],
    "nro_referencia_mkp": ["nroreferenciamkp"],
    "region_despacho": ["regiondespacho"],
    "tipo_despacho_wms": ["tipodespacho"],
    "fecha_despacho": ["fechadespacho"],
    "fecha_creacion": ["fechacreacion"],
}


def _log(msg: str) -> None:
    print(f"[load] {msg}")


def load_reporte() -> pd.DataFrame:
    files = sorted(REPORTE_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No se encontraron CSV en {REPORTE_DIR}")

    frames = []
    for f in files:
        header = pd.read_csv(f, sep=";", encoding="latin-1", nrows=0)
        rename = keys.build_rename_map(header.columns, REPORTE_MAP)
        df = pd.read_csv(
            f, sep=";", encoding="latin-1", low_memory=False,
            usecols=list(rename), dtype=str,
        ).rename(columns=rename)
        frames.append(df)

    reporte = pd.concat(frames, ignore_index=True)
    _log(f"{len(files)} CSV cargados, {len(reporte)} lineas brutas")

    reporte = reporte[reporte["canal"].str.strip().str.upper().isin(CANALES_INCLUIDOS)].copy()
    _log(f"{len(reporte)} lineas tras filtro de canal {CANALES_INCLUIDOS}")

    reporte = reporte.drop_duplicates(subset=["num_envio", "sku"], keep="last")
    _log(f"{len(reporte)} lineas post-dedupe (num_envio, sku)")

    reporte["fecha_trx"] = pd.to_datetime(reporte["fecha_trx"], dayfirst=True, errors="coerce")
    reporte["fecha_entrega"] = pd.to_datetime(reporte["fecha_entrega"], dayfirst=True, errors="coerce")
    if "fecha_ult_movimiento" in reporte.columns:
        reporte["fecha_ult_movimiento"] = pd.to_datetime(reporte["fecha_ult_movimiento"], dayfirst=True, errors="coerce")
    reporte["orden_compra_norm"] = reporte["orden_compra"].apply(keys.norm_orden_compra)
    reporte["envio_norm"] = reporte["num_envio"].apply(keys.norm_envio)

    _validar_reporte(reporte)
    return reporte


def load_wms() -> pd.DataFrame:
    files = list(WMS_DIR.glob("DocumentoSalida*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No se encontro DocumentoSalida*.xlsx en {WMS_DIR}")
    wms_file = max(files, key=lambda p: p.stat().st_mtime)
    _log(f"WMS: {wms_file.name}")

    df = pd.read_excel(wms_file, dtype=str)
    df = keys.resolve_columns(df, WMS_MAP)

    df["fecha_compromiso"] = pd.to_datetime(df["fecha_compromiso"], dayfirst=True, errors="coerce")
    df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"], dayfirst=True, errors="coerce")
    df["fecha_creacion"] = pd.to_datetime(df["fecha_creacion"], dayfirst=True, errors="coerce")
    df["prefijo"] = df["orden_salida"].apply(keys.prefijo_orden_salida)
    df["orden_cliente_norm"] = df["nro_orden_cliente"].apply(keys.norm_orden_compra)
    df["referencia_mkp_norm"] = df["nro_referencia_mkp"].apply(keys.norm_envio)

    df = df[df["prefijo"] != PREFIJO_TEB].copy()
    df = df.drop_duplicates(subset=["orden_salida"], keep="last")
    _log(f"WMS {len(df)} filas (sin TEB, dedupe OrdenSalida)")

    _validar_wms(df)
    return df


def load_sap_quiebres() -> pd.DataFrame:
    """Carga el export SAP de quiebres SIN guia (el mas reciente en SAP_DIR).

    Devuelve vacio si no hay archivo (la rutina sigue funcionando sin SAP).
    Columnas clave: Num Orden (OC), Incremento Id (N de envio), Estado_Quiebre_OC.
    """
    if not SAP_DIR.exists():
        return pd.DataFrame()
    files = list(SAP_DIR.glob("*.xlsx"))
    if not files:
        return pd.DataFrame()
    f = max(files, key=lambda p: p.stat().st_mtime)
    _log(f"SAP quiebres: {f.name}")
    df = pd.read_excel(f, dtype=str)
    ren = keys.build_rename_map(df.columns, {
        "sap_oc": ["num orden"],
        "sap_envio": ["incremento id"],
        "sap_estado_quiebre": ["estado quiebre"],
    })
    df = df.rename(columns=ren)
    df["oc_norm"] = df["sap_oc"].apply(keys.norm_orden_compra)
    df["envio_norm"] = df["sap_envio"].apply(keys.norm_envio)
    return df


def attach_sap_quiebres(merged: pd.DataFrame) -> pd.DataFrame:
    """Agrega columna 'sap_quiebre' (Estado_Quiebre_OC) cruzando por envio y luego OC."""
    merged = merged.copy()
    sap = load_sap_quiebres()
    if len(sap) == 0:
        merged["sap_quiebre"] = ""
        return merged
    by_envio = {k: v for k, v in
                sap.drop_duplicates("envio_norm").set_index("envio_norm")["sap_estado_quiebre"].items()
                if k}
    by_oc = {k: v for k, v in
             sap.dropna(subset=["oc_norm"]).drop_duplicates("oc_norm").set_index("oc_norm")["sap_estado_quiebre"].items()
             if k is not None}

    def _q(r):
        e = r.get("envio_norm")
        if e and e in by_envio:
            return by_envio[e] or ""
        oc = r.get("orden_compra_norm")
        if oc in by_oc:
            return by_oc[oc] or ""
        return ""

    merged["sap_quiebre"] = merged.apply(_q, axis=1)
    _log(f"SAP quiebres cruzados: {int((merged['sap_quiebre'] != '').sum())} cabeceras marcadas")
    return merged


def dedupe_cabecera(reporte: pd.DataFrame, piso_fecha=None, incluir_terminales: bool = False) -> pd.DataFrame:
    """Reduce Reporte a nivel cabecera (orden_compra, num_envio), tomando la primera linea.

    piso_fecha: si se entrega, excluye cabeceras con fecha_trx anterior (fuera del
    alcance del WMS). Evita marcar como 'NO EXISTE EN WMS' pedidos previos al WMS.
    incluir_terminales: True para incluir tambien Entregado/Anulado (necesario para SLA Courier).
    """
    if incluir_terminales:
        # Excluye SIEMPRE los Anulados (no aportan a KPI ni SLA). Solo suma Entregado.
        base = reporte[reporte["estado"] != "Anulado"].copy()
    else:
        base = reporte[~reporte["estado"].isin(ESTADOS_TERMINALES)].copy()
    if piso_fecha is not None:
        antes = len(base)
        base = base[base["fecha_trx"] >= piso_fecha]
        _log(f"{antes - len(base)} lineas descartadas por fecha_trx < {pd.Timestamp(piso_fecha).date()} (fuera del alcance WMS)")
    cab = base.drop_duplicates(subset=["orden_compra_norm", "envio_norm"], keep="first")
    _log(f"{len(cab)} cabeceras dentro del alcance ({'todos' if incluir_terminales else 'abiertos'})")
    return cab.reset_index(drop=True)


def _reserva_sin_ov(wms_row, wms_df) -> bool:
    if wms_row["prefijo"] != PREFIJO_RESERVA or str(wms_row.get("estado_wms", "")).strip() != "Cancelada":
        return False
    ov = wms_df[
        (wms_df["prefijo"] == PREFIJO_OV)
        & (
            (wms_df["orden_cliente_norm"] == wms_row["orden_cliente_norm"])
            | (wms_df["referencia_mkp_norm"] == wms_row["referencia_mkp_norm"])
        )
    ]
    return len(ov) == 0


def _pick_wms(candidatos, envio):
    """Elige la fila WMS relevante para una cabecera.

    1) match exacto por envio (referencia MKP).
    2) si hay varias (ej. reserva 13- Cancelada + OV 17- Despachada para la misma OC),
       prioriza la OV (17-), la fila Despachada, y evita las Canceladas.
    """
    # el match por envio puede devolver varias (reserva 13- y OV 17- comparten refmkp);
    # se usa como filtro, pero SIEMPRE se rankea dentro del pool resultante.
    pool = candidatos
    m = candidatos[candidatos["referencia_mkp_norm"] == envio]
    if len(m):
        pool = m
    if len(pool) == 1:
        return pool.iloc[0]
    est = pool["estado_wms"].astype(str).str.strip()
    rank = (
        (pool["prefijo"] == PREFIJO_OV).astype(int) * 4
        + (est == "Despachada").astype(int) * 2
        + (est != "Cancelada").astype(int)
    )
    return pool.loc[rank.sort_values(ascending=False).index[0]]


def merge_sources(cabecera: pd.DataFrame, wms_df: pd.DataFrame) -> pd.DataFrame:
    """Left join Reporte(cabecera) -> WMS.

    Cruce por OC (orden_compra <-> NroOrdenCliente) Y por envio (N de Envio <->
    NroReferenciaMKP). Se combinan ambos conjuntos de candidatos y se rankea
    (prioriza OV 17- despachada), lo que corrige casos donde el match por OC no
    existe o apunta a la fila equivocada.
    """
    wms_by_oc = {k: v for k, v in wms_df.groupby("orden_cliente_norm")}
    wms_by_mkp = {k: v for k, v in wms_df.groupby("referencia_mkp_norm") if k}
    wms_cols = ["orden_salida", "tipo_wms", "estado_wms", "fecha_compromiso",
                "fecha_despacho", "fecha_creacion", "region_despacho", "prefijo",
                "nro_referencia2"]

    rows = []
    for _, rep in cabecera.iterrows():
        oc = rep["orden_compra_norm"]
        envio = rep["envio_norm"]

        partes = []
        c_oc = wms_by_oc.get(oc)
        if c_oc is not None:
            partes.append(c_oc)
        if envio:
            c_mkp = wms_by_mkp.get(envio)
            if c_mkp is not None:
                partes.append(c_mkp)

        wms_row = None
        sin_wms = False
        if not partes:
            sin_wms = True
        else:
            candidatos = pd.concat(partes).drop_duplicates(subset=["orden_salida"])
            wms_row = _pick_wms(candidatos, envio)

        flag_reserva = False
        combined = rep.to_dict()
        if wms_row is not None:
            flag_reserva = _reserva_sin_ov(wms_row, wms_df)
            for c in wms_cols:
                combined[c] = wms_row.get(c)
        combined["sin_ingreso_wms"] = sin_wms
        combined["flag_reserva_sin_ov"] = flag_reserva
        rows.append(combined)

    merged = pd.DataFrame(rows)
    _log(f"merge listo: {len(merged)} cabeceras, {int(merged['sin_ingreso_wms'].sum())} sin match WMS")
    return merged


def _validar_reporte(df: pd.DataFrame) -> None:
    ft = df["fecha_trx"]
    print(f"[valid] Reporte Fecha Trx: {ft.min()} -> {ft.max()}")
    hoy = pd.Timestamp.now().normalize()
    if pd.notna(ft.max()) and ft.max() < hoy - pd.Timedelta(days=2):
        print("[ALERTA] El export de Reporte parece viejo (max Fecha Trx < hoy-2d)")


def _validar_wms(df: pd.DataFrame) -> None:
    fc = df["fecha_creacion"]
    print(f"[valid] WMS FechaCreacion: {fc.min()} -> {fc.max()}")
