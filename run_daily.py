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
import fedex
import bigticket


def _kpis(resultado, hoy_str):
    total = len(resultado)
    atrasados = resultado[resultado["atrasado"]]
    n_atr = len(atrasados)
    dias_prom = atrasados["dias_atraso"].mean()
    diag = [(k, v) for k, v in atrasados["diagnostico"].value_counts().items()]

    # SLA Ecommerce: 48 horas creación → despacho
    sla_ecom_cumplido = resultado[resultado["sla_ecommerce"] == True]
    con_sla_ecom = resultado[resultado["sla_ecommerce"].notna()]
    pct_sla_ecom = round(100 * len(sla_ecom_cumplido) / len(con_sla_ecom), 1) if len(con_sla_ecom) > 0 else 0

    # SLA Operación: despacho → compromiso
    sla_oper_cumplido = resultado[resultado["sla_operacion"] == True]
    con_sla_oper = resultado[resultado["sla_operacion"].notna()]
    pct_sla_oper = round(100 * len(sla_oper_cumplido) / len(con_sla_oper), 1) if len(con_sla_oper) > 0 else 0

    # SLA Courier: última milla (solo Domicilio y Fecha Pactada, sobre pedidos entregados)
    sla_cour_cumplido = resultado[resultado["sla_courier"] == True]
    con_sla_cour = resultado[resultado["sla_courier"].notna()]
    pct_sla_cour = round(100 * len(sla_cour_cumplido) / len(con_sla_cour), 1) if len(con_sla_cour) > 0 else 0

    return {
        "fecha": hoy_str,
        "total_abiertos": total,
        "atrasados": n_atr,
        "pct_atrasados": round(100 * n_atr / total, 1) if total else 0,
        "pct_otif": round(100 * (total - n_atr) / total, 1) if total else 0,
        "dias_atraso_prom": round(dias_prom, 1) if pd.notna(dias_prom) else 0,
        "reserva_sin_ov": int(resultado["flag_reserva_sin_ov"].sum()),
        "no_wms": int(resultado["sin_ingreso_wms"].sum()),
        "pct_sla_ecommerce": pct_sla_ecom,
        "pct_sla_operacion": pct_sla_oper,
        "pct_sla_courier": pct_sla_cour,
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
    # Incluir entregados/anulados para poder medir SLA Courier sobre el histórico completo.
    cabecera = load.dedupe_cabecera(reporte, piso_fecha=piso, incluir_terminales=True)

    # Anulados: se excluyen del pipeline pero se cuentan para mostrar como nota en el dashboard.
    anulados_df = reporte[(reporte["estado"] == "Anulado") & (reporte["fecha_trx"] >= piso)] if piso is not None else reporte[reporte["estado"] == "Anulado"]
    anulados_df = anulados_df.drop_duplicates(subset=["orden_compra_norm", "envio_norm"])
    n_anulados = len(anulados_df)
    print(f"[load] {n_anulados} anulados excluidos del cálculo (se muestran como nota)")
    merged = load.merge_sources(cabecera, wms)
    merged = load.attach_sap_quiebres(merged)
    try:
        merged = fedex.enrich_dataframe(merged)
    except Exception as e:
        print(f"[FEDEX] Skip (error consultando API): {e}")
    try:
        bt_path = load.BASE / "AUTO_INPUTS" / "bigticket_dump.json"
        merged = bigticket.enrich_dataframe(merged, bt_path)
    except Exception as e:
        print(f"[BIGTICKET] Skip: {e}")
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
    dashboard.export_dashboard_json(resultado, hoy_str, json_path, anulados=n_anulados)
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
