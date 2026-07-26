"""Cliente FedEx Track API v1.

Docs: https://developer.fedex.com/api/en-us/catalog/track/v1/docs.html

Flujo:
1. get_token(): OAuth2 client_credentials -> access_token (cache 55min)
2. track_batch(numbers): consulta hasta 30 tracking numbers en 1 request
3. enrich_dataframe(df): agrega columnas fedex_estado, fedex_fecha, fedex_evento

Credenciales en .env (no versionar):
    FEDEX_CLIENT_ID=...
    FEDEX_CLIENT_SECRET=...
    FEDEX_ENV=production  # o sandbox
"""
import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

CLIENT_ID = os.getenv("FEDEX_CLIENT_ID")
CLIENT_SECRET = os.getenv("FEDEX_CLIENT_SECRET")
ENV = os.getenv("FEDEX_ENV", "production").lower()

BASE = "https://apis.fedex.com" if ENV == "production" else "https://apis-sandbox.fedex.com"
TIMEOUT = 30

_token_cache = {"token": None, "expires": 0}


def get_token() -> str:
    """OAuth2 client_credentials. Cache 55 minutos (token dura 1h)."""
    if _token_cache["token"] and time.time() < _token_cache["expires"]:
        return _token_cache["token"]

    r = requests.post(
        f"{BASE}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    j = r.json()
    _token_cache["token"] = j["access_token"]
    _token_cache["expires"] = time.time() + j.get("expires_in", 3600) - 300
    return _token_cache["token"]


def track_batch(numbers: list[str]) -> dict:
    """Consulta hasta 30 tracking numbers. Devuelve dict {tracking: {estado, fecha, evento}}."""
    numbers = [n for n in numbers if n and str(n).strip()]
    if not numbers:
        return {}

    resultados = {}
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-locale": "es_CL",
    }

    for i in range(0, len(numbers), 30):
        chunk = numbers[i:i + 30]
        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": n}} for n in chunk],
        }
        try:
            r = requests.post(
                f"{BASE}/track/v1/trackingnumbers",
                json=payload, headers=headers, timeout=TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[FEDEX] Error batch {i}-{i+30}: {e}")
            continue

        for res in data.get("output", {}).get("completeTrackResults", []):
            tn = res.get("trackingNumber")
            tracks = res.get("trackResults", [])
            if not tracks:
                continue
            t = tracks[0]
            estado = t.get("latestStatusDetail", {}).get("description", "")
            code = t.get("latestStatusDetail", {}).get("code", "")
            fecha = ""
            eventos = t.get("scanEvents", [])
            if eventos:
                fecha = eventos[0].get("date", "")
            resultados[tn] = {
                "fedex_estado": estado,
                "fedex_codigo": code,
                "fedex_fecha": fecha,
                "fedex_eventos": len(eventos),
            }

    return resultados


def enrich_dataframe(df: pd.DataFrame, col_tracking: str = "tracking",
                     col_transportista: str = "transportista") -> pd.DataFrame:
    """Agrega columnas fedex_* al DataFrame.
    Solo consulta filas con transportista FedEx y tracking de 12 dígitos (formato válido)."""
    if col_tracking not in df.columns:
        print(f"[FEDEX] Columna '{col_tracking}' no encontrada, skip")
        return df

    tr = df[col_tracking].astype(str).str.strip()
    es_fedex = df[col_transportista].astype(str).str.contains("edex", case=False, na=False) if col_transportista in df.columns else pd.Series(True, index=df.index)
    valido = (tr.str.len() == 12) & tr.str.match(r"^\d+$", na=False)
    mask = es_fedex & valido

    numeros = tr[mask].unique().tolist()
    print(f"[FEDEX] Consultando {len(numeros)} tracking FedEx (de {mask.sum()} filas abiertas)...")

    if not numeros:
        df = df.copy()
        for c in ("fedex_estado", "fedex_codigo", "fedex_fecha", "fedex_eventos"):
            df[c] = "" if c != "fedex_eventos" else 0
        return df

    resultados = track_batch(numeros)
    print(f"[FEDEX] Recibidos {len(resultados)} resultados")

    df = df.copy()
    def _g(k, col):
        r = resultados.get(str(k).strip(), {})
        return r.get(col, "" if col != "fedex_eventos" else 0)
    df["fedex_estado"] = tr.apply(lambda x: _g(x, "fedex_estado"))
    df["fedex_codigo"] = tr.apply(lambda x: _g(x, "fedex_codigo"))
    df["fedex_fecha"] = tr.apply(lambda x: _g(x, "fedex_fecha"))
    df["fedex_eventos"] = tr.apply(lambda x: _g(x, "fedex_eventos"))
    return df


if __name__ == "__main__":
    # Test rapido
    try:
        token = get_token()
        print(f"[OK] Token obtenido: {token[:20]}...")
    except Exception as e:
        print(f"[ERROR] {e}")
