"""Normalizacion de llaves de cruce y resolucion de nombres de columna.

Los exports vienen con acentos y espacios inconsistentes (y el CSV en latin-1),
asi que las columnas se resuelven por coincidencia difusa a nombres canonicos ASCII.
"""
import unicodedata

import pandas as pd


def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)
    )


def _norm(s: str) -> str:
    return _strip_accents(s).strip().lower().replace("  ", " ")


def build_rename_map(columns, mapping: dict) -> dict:
    """Devuelve {columna_original: nombre_canonico}.

    mapping: {nombre_canonico: [substrings candidatos]}. Se elige la primera
    columna cuyo nombre normalizado contenga TODOS los tokens de algun candidato.
    """
    norm_cols = {col: _norm(col) for col in columns}
    rename = {}
    for canonico, candidatos in mapping.items():
        for cand in candidatos:
            tokens = _norm(cand).split()
            match = next(
                (col for col, n in norm_cols.items()
                 if all(t in n for t in tokens) and col not in rename),
                None,
            )
            if match:
                rename[match] = canonico
                break
    return rename


def resolve_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Renombra columnas de df a nombres canonicos (ver build_rename_map)."""
    return df.rename(columns=build_rename_map(df.columns, mapping))


def norm_orden_compra(value):
    """Quita ceros a la izquierda y castea a int. None si no es parseable."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    s = s.lstrip("0") or "0"
    try:
        return int(s)
    except ValueError:
        return None


def norm_envio(value) -> str:
    """String de 9 digitos con zfill. '' si vacio."""
    if pd.isna(value):
        return ""
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if not s or s == "-":
        return ""
    return s.zfill(9)


def prefijo_orden_salida(orden_salida) -> str:
    """Primeros 2 caracteres de OrdenSalida: '12'=TEB, '13'=reserva, '17'=OV."""
    if pd.isna(orden_salida):
        return ""
    return str(orden_salida).strip()[:2]
