"""Carga y cruce con Big Ticket (DispatchTrack).

Consume un dump JSON generado con JavaScript en el navegador autenticado
(ver docs/como-descargar-bigticket.md). El dump es una lista de dicts:
    {code, estado, subestado, cliente, fecha_ruta, ventana_min, ventana_max, created_at}

El cruce es por N° de envío (code de Big Ticket == num_envio del OMS, 9 dígitos zfill).
"""
from pathlib import Path
import json

import pandas as pd

import keys


def load_bigticket_dump(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[BIGTICKET] Dump no encontrado en {path}, skip")
        return pd.DataFrame()
    data = json.loads(path.read_text(encoding="utf-8"))
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["envio_norm"] = df["code"].apply(keys.norm_envio)
    for col in ("ventana_min", "ventana_max", "created_at"):
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.tz_localize(None)
    df["fecha_ruta"] = pd.to_datetime(df["fecha_ruta"], errors="coerce")
    df = df.drop_duplicates(subset=["envio_norm"], keep="last")
    print(f"[BIGTICKET] {len(df)} despachos cargados")
    return df


def enrich_dataframe(df: pd.DataFrame, dump_path: Path) -> pd.DataFrame:
    bt = load_bigticket_dump(dump_path)
    if bt.empty:
        for c in ("bt_estado", "bt_subestado", "bt_fecha_ruta", "bt_ventana_max"):
            df[c] = ""
        return df

    # solo pedidos abiertos donde el transportista es Big Ticket / DispatchTrack
    bt = bt.set_index("envio_norm")
    df = df.copy()
    def _g(env, col):
        try:
            return bt.at[env, col]
        except (KeyError, TypeError):
            return None

    df["bt_estado"] = df["envio_norm"].apply(lambda e: _g(e, "estado") if e else None)
    df["bt_subestado"] = df["envio_norm"].apply(lambda e: _g(e, "subestado") if e else None)
    df["bt_fecha_ruta"] = df["envio_norm"].apply(lambda e: _g(e, "fecha_ruta") if e else None)
    df["bt_ventana_max"] = df["envio_norm"].apply(lambda e: _g(e, "ventana_max") if e else None)

    cruzados = df["bt_estado"].notna().sum()
    print(f"[BIGTICKET] {cruzados} pedidos cruzados con Big Ticket")
    return df
