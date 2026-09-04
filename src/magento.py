"""Cliente Magento REST API para detectar pedidos que requieren gestión.

Docs: https://developer.adobe.com/commerce/webapi/rest/

Flujo:
1. get_token(): POST /rest/V1/integration/admin/token con user/pass (dura 1h, se cachea).
2. fetch_canceled_last_days(N): cancelados+closed con pago autorizado sin anular.
3. fetch_pending_last_days(N): pedidos pending/pending_payment que llevan más de N días.
4. resumen_diario(): combina ambos para alerta.
"""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

BASE = os.getenv("MAGENTO_URL", "").rstrip("/")
USER = os.getenv("MAGENTO_USER")
PASS = os.getenv("MAGENTO_PASS")
TIMEOUT = 60

_token_cache = {"token": None, "expires": 0}


def get_token() -> str:
    """POST admin/token. Cache 55 min (token dura 1h)."""
    if _token_cache["token"] and time.time() < _token_cache["expires"]:
        return _token_cache["token"]
    r = requests.post(
        f"{BASE}/rest/V1/integration/admin/token",
        json={"username": USER, "password": PASS},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    token = r.json()  # devuelve string plano
    _token_cache["token"] = token
    _token_cache["expires"] = time.time() + 3300  # 55 min
    return token


def _get(path: str, params: dict, retries: int = 3) -> dict:
    token = get_token()
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{BASE}{path}",
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                params=params, timeout=TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            if r.status_code in (502, 503, 504) and attempt < retries - 1:
                import time
                time.sleep(5 * (attempt + 1))
                continue
            raise
    return {}


def _fetch_paginado(params: dict, page_size: int) -> list:
    """Trae TODAS las paginas de /V1/orders para los filtros dados.
    fetch_canceled_last_days/fetch_closed_last_days/fetch_pending_last_days
    filtran por ventanas con mas de page_size pedidos con facilidad (Magento
    devuelve por entity_id ascendente), asi que sin paginar se pierden
    silenciosamente los pedidos mas nuevos de la ventana."""
    items = []
    page = 1
    while True:
        params["searchCriteria[currentPage]"] = page
        data = _get("/rest/V1/orders", params)
        batch = data.get("items", [])
        items.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return items


def fetch_canceled_last_days(days: int = 3, page_size: int = 100) -> list:
    """Trae pedidos con status in (canceled, oc_cancel) actualizados en los últimos N días.

    No incluye "closed": esas son devoluciones ya cerradas por el ERP, no
    casos que requieran gestión. "oc_cancel" es el estado real que usa
    Magento para "Cancelada" en el front (canceled = "Error en pago").
    """
    desde = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    params = {
        "searchCriteria[filter_groups][0][filters][0][field]": "status",
        "searchCriteria[filter_groups][0][filters][0][value]": "canceled,oc_cancel",
        "searchCriteria[filter_groups][0][filters][0][condition_type]": "in",
        "searchCriteria[filter_groups][1][filters][0][field]": "updated_at",
        "searchCriteria[filter_groups][1][filters][0][value]": desde,
        "searchCriteria[filter_groups][1][filters][0][condition_type]": "gteq",
        "searchCriteria[pageSize]": page_size,
    }
    return _fetch_paginado(params, page_size)


def _webpay_authorized_amount(payment: dict) -> float:
    """Para transbank_webpay: si Magento canceló el pedido antes de facturarlo,
    total_paid/amount_paid/amount_authorized quedan en null aunque Transbank sí
    haya autorizado el cobro. La única prueba real queda en additional_information
    (respuesta cruda del gateway)."""
    if payment.get("method") != "transbank_webpay":
        return 0.0
    for item in payment.get("additional_information") or []:
        try:
            data = json.loads(item)
        except (TypeError, ValueError):
            continue
        if isinstance(data, dict) and data.get("status") == "AUTHORIZED" and data.get("responseCode") == 0:
            return float(data.get("amount") or 0)
    return 0.0


def _payment_flags(order: dict) -> dict:
    """Extrae señales de pago del pedido. Un pedido problemático es el que capturó plata pero se canceló."""
    total_paid = float(order.get("total_paid") or 0)
    total_refunded = float(order.get("total_refunded") or 0)
    p = order.get("payment") or {}
    amount_paid = float(p.get("amount_paid") or 0)
    amount_authorized = float(p.get("amount_authorized") or 0)
    last_trans = str(p.get("last_trans_id") or "")
    webpay_amount = _webpay_authorized_amount(p)
    autorizacion_sin_cerrar = (
        (total_paid > 0 and total_paid > total_refunded)
        or amount_paid > 0
        or (amount_authorized > 0 and amount_paid == 0)
        or webpay_amount > 0
    ) and not last_trans.endswith("-expire")
    return {
        "total_paid": total_paid or webpay_amount,
        "total_refunded": total_refunded,
        "amount_paid": amount_paid,
        "amount_authorized": amount_authorized,
        "last_trans_id": last_trans,
        "requiere_gestion": autorizacion_sin_cerrar,
    }


def filter_with_payment(orders: list) -> list:
    """Deja solo los que requieren gestión (pago autorizado/capturado pero canceladas)."""
    salida = []
    for o in orders:
        flags = _payment_flags(o)
        if flags["requiere_gestion"]:
            salida.append({
                "increment_id": o.get("increment_id"),
                "created_at": o.get("created_at"),
                "updated_at": o.get("updated_at"),
                "status": o.get("status"),
                "grand_total": o.get("grand_total"),
                "cliente": f"{o.get('customer_firstname','')} {o.get('customer_lastname','')}".strip(),
                "email": o.get("customer_email"),
                "metodo_pago": (o.get("payment") or {}).get("method"),
                **flags,
            })
    return salida


def fetch_closed_last_days(days: int = 3, page_size: int = 100) -> list:
    """Trae pedidos 'closed' actualizados en los últimos N días.

    "closed" generalmente son devoluciones ya procesadas por el ERP (ver
    memoria feedback-magento-cancelados) y por eso se excluyen de
    fetch_canceled_last_days. Pero un subconjunto sí requiere gestión: ver
    filter_closed_sin_reembolso.
    """
    desde = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    params = {
        "searchCriteria[filter_groups][0][filters][0][field]": "status",
        "searchCriteria[filter_groups][0][filters][0][value]": "closed",
        "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
        "searchCriteria[filter_groups][1][filters][0][field]": "updated_at",
        "searchCriteria[filter_groups][1][filters][0][value]": desde,
        "searchCriteria[filter_groups][1][filters][0][condition_type]": "gteq",
        "searchCriteria[pageSize]": page_size,
    }
    return _fetch_paginado(params, page_size)


def filter_closed_sin_reembolso(orders: list) -> list:
    """Deja solo 'closed' con pago capturado y total_refunded=0 (plata sin conciliar).

    A diferencia de filter_with_payment, exige refund=0 explícito: un closed
    totalmente reembolsado (total_paid == total_refunded) no requiere gestión,
    aunque amount_paid siga marcando >0 en el payment original.
    """
    salida = []
    for o in orders:
        flags = _payment_flags(o)
        dinero_capturado = flags["total_paid"] > 0 or flags["amount_paid"] > 0
        sin_reembolso = flags["total_refunded"] == 0
        if dinero_capturado and sin_reembolso:
            salida.append({
                "increment_id": o.get("increment_id"),
                "created_at": o.get("created_at"),
                "updated_at": o.get("updated_at"),
                "status": o.get("status"),
                "grand_total": o.get("grand_total"),
                "cliente": f"{o.get('customer_firstname','')} {o.get('customer_lastname','')}".strip(),
                "email": o.get("customer_email"),
                "metodo_pago": (o.get("payment") or {}).get("method"),
                **flags,
            })
    return salida


def fetch_pending_last_days(days: int = 3, max_days: int = 30, page_size: int = 100) -> list:
    """Trae pedidos pending/pending_payment creados entre max_days y days atrás."""
    desde = (datetime.now() - timedelta(days=max_days)).strftime("%Y-%m-%d 00:00:00")
    hasta = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 23:59:59")
    params = {
        "searchCriteria[filter_groups][0][filters][0][field]": "status",
        "searchCriteria[filter_groups][0][filters][0][value]": "pending,pending_payment",
        "searchCriteria[filter_groups][0][filters][0][condition_type]": "in",
        "searchCriteria[filter_groups][1][filters][0][field]": "created_at",
        "searchCriteria[filter_groups][1][filters][0][value]": hasta,
        "searchCriteria[filter_groups][1][filters][0][condition_type]": "lteq",
        "searchCriteria[filter_groups][2][filters][0][field]": "created_at",
        "searchCriteria[filter_groups][2][filters][0][value]": desde,
        "searchCriteria[filter_groups][2][filters][0][condition_type]": "gteq",
        "searchCriteria[pageSize]": page_size,
    }
    return _fetch_paginado(params, page_size)


def filter_pending_with_payment(orders: list) -> list:
    """Deja solo pendientes que tengan pago autorizado o capturado."""
    salida = []
    for o in orders:
        flags = _payment_flags(o)
        if not flags["requiere_gestion"]:
            continue
        dias = (datetime.now() - datetime.strptime(o.get("created_at", ""), "%Y-%m-%d %H:%M:%S")).days if o.get("created_at") else 0
        salida.append({
            "increment_id": o.get("increment_id"),
            "created_at": o.get("created_at"),
            "updated_at": o.get("updated_at"),
            "status": o.get("status"),
            "grand_total": o.get("grand_total"),
            "cliente": f"{o.get('customer_firstname','')} {o.get('customer_lastname','')}".strip(),
            "email": o.get("customer_email"),
            "metodo_pago": (o.get("payment") or {}).get("method"),
            "dias_pendiente": dias,
            **flags,
        })
    return salida


def resumen_diario(days: int = 3) -> dict:
    """Devuelve {cancelados, pendientes, ...}."""
    # Cancelados con pago
    orders_cancel = fetch_canceled_last_days(days=days)
    casos_cancel = filter_with_payment(orders_cancel)

    # Closed sin reembolso (subconjunto de "closed" que sí requiere gestión)
    try:
        orders_closed = fetch_closed_last_days(days=days)
        casos_closed = filter_closed_sin_reembolso(orders_closed)
    except Exception as e:
        print(f"[MAGENTO] Error consultando closed: {e}")
        orders_closed = []
        casos_closed = []

    # Pendientes > N días
    try:
        orders_pending = fetch_pending_last_days(days=days)
        casos_pending = filter_pending_with_payment(orders_pending)
    except Exception as e:
        print(f"[MAGENTO] Error consultando pendientes: {e}")
        orders_pending = []
        casos_pending = []

    return {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ventana_dias": days,
        "total_cancelados_revisados": len(orders_cancel),
        "cancelados_con_pago": len(casos_cancel),
        "casos_cancelados": casos_cancel,
        "total_closed_revisados": len(orders_closed),
        "closed_sin_reembolso": len(casos_closed),
        "casos_closed_sin_reembolso": casos_closed,
        "total_pendientes": len(orders_pending),
        "casos_pendientes": casos_pending,
    }


if __name__ == "__main__":
    import json
    r = resumen_diario(3)
    print(json.dumps(r, indent=2, ensure_ascii=False))
