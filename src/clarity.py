# -*- coding: utf-8 -*-
"""Consulta Microsoft Clarity Export API y agrupa métricas por etapa del funnel."""
import os
import re
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://www.clarity.ms/export-data/api/v1/project-live-insights"


def _headers():
    return {
        "Authorization": f"Bearer {os.environ['CLARITY_TOKEN']}",
        "Content-Type": "application/json",
    }


def _funnel_stage(url_str):
    if not url_str:
        return None
    path = urlparse(url_str).path.rstrip("/").lower()
    if path in ("", "/"):
        return "Home"
    if "/checkout/onepage/success" in path:
        return "Confirmacion"
    if "/checkout/cart" in path:
        return "Carrito"
    if "/checkout" in path:
        return "Checkout"
    if path.endswith(".html"):
        return "Producto"
    return "Categoria"


FUNNEL_ORDER = ["Home", "Categoria", "Producto", "Carrito", "Checkout", "Confirmacion"]


def fetch_clarity_data(days=3):
    params = {"numOfDays": str(days), "dimension1": "URL"}
    r = requests.get(API_URL, params=params, headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def _aggregate_metric(raw, metric_name, value_key, agg="sum"):
    metric = next((m for m in raw if m["metricName"] == metric_name), None)
    if not metric:
        return {}
    by_stage = {}
    for row in metric.get("information", []):
        stage = _funnel_stage(row.get("Url"))
        if not stage:
            continue
        val = float(row.get(value_key, 0) or 0)
        sessions = int(row.get("sessionsCount", 0) or 0)
        if stage not in by_stage:
            by_stage[stage] = {"total": 0, "count": 0, "sessions": 0}
        by_stage[stage]["total"] += val
        by_stage[stage]["count"] += 1
        by_stage[stage]["sessions"] += sessions
    result = {}
    for stage in FUNNEL_ORDER:
        if stage in by_stage:
            d = by_stage[stage]
            if agg == "avg" and d["count"] > 0:
                result[stage] = round(d["total"] / d["count"], 2)
            else:
                result[stage] = round(d["total"], 2)
    return result


def get_funnel_metrics(days=3):
    raw = fetch_clarity_data(days)

    rage = {}
    dead = {}
    quickback = {}
    scroll = {}
    engagement = {}
    traffic = {}

    for m in raw:
        name = m["metricName"]
        for row in m.get("information", []):
            stage = _funnel_stage(row.get("Url"))
            if not stage:
                continue

            if name == "Traffic":
                traffic[stage] = traffic.get(stage, 0) + int(row.get("totalSessionCount", 0) or 0)

            elif name == "RageClickCount":
                pct = float(row.get("sessionsWithMetricPercentage", 0) or 0)
                sessions = int(row.get("sessionsCount", 0) or 0)
                if stage not in rage:
                    rage[stage] = {"weighted_sum": 0, "total_sessions": 0}
                rage[stage]["weighted_sum"] += pct * sessions
                rage[stage]["total_sessions"] += sessions

            elif name == "DeadClickCount":
                pct = float(row.get("sessionsWithMetricPercentage", 0) or 0)
                sessions = int(row.get("sessionsCount", 0) or 0)
                if stage not in dead:
                    dead[stage] = {"weighted_sum": 0, "total_sessions": 0}
                dead[stage]["weighted_sum"] += pct * sessions
                dead[stage]["total_sessions"] += sessions

            elif name == "QuickbackClick":
                pct = float(row.get("sessionsWithMetricPercentage", 0) or 0)
                sessions = int(row.get("sessionsCount", 0) or 0)
                if stage not in quickback:
                    quickback[stage] = {"weighted_sum": 0, "total_sessions": 0}
                quickback[stage]["weighted_sum"] += pct * sessions
                quickback[stage]["total_sessions"] += sessions

            elif name == "ScrollDepth":
                depth = float(row.get("averageScrollDepth", 0) or 0)
                if stage not in scroll:
                    scroll[stage] = {"total": 0, "count": 0}
                scroll[stage]["total"] += depth
                scroll[stage]["count"] += 1

            elif name == "EngagementTime":
                active = float(row.get("activeTime", 0) or 0)
                if stage not in engagement:
                    engagement[stage] = {"total": 0, "count": 0}
                engagement[stage]["total"] += active
                engagement[stage]["count"] += 1

    result = {}
    for stage in FUNNEL_ORDER:
        result[stage] = {
            "rage_pct": round(rage[stage]["weighted_sum"] / rage[stage]["total_sessions"], 2) if stage in rage and rage[stage]["total_sessions"] > 0 else 0,
            "dead_pct": round(dead[stage]["weighted_sum"] / dead[stage]["total_sessions"], 2) if stage in dead and dead[stage]["total_sessions"] > 0 else 0,
            "quickback_pct": round(quickback[stage]["weighted_sum"] / quickback[stage]["total_sessions"], 2) if stage in quickback and quickback[stage]["total_sessions"] > 0 else 0,
            "scroll_depth": round(scroll[stage]["total"] / scroll[stage]["count"], 1) if stage in scroll and scroll[stage]["count"] > 0 else 0,
            "active_time_s": round(engagement[stage]["total"] / engagement[stage]["count"], 1) if stage in engagement and engagement[stage]["count"] > 0 else 0,
            "sessions": traffic.get(stage, 0),
        }

    return result


def get_top_friction_pages(days=3, top_n=10):
    raw = fetch_clarity_data(days)
    pages = {}
    for m in raw:
        name = m["metricName"]
        for row in m.get("information", []):
            url = row.get("Url")
            if not url:
                continue
            path = urlparse(url).path.rstrip("/") or "/"
            if path not in pages:
                pages[path] = {"url": path, "stage": _funnel_stage(url), "sessions": 0,
                               "rage": 0, "dead": 0, "quickback": 0, "scroll": 0}

            sessions = int(row.get("sessionsCount", 0) or 0)

            if name == "Traffic":
                pages[path]["sessions"] = max(pages[path]["sessions"], int(row.get("totalSessionCount", 0) or 0))
            elif name == "RageClickCount":
                pages[path]["sessions"] = max(pages[path]["sessions"], sessions)
                pages[path]["rage"] = max(pages[path]["rage"], float(row.get("sessionsWithMetricPercentage", 0) or 0))
            elif name == "DeadClickCount":
                pages[path]["dead"] = max(pages[path]["dead"], float(row.get("sessionsWithMetricPercentage", 0) or 0))
            elif name == "QuickbackClick":
                pages[path]["quickback"] = max(pages[path]["quickback"], float(row.get("sessionsWithMetricPercentage", 0) or 0))
            elif name == "ScrollDepth":
                pages[path]["scroll"] = max(pages[path]["scroll"], float(row.get("averageScrollDepth", 0) or 0))

    scored = []
    for p in pages.values():
        if p["sessions"] < 5:
            continue
        p["friction_score"] = round(p["rage"] * 3 + p["dead"] * 2 + p["quickback"] * 2 + max(0, 50 - p["scroll"]), 1)
        scored.append(p)

    scored.sort(key=lambda x: x["friction_score"], reverse=True)
    return scored[:top_n]


HISTORIAL_DIR = Path(__file__).parent.parent / "data" / "clarity"


def guardar_snapshot(days=1):
    """Descarga métricas del último día y las agrega al historial JSON."""
    HISTORIAL_DIR.mkdir(parents=True, exist_ok=True)
    historial_path = HISTORIAL_DIR / "clarity_historial.json"

    if historial_path.exists():
        historial = json.loads(historial_path.read_text(encoding="utf-8"))
    else:
        historial = []

    hoy = date.today().isoformat()
    if any(h["fecha"] == hoy for h in historial):
        return historial

    funnel = get_funnel_metrics(days)
    friction = get_top_friction_pages(days, top_n=15)

    raw = fetch_clarity_data(days)
    traffic_total = 0
    for m in raw:
        if m["metricName"] == "Traffic":
            for row in m.get("information", []):
                traffic_total += int(row.get("totalSessionCount", 0) or 0)

    entry = {
        "fecha": hoy,
        "funnel": funnel,
        "top_friction": friction,
        "total_sessions": traffic_total,
    }
    historial.append(entry)
    historial_path.write_text(json.dumps(historial, indent=2, ensure_ascii=False), encoding="utf-8")
    return historial


def cargar_historial():
    historial_path = HISTORIAL_DIR / "clarity_historial.json"
    if not historial_path.exists():
        return []
    return json.loads(historial_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    print("=== GUARDANDO SNAPSHOT ===")
    h = guardar_snapshot(1)
    print(f"Historial: {len(h)} dias guardados")

    print("\n=== FUNNEL METRICS ===")
    fm = get_funnel_metrics(3)
    for stage, data in fm.items():
        print(f"  {stage:15s} | sessions={data['sessions']:5d} | rage={data['rage_pct']:5.1f}% | dead={data['dead_pct']:5.1f}% | quickback={data['quickback_pct']:5.1f}% | scroll={data['scroll_depth']:5.1f}% | active={data['active_time_s']:5.1f}s")

    print("\n=== TOP FRICTION PAGES ===")
    fp = get_top_friction_pages(3)
    for p in fp:
        print(f"  [{p['stage']:12s}] score={p['friction_score']:6.1f} | rage={p['rage']:5.1f}% | dead={p['dead']:5.1f}% | qb={p['quickback']:5.1f}% | scroll={p['scroll']:5.1f}% | {p['url'][:60]}")
