"""Análisis puntual: eventos GA4 generados por tráfico de gopersonal.

No toca el pipeline existente ni ningún archivo automático — es un script
aparte para responder una pregunta puntual. Trae eventName x sessionSource
x sessionMedium desde la Data API de GA4 y filtra client-side las filas
cuyo source/medium pertenezca a gopersonal (no hay forma de filtrar por
substring directo en la API sin tocar ga4.run_report(), así que se trae
todo el reporte y se filtra acá).
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
import ga4

OUTPUT_DIR = Path(__file__).parent / "data" / "extraccion_completa"

GOPERSONAL_MARKERS = ("gopersonal",)


def _es_gopersonal(source: str) -> bool:
    s = (source or "").lower()
    return any(m in s for m in GOPERSONAL_MARKERS)


def main(dias=30):
    fin = date.today()
    inicio = fin - timedelta(days=dias)

    print(f"[GOPERSONAL] Consultando eventos GA4 {inicio} -> {fin}...")
    rows = ga4.run_report(
        inicio.isoformat(), fin.isoformat(),
        dimensions=["sessionSource", "sessionMedium", "eventName"],
        metrics=["eventCount", "totalUsers"],
        order_by="eventCount",
    )

    filas_gp = [r for r in rows if _es_gopersonal(r.get("sessionSource"))]
    print(f"[GOPERSONAL] {len(filas_gp)} filas (source/medium/evento) de {len(rows)} totales")

    # Resumen por evento (sumado entre todas las variantes de source: gopersonal,
    # admin.gopersonal.ai, discover.gopersonal.ai, etc.)
    por_evento = {}
    for r in filas_gp:
        ev = r["eventName"]
        d = por_evento.setdefault(ev, {"eventCount": 0, "totalUsers": 0})
        d["eventCount"] += int(r["eventCount"])
        d["totalUsers"] += int(r["totalUsers"])

    resumen = sorted(por_evento.items(), key=lambda kv: kv[1]["eventCount"], reverse=True)

    print("\n=== EVENTOS gopersonal (todas las fuentes/medios) ===")
    print(f"{'Evento':35s} | {'Count':>10s} | {'Usuarios':>10s}")
    for ev, d in resumen:
        print(f"{ev:35s} | {d['eventCount']:10,d} | {d['totalUsers']:10,d}")

    # Detalle por source/medium tambien, para ver de donde viene cada evento
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"ga4_eventos_gopersonal_{fin.isoformat()}.csv"
    import csv
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["sessionSource", "sessionMedium", "eventName", "eventCount", "totalUsers"])
        for r in sorted(filas_gp, key=lambda r: int(r["eventCount"]), reverse=True):
            w.writerow([r["sessionSource"], r["sessionMedium"], r["eventName"], r["eventCount"], r["totalUsers"]])

    print(f"\n[GOPERSONAL] Detalle guardado en {out_path}")


if __name__ == "__main__":
    main()
