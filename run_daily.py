"""Rutina diaria: carga -> cruce -> reglas -> Excel + dashboard, y resumen en consola.

Uso:
    python run_daily.py

Agendar con Task Scheduler (ver README).
"""
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))
import load
import rules
import report
import dashboard


def _kpis(resultado, hoy_str):
    total = len(resultado)
    atrasados = resultado[resultado["atrasado"]]
    n_atr = len(atrasados)
    dias_prom = atrasados["dias_atraso"].mean()
    diag = [(k, v) for k, v in atrasados["diagnostico"].value_counts().items()]
    return {
        "fecha": hoy_str,
        "total_abiertos": total,
        "atrasados": n_atr,
        "pct_atrasados": round(100 * n_atr / total, 1) if total else 0,
        "pct_otif": round(100 * (total - n_atr) / total, 1) if total else 0,
        "dias_atraso_prom": round(dias_prom, 1) if pd.notna(dias_prom) else 0,
        "reserva_sin_ov": int(resultado["flag_reserva_sin_ov"].sum()),
        "no_wms": int(resultado["sin_ingreso_wms"].sum()),
        "por_diagnostico": diag,
    }


def _validar_cobertura(reporte, wms):
    rmin, rmax = reporte["fecha_trx"].min(), reporte["fecha_trx"].max()
    wmin, wmax = wms["fecha_creacion"].min(), wms["fecha_creacion"].max()
    if pd.notna(wmax) and pd.notna(rmax) and abs((rmax - wmax).days) > 3:
        print("[ALERTA] Rangos WMS y Reporte no coinciden (una fuente puede estar desactualizada):")
        print(f"         Reporte hasta {rmax.date()} | WMS hasta {wmax.date()}")


def _git_push_dashboard(json_path, hoy_str):
    """Actualiza dashboard-data.json en GitHub (git add -> commit -> push)."""
    try:
        repo_root = Path(__file__).parent
        subprocess.run(["git", "-C", str(repo_root), "add", "dashboard-data.json"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo_root), "commit", "-m", f"[AUTO] Actualizar dashboard-data.json {hoy_str}"], check=True, capture_output=True)
        result = subprocess.run(["git", "-C", str(repo_root), "push"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[GIT] Pushed dashboard-data.json a GitHub ✓")
        else:
            print(f"[GIT] Error al push: {result.stderr}")
    except Exception as e:
        print(f"[GIT] Error: {e}")


def main():
    hoy = pd.Timestamp(datetime.now().date())
    hoy_str = hoy.strftime("%Y-%m-%d")

    reporte = load.load_reporte()
    wms = load.load_wms()
    _validar_cobertura(reporte, wms)

    piso = wms["fecha_creacion"].min()
    cabecera = load.dedupe_cabecera(reporte, piso_fecha=piso)
    merged = load.merge_sources(cabecera, wms)
    merged = load.attach_sap_quiebres(merged)
    resultado = rules.aplicar_reglas(merged, hoy)

    kpis = _kpis(resultado, hoy_str)

    out = load.OUTPUT_DIR
    xlsx_path = out / f"resumen_atrasos_{hoy_str}.xlsx"
    dash_path = out / f"dashboard_{hoy_str}.html"
    dash_latest = out / "dashboard.html"

    report.build_excel(resultado, kpis, xlsx_path)
    generado = datetime.now().strftime("%Y-%m-%d %H:%M")
    dashboard.build_dashboard(resultado, kpis, dash_path, generado)
    dashboard.build_dashboard(resultado, kpis, dash_latest, generado)

    # Generar JSON para dashboard Vercel (datos en vivo)
    json_path = Path(__file__).parent / "dashboard-data.json"
    dashboard.export_dashboard_json(resultado, hoy_str, json_path)
    _git_push_dashboard(json_path, hoy_str)

    # casos sin regla, para iterar
    manual = resultado[resultado["diagnostico"] == "REVISAR MANUAL"]

    print("\n" + "=" * 60)
    print(f"RESUMEN EJECUTIVO — {hoy_str}")
    print("=" * 60)
    print(f"Pedidos abiertos      : {kpis['total_abiertos']}")
    print(f"Atrasados             : {kpis['atrasados']} ({kpis['pct_atrasados']}%)")
    print(f"% OTIF                : {kpis['pct_otif']}%")
    print(f"Días atraso promedio  : {kpis['dias_atraso_prom']}")
    print(f"No están en WMS       : {kpis['no_wms']}")
    print(f"Reservas 13- sin OV   : {kpis['reserva_sin_ov']}")
    print("\nAtrasados por diagnóstico:")
    for diag, n in kpis["por_diagnostico"]:
        print(f"  - {diag}: {n}")
    if len(manual):
        print(f"\n[REVISAR MANUAL] {len(manual)} casos sin regla (combinaciones no cubiertas).")
    print(f"\nExcel     : {xlsx_path}")
    print(f"Dashboard : {dash_path}")
    print(f"Dashboard : {dash_latest} (latest)")
    print(f"JSON      : {json_path}")


if __name__ == "__main__":
    main()
