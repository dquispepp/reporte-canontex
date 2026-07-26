"""Rutina diaria AUTOMATICA de pedidos atrasados.

Descarga sola las fuentes desde sus portales (OMSWeb + WMS), sin export manual,
y corre el mismo pipeline de cruce/Excel/dashboard que run_daily.py.

Rango: diciembre (01/12/2025) -> hoy. Canales ECOMMERCE + KIOSCO (filtro en load).
Requiere variables de entorno OMS_USER/OMS_PASS y WMS_USER/WMS_PASS, y estar en la
red de Cannon (el WMS es interno). Agendar con Task Scheduler (ver README).

    python run_daily_auto.py
"""
import os
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
import fetch
import load
import run_daily

# Desde cuando se reporta (diciembre a la fecha). Configurable para pruebas.
_desde_env = os.environ.get("AUTO_DESDE")
DESDE = datetime.strptime(_desde_env, "%Y-%m-%d").date() if _desde_env else date(2025, 12, 1)

# Carpeta compartida donde caen el Excel + dashboard (para que la vea el equipo).
SALIDA_DIR = Path(r"C:\Users\dquispe\OneDrive - Representaciones Canontex Ltda\Documentos\DOC DANI\Reporte Atraso Claude")


def main():
    hoy = datetime.now().date()
    hoy_str = hoy.strftime("%Y-%m-%d")

    auto_dir = load.BASE / "AUTO_INPUTS"
    auto_dir.mkdir(parents=True, exist_ok=True)
    for f in list(auto_dir.glob("*.csv")) + list(auto_dir.glob("DocumentoSalida*.xlsx")):
        f.unlink()

    wms_timeout = int(os.environ.get("WMS_TIMEOUT", "900"))
    print(f"[auto] Descargando fuentes {DESDE} -> {hoy} ...")
    fetch.fetch_reporteria_csv(DESDE, hoy, auto_dir / f"reporteria_{DESDE}_{hoy_str}.csv")
    fetch.fetch_wms_xlsx(DESDE, hoy, auto_dir / "DocumentoSalida_auto.xlsx", timeout=wms_timeout)

    # apuntar el pipeline existente a la carpeta con la data recien bajada
    load.REPORTE_DIR = auto_dir
    load.WMS_DIR = auto_dir

    # salidas (Excel + dashboard) a la carpeta compartida del equipo
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    load.OUTPUT_DIR = SALIDA_DIR

    run_daily.main()


if __name__ == "__main__":
    main()
