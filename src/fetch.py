# -*- coding: utf-8 -*-
"""Descarga automatica de fuentes desde sus portales (sin export manual).

- OMSWeb reporteria detallada: GET /webapp/wsrest/getReporteria (JSON base64 -> CSV latin-1 ';').
- WMS DocumentoSalida: POST ASP.NET WebForms a DocumentoSalida.aspx (boton Excel) -> xlsx.

Credenciales por variables de entorno: OMS_USER/OMS_PASS y WMS_USER/WMS_PASS.
Solo funciona desde un equipo dentro de la red de Cannon (el WMS es IP interna 10.x).
"""
import os
import re
import base64
from datetime import date, datetime
from html import unescape
from pathlib import Path

import requests

OMS_BASE = "https://canontex.bbr.cl"
WMS_BASE = "http://10.1.0.3:84/CANNON/EnfasysWMS_Admin/VIEW/"
WMS_LOGIN = WMS_BASE + "Security/login.aspx"
WMS_DOCSAL = WMS_BASE + "Salida/DocumentoSalida.aspx"

WMS_TIPOFECHA_COMPROMISO = "3"


def _log(msg: str) -> None:
    print(f"[fetch] {msg}")


# ---------------------------------------------------------------- OMSWeb
def _oms_login() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    lp = s.get(f"{OMS_BASE}/webapp/login?logout", timeout=30)
    lp.raise_for_status()
    m = re.search(r'name="_csrf" value="([^"]+)"', lp.text)
    if not m:
        raise RuntimeError("OMSWeb: no se encontro token _csrf")
    r = s.post(f"{OMS_BASE}/login",
               data={"_csrf": m.group(1),
                     "username": os.environ["OMS_USER"],
                     "password": os.environ["OMS_PASS"]},
               timeout=30)
    r.raise_for_status()
    if "login" in r.url.lower():
        raise RuntimeError("OMSWeb: login fallido (credenciales o CSRF)")
    return s


def _fmt_oms(d: date) -> str:
    # formato que espera getReporteria: YYYY-M-D 00:00:00 (mes/dia sin cero)
    return f"{d.year}-{d.month}-{d.day} 00:00:00"


def fetch_reporteria_csv(desde: date, hasta: date, dest: Path) -> Path:
    """Descarga la reporteria detallada al archivo dest (CSV, sep ';', latin-1)."""
    s = _oms_login()
    r = s.get(f"{OMS_BASE}/webapp/wsrest/getReporteria",
              params={"fechaIni": _fmt_oms(desde), "fechaFin": _fmt_oms(hasta)},
              timeout=600)
    r.raise_for_status()
    b64 = r.json()["reporteBase64"]
    raw = base64.b64decode(b64)
    # El API devuelve el CSV en UTF-8; el pipeline (y el export manual) usan latin-1.
    # Transcodificamos para que el archivo quede byte-compatible con load.py.
    text = raw.decode("utf-8")
    data = text.encode("latin-1", errors="replace")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    _log(f"reporteria {desde} -> {hasta}: {len(data)} bytes en {dest.name}")
    return dest


# ---------------------------------------------------------------- WMS
def _wms_hidden(html: str, name: str) -> str:
    m = re.search(r'(?:id|name)="' + re.escape(name) + r'"[^>]*value="([^"]*)"', html)
    return unescape(m.group(1)) if m else ""


def _wms_login() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    r = s.get(WMS_LOGIN, timeout=30)
    r.raise_for_status()
    s.post(WMS_LOGIN, data={
        "__LASTFOCUS": "", "__EVENTTARGET": "", "__EVENTARGUMENT": "",
        "__VIEWSTATE": _wms_hidden(r.text, "__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": _wms_hidden(r.text, "__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": _wms_hidden(r.text, "__EVENTVALIDATION"),
        "hdnIpPublica": "",
        "txtUsuario": os.environ["WMS_USER"],
        "txtClave": os.environ["WMS_PASS"],
        "CmdLogin": "Ingresar",
    }, timeout=30, allow_redirects=True)
    return s


def _serialize_form(html: str) -> dict:
    """Serializa inputs (text/hidden) y selects (opcion seleccionada o primera)."""
    data = {}
    for m in re.finditer(r'<input\b[^>]*>', html):
        tag = m.group(0)
        name = re.search(r'name="([^"]+)"', tag)
        if not name:
            continue
        name = name.group(1)
        typ = re.search(r'type="([^"]+)"', tag)
        typ = typ.group(1) if typ else "text"
        if typ in ("submit", "button", "image", "reset"):
            continue
        val = re.search(r'value="([^"]*)"', tag)
        val = unescape(val.group(1)) if val else ""
        if typ in ("checkbox", "radio"):
            if re.search(r'\bchecked\b', tag):
                data[name] = val or "on"
            continue
        data[name] = val
    for sm in re.finditer(r'<select\b[^>]*name="([^"]+)"[^>]*>(.*?)</select>', html, re.DOTALL):
        name, body = sm.group(1), sm.group(2)
        sel = (re.search(r'<option[^>]*\bselected\b[^>]*value="([^"]*)"', body)
               or re.search(r'<option[^>]*value="([^"]*)"[^>]*\bselected\b', body))
        if sel:
            data[name] = unescape(sel.group(1))
        else:
            first = re.search(r'<option[^>]*value="([^"]*)"', body)
            data[name] = unescape(first.group(1)) if first else ""
    return data


def _fmt_wms(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def fetch_wms_xlsx(desde: date, hasta: date, dest: Path, timeout: int = 600) -> Path:
    """Descarga el DocumentoSalida (xlsx) filtrado por Fecha Compromiso desde->hasta."""
    s = _wms_login()
    page = s.get(WMS_DOCSAL, timeout=60)
    page.raise_for_status()
    data = _serialize_form(page.text)
    data["ctl00$bodyContent$txtFechaDesde"] = _fmt_wms(desde)
    data["ctl00$bodyContent$txtFechaHasta"] = _fmt_wms(hasta)
    data["ctl00$bodyContent$ddlTipoFecha"] = WMS_TIPOFECHA_COMPROMISO
    data["ctl00$bodyContent$ddlOwner"] = "CANNON"
    data["ctl00$bodyContent$btnExcelTradicional"] = "Excel"
    data.setdefault("__EVENTTARGET", "")
    data.setdefault("__EVENTARGUMENT", "")

    r = s.post(WMS_DOCSAL, data=data, timeout=timeout)
    r.raise_for_status()
    if r.content[:2] != b"PK":
        raise RuntimeError(f"WMS: la respuesta no es xlsx (Content-Type={r.headers.get('Content-Type')})")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    _log(f"WMS {desde} -> {hasta}: {len(r.content)} bytes en {dest.name}")
    return dest


if __name__ == "__main__":
    # prueba manual: python src/fetch.py 2026-07-14 2026-07-21 <carpeta_dest>
    import sys
    d1 = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    d2 = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
    out = Path(sys.argv[3] if len(sys.argv) > 3 else ".")
    fetch_reporteria_csv(d1, d2, out / f"reporteria_{d1}_{d2}.csv")
    fetch_wms_xlsx(d1, d2, out / "DocumentoSalida_auto.xlsx")
