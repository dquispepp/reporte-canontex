"""Reporte de conversión GA4 + OMS: genera PDF y envía por correo.

Cruza sesiones/funnel de GA4 con pedidos reales de reportería OMS (canal Ecommerce).
Estructura:
  - Pag 1: Acumulado YTD (ene 1 hasta fin mes anterior) + KPIs mes en curso
  - Pag 2: Detalle diario del mes en curso + funnel

Programado: lunes y jueves 08:45.
"""
import os
import sys
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent / "src"))
import ga4
import fetch
import clarity
import json as _json
import subprocess

OUTPUT_DIR = Path(__file__).parent / "data" / "conversion"
DESTINATARIO = os.environ.get("CONVERSION_MAILTO", os.environ["MAIL_USER"])

MESES_ES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
             7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}


def _rangos():
    ayer = date.today() - timedelta(days=1)
    inicio_mes = ayer.replace(day=1)
    anio = ayer.year
    anio_ant = anio - 1

    # Mes en curso: día 1 del mes actual hasta ayer
    mes = {
        "actual_inicio": inicio_mes,
        "actual_fin": ayer,
        "anterior_inicio": inicio_mes.replace(year=anio_ant),
        "anterior_fin": ayer.replace(year=anio_ant),
    }

    # YTD: ene 1 hasta fin del mes anterior (meses cerrados)
    ytd = None
    if inicio_mes.month > 1:
        fin_mes_ant = inicio_mes - timedelta(days=1)
        ytd = {
            "actual_inicio": date(anio, 1, 1),
            "actual_fin": fin_mes_ant,
            "anterior_inicio": date(anio_ant, 1, 1),
            "anterior_fin": fin_mes_ant.replace(year=anio_ant),
        }

    return mes, ytd, anio, anio_ant


def _ga4_data(inicio, fin):
    rows = ga4.run_report(
        inicio.strftime("%Y-%m-%d"),
        fin.strftime("%Y-%m-%d"),
        dimensions=["date"],
        metrics=["sessions", "addToCarts", "checkouts", "ecommercePurchases", "totalRevenue"],
    )
    totals = {"sessions": 0, "addToCarts": 0, "checkouts": 0, "ecommercePurchases": 0, "totalRevenue": 0.0}
    daily = []
    for r in rows:
        d = {
            "date": r["date"],
            "sessions": int(r["sessions"]),
            "addToCarts": int(r["addToCarts"]),
            "checkouts": int(r["checkouts"]),
            "purchases": int(r["ecommercePurchases"]),
            "revenue": float(r["totalRevenue"]),
        }
        daily.append(d)
        for k in totals:
            if k == "totalRevenue":
                totals[k] += float(r[k])
            else:
                totals[k] += int(r[k])
    daily.sort(key=lambda x: x["date"])
    return totals, daily


CHUNK_MESES = 2

def _oms_pedidos(inicio, fin):
    import pandas as pd

    dias_total = (fin - inicio).days
    if dias_total > CHUNK_MESES * 31:
        dfs = []
        cursor = inicio
        while cursor <= fin:
            chunk_fin = min(cursor + timedelta(days=CHUNK_MESES * 30), fin)
            csv_chunk = OUTPUT_DIR / f"reporteria_{cursor}_{chunk_fin}.csv"
            print(f"  [OMS chunk] {cursor} -> {chunk_fin}")
            fetch.fetch_reporteria_csv(cursor, chunk_fin, csv_chunk)
            for enc in ("utf-8-sig", "latin-1"):
                try:
                    dfs.append(pd.read_csv(csv_chunk, dtype=str, encoding=enc, sep=";"))
                    break
                except Exception:
                    continue
            cursor = chunk_fin + timedelta(days=1)
        df = pd.concat(dfs, ignore_index=True)
    else:
        csv_path = OUTPUT_DIR / f"reporteria_{inicio}_{fin}.csv"
        fetch.fetch_reporteria_csv(inicio, fin, csv_path)
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(csv_path, dtype=str, encoding=enc, sep=";")
                break
            except Exception:
                continue

    col_canal = None
    for col in df.columns:
        if "canal" in col.lower() and "venta" in col.lower():
            col_canal = col
            break
    if not col_canal:
        for col in df.columns:
            if "canal" in col.lower():
                col_canal = col
                break

    if col_canal:
        ecom = df[df[col_canal].str.strip().str.upper() == "ECOMMERCE"]
    else:
        ecom = df

    col_envio = None
    for col in ecom.columns:
        if "envio" in col.lower() or "envío" in col.lower():
            col_envio = col
            break

    if col_envio:
        pedidos = ecom.drop_duplicates(subset=[col_envio])
    else:
        pedidos = ecom

    col_estado = None
    for col in pedidos.columns:
        if col.lower().rstrip() == "estado":
            col_estado = col
            break

    total = len(pedidos)
    entregados = 0
    anulados = 0
    if col_estado:
        entregados = len(pedidos[pedidos[col_estado].str.strip().str.lower() == "entregado"])
        anulados = len(pedidos[pedidos[col_estado].str.strip().str.lower() == "anulado"])

    return {
        "total_pedidos": total,
        "entregados": entregados,
        "anulados": anulados,
        "en_proceso": total - entregados - anulados,
    }


def _oms_diario_maps(rangos_mes):
    """Pedidos OMS reales por dia (YYYYMMDD -> cantidad), mes actual y anterior.
    Reutiliza los CSV de reporteria que _oms_pedidos() ya dejo cacheados en disco."""
    import pandas as pd

    def _diario_map(csv_path):
        if not csv_path.exists():
            return {}
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(csv_path, dtype=str, encoding=enc, sep=";")
                break
            except Exception:
                continue
        else:
            return {}
        col_canal = next((c for c in df.columns if "canal" in c.lower() and "venta" in c.lower()), None)
        col_envio = next((c for c in df.columns if "envío" in c.lower() or "envio" in c.lower()), None)
        col_fecha = next((c for c in df.columns if "fecha trx" in c.lower()), None)
        if not (col_canal and col_envio and col_fecha):
            return {}
        ecom = df[df[col_canal].str.strip().str.upper() == "ECOMMERCE"].drop_duplicates(subset=[col_envio]).copy()
        ecom["fecha_parsed"] = pd.to_datetime(ecom[col_fecha], format="%d/%m/%Y", errors="coerce")
        mapa = {}
        for fecha_dt, grupo in ecom.groupby("fecha_parsed"):
            if pd.notna(fecha_dt):
                mapa[fecha_dt.strftime("%Y%m%d")] = len(grupo)
        return mapa

    csv_actual = OUTPUT_DIR / f"reporteria_{rangos_mes['actual_inicio']}_{rangos_mes['actual_fin']}.csv"
    csv_anterior = OUTPUT_DIR / f"reporteria_{rangos_mes['anterior_inicio']}_{rangos_mes['anterior_fin']}.csv"
    return _diario_map(csv_actual), _diario_map(csv_anterior)


GOPERSONAL_MARKERS = ("gopersonal",)


def _es_gopersonal(source) -> bool:
    s = (source or "").lower()
    return any(m in s for m in GOPERSONAL_MARKERS)


def _gopersonal_data(rangos_mes):
    """Funnel diario + eventos del canal gopersonal (personalizacion/leads),
    filtrado client-side ya que la Data API de GA4 no soporta un filtro por
    substring de source dentro de ga4.run_report()."""
    inicio = rangos_mes["actual_inicio"].isoformat()
    fin = rangos_mes["actual_fin"].isoformat()

    rows = ga4.run_report(
        inicio, fin,
        dimensions=["date", "sessionSource", "sessionMedium"],
        metrics=["sessions", "addToCarts", "checkouts", "ecommercePurchases", "totalRevenue"],
    )
    diario = {}
    for r in rows:
        if not _es_gopersonal(r.get("sessionSource")):
            continue
        f = r["date"]
        d = diario.setdefault(f, {"sessions": 0, "addToCarts": 0, "checkouts": 0,
                                   "ecommercePurchases": 0, "totalRevenue": 0.0})
        d["sessions"] += int(r["sessions"])
        d["addToCarts"] += int(r["addToCarts"])
        d["checkouts"] += int(r["checkouts"])
        d["ecommercePurchases"] += int(r["ecommercePurchases"])
        d["totalRevenue"] += float(r["totalRevenue"])
    diario_list = [
        {"Fecha": f"{f[:4]}-{f[4:6]}-{f[6:]}", "Sesiones": v["sessions"],
         "Add to Cart": v["addToCarts"], "Checkouts": v["checkouts"],
         "Compras GA4": v["ecommercePurchases"], "Revenue GA4": round(v["totalRevenue"]),
         "Tasa Conversion": round(v["ecommercePurchases"] / v["sessions"] * 100, 2) if v["sessions"] else 0}
        for f, v in sorted(diario.items())
    ]

    ev_rows = ga4.run_report(
        inicio, fin,
        dimensions=["sessionSource", "sessionMedium", "eventName"],
        metrics=["eventCount", "totalUsers"],
    )
    eventos = {}
    for r in ev_rows:
        if not _es_gopersonal(r.get("sessionSource")):
            continue
        ev = r["eventName"]
        d = eventos.setdefault(ev, {"eventCount": 0, "totalUsers": 0})
        d["eventCount"] += int(r["eventCount"])
        d["totalUsers"] += int(r["totalUsers"])
    eventos_list = sorted(
        [{"Evento": ev, "Eventos": v["eventCount"], "Usuarios": v["totalUsers"]} for ev, v in eventos.items()],
        key=lambda x: x["Eventos"], reverse=True,
    )

    return diario_list, eventos_list


# ── PDF helpers ──────────────────────────────────────────────

def _var_pct(actual, anterior):
    if anterior == 0:
        return 0
    return (actual - anterior) / anterior * 100

def _fmt_var(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"

def _fmt_num(n):
    if n >= 1_000_000:
        return f"{n/1e6:.1f}M"
    if n >= 1_000:
        return f"{n/1e3:.1f}K"
    return f"{n:,}"


def _generar_pdf(mes_ga4, mes_ga4_ant, mes_oms, mes_oms_ant, mes_daily, mes_daily_ant,
                 ytd_ga4, ytd_ga4_ant, ytd_oms, ytd_oms_ant,
                 rangos_mes, rangos_ytd, anio, anio_ant, path,
                 clarity_funnel=None, clarity_friction=None,
                 oms_diario_map=None, oms_diario_ant_map=None):
    oms_diario_map = oms_diario_map or {}
    oms_diario_ant_map = oms_diario_ant_map or {}

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle

    W, H = letter
    c = canvas.Canvas(str(path), pagesize=letter)

    DARK_BLUE = HexColor('#1e3a5f')
    GREEN = HexColor('#008300')
    RED = HexColor('#c9190b')
    LIGHT_GRAY = HexColor('#f8f9fa')
    BORDER = HexColor('#e5e5e5')
    GRAY = HexColor('#666666')
    BLUE_C = HexColor('#2a78d6')
    ORANGE_C = HexColor('#eb6834')
    ORANGE_BG = HexColor('#fff8e1')
    ORANGE_BD = HexColor('#eda100')

    def vc(val, inv=False):
        if inv:
            return RED if val >= 0 else GREEN
        return GREEN if val >= 0 else RED

    def conv(oms_t, ga4_t):
        """Tasa de conversion real: pedidos OMS (reporteria) sobre sesiones GA4."""
        return oms_t["total_pedidos"] / ga4_t["sessions"] * 100 if ga4_t["sessions"] else 0

    def draw_kpi_row(c, y, kpis, kpi_w):
        for i, (label, value, delta, delta_color) in enumerate(kpis):
            x = 40 + i * (kpi_w + 10)
            c.setFillColor(LIGHT_GRAY)
            c.roundRect(x, y - 55, kpi_w, 58, 6, fill=1, stroke=0)
            c.setStrokeColor(BORDER)
            c.roundRect(x, y - 55, kpi_w, 58, 6, fill=0, stroke=1)
            c.setFillColor(GRAY)
            c.setFont('Helvetica', 7)
            c.drawCentredString(x + kpi_w / 2, y - 5, label)
            c.setFillColor(black)
            c.setFont('Helvetica-Bold', 17)
            c.drawCentredString(x + kpi_w / 2, y - 27, value)
            c.setFillColor(delta_color)
            c.setFont('Helvetica-Bold', 8)
            c.drawCentredString(x + kpi_w / 2, y - 43, delta)
        return y - 65

    def draw_table(c, y, data, col_widths, var_col_idx=5, bold_last=False):
        t = Table(data, colWidths=col_widths)
        style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('TEXTCOLOR', (0, 0), (-1, 0), GRAY),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        if bold_last:
            style.append(('FONTNAME', (0, len(data)-1), (-1, len(data)-1), 'Helvetica-Bold'))
        for row_idx in range(1, len(data)):
            val_str = data[row_idx][var_col_idx]
            if val_str.startswith('+'):
                style.append(('TEXTCOLOR', (var_col_idx, row_idx), (var_col_idx, row_idx), GREEN))
            elif val_str.startswith('-'):
                style.append(('TEXTCOLOR', (var_col_idx, row_idx), (var_col_idx, row_idx), RED))
            style.append(('FONTNAME', (var_col_idx, row_idx), (var_col_idx, row_idx), 'Helvetica-Bold'))
        t.setStyle(TableStyle(style))
        tw, th = t.wrap(0, 0)
        t.drawOn(c, 40, y - th)
        return y - th - 8

    mes_nombre = MESES_ES.get(rangos_mes["actual_inicio"].month, "")
    periodo_mes = f'{rangos_mes["actual_inicio"].strftime("%d/%m")} al {rangos_mes["actual_fin"].strftime("%d/%m")}'

    kpi_w = (W - 80 - 30) / 4

    # ═══════════════════ PAGINA 1 ═══════════════════
    y = H - 40

    # Header
    c.setFillColor(DARK_BLUE)
    c.roundRect(40, y - 50, W - 80, 55, 8, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 17)
    c.drawString(55, y - 20, f'Reporte Conversion — {mes_nombre} {anio}')
    c.setFont('Helvetica', 10)
    c.drawString(55, y - 36, f'GA4 + OMS Ecommerce | {periodo_mes} | vs {anio_ant}')

    y -= 75

    # ── ACUMULADO YTD ──
    if ytd_ga4 is not None:
        ytd_periodo = f'Ene - {MESES_ES.get(rangos_ytd["actual_fin"].month, "")}'

        c.setFillColor(DARK_BLUE)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40, y, f'Acumulado {anio} ({ytd_periodo})')
        c.setStrokeColor(BORDER)
        c.line(40, y - 4, W - 40, y - 4)
        y -= 18

        # GA4 YTD
        c.setFillColor(black)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(40, y, 'Google Analytics')
        y -= 8

        ytd_ses_v = _var_pct(ytd_ga4["sessions"], ytd_ga4_ant["sessions"])
        ytd_conv_a = conv(ytd_oms, ytd_ga4)
        ytd_conv_p = conv(ytd_oms_ant, ytd_ga4_ant)
        ytd_rev_v = _var_pct(ytd_ga4["totalRevenue"], ytd_ga4_ant["totalRevenue"])
        ytd_ped_v = _var_pct(ytd_oms["total_pedidos"], ytd_oms_ant["total_pedidos"])

        y = draw_kpi_row(c, y, [
            ('SESIONES', _fmt_num(ytd_ga4["sessions"]), _fmt_var(ytd_ses_v), vc(ytd_ses_v)),
            ('CONVERSION', f'{ytd_conv_a:.2f}%', f'vs {ytd_conv_p:.2f}%', vc(_var_pct(ytd_conv_a, ytd_conv_p))),
            ('REVENUE', f'${ytd_ga4["totalRevenue"]/1e6:.0f}M', _fmt_var(ytd_rev_v), vc(ytd_rev_v)),
            ('PEDIDOS OMS', f'{ytd_oms["total_pedidos"]:,}', _fmt_var(ytd_ped_v), vc(ytd_ped_v)),
        ], kpi_w)

        y -= 5

        # Funnel YTD
        def pct_s(v, s):
            return f'{v/s*100:.1f}%' if s else '-'

        ytd_funnel = [
            ['Etapa', str(anio_ant), '% ses.', str(anio), '% ses.', 'Var %'],
            ['Sesiones', f'{ytd_ga4_ant["sessions"]:,}', '100%', f'{ytd_ga4["sessions"]:,}', '100%', _fmt_var(ytd_ses_v)],
            ['Add to Cart', f'{ytd_ga4_ant["addToCarts"]:,}', pct_s(ytd_ga4_ant["addToCarts"], ytd_ga4_ant["sessions"]),
             f'{ytd_ga4["addToCarts"]:,}', pct_s(ytd_ga4["addToCarts"], ytd_ga4["sessions"]),
             _fmt_var(_var_pct(ytd_ga4["addToCarts"], ytd_ga4_ant["addToCarts"]))],
            ['Checkout', f'{ytd_ga4_ant["checkouts"]:,}', pct_s(ytd_ga4_ant["checkouts"], ytd_ga4_ant["sessions"]),
             f'{ytd_ga4["checkouts"]:,}', pct_s(ytd_ga4["checkouts"], ytd_ga4["sessions"]),
             _fmt_var(_var_pct(ytd_ga4["checkouts"], ytd_ga4_ant["checkouts"]))],
            ['Compra GA4', f'{ytd_ga4_ant["ecommercePurchases"]:,}', pct_s(ytd_ga4_ant["ecommercePurchases"], ytd_ga4_ant["sessions"]),
             f'{ytd_ga4["ecommercePurchases"]:,}', pct_s(ytd_ga4["ecommercePurchases"], ytd_ga4["sessions"]),
             _fmt_var(_var_pct(ytd_ga4["ecommercePurchases"], ytd_ga4_ant["ecommercePurchases"]))],
            ['Pedidos OMS', f'{ytd_oms_ant["total_pedidos"]:,}', '', f'{ytd_oms["total_pedidos"]:,}', '', _fmt_var(ytd_ped_v)],
        ]
        y = draw_table(c, y, ytd_funnel, [90, 75, 50, 75, 50, 60], bold_last=True)
        y -= 5

    # ── MES EN CURSO ──
    c.setFillColor(DARK_BLUE)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, f'{mes_nombre} {anio} ({periodo_mes})')
    c.setStrokeColor(BORDER)
    c.line(40, y - 4, W - 40, y - 4)
    y -= 18

    c.setFillColor(black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y, 'Google Analytics')
    y -= 8

    m_ses_v = _var_pct(mes_ga4["sessions"], mes_ga4_ant["sessions"])
    m_conv_a = conv(mes_oms, mes_ga4)
    m_conv_p = conv(mes_oms_ant, mes_ga4_ant)
    m_rev_v = _var_pct(mes_ga4["totalRevenue"], mes_ga4_ant["totalRevenue"])
    m_ped_v = _var_pct(mes_oms["total_pedidos"], mes_oms_ant["total_pedidos"])

    y = draw_kpi_row(c, y, [
        ('SESIONES', _fmt_num(mes_ga4["sessions"]), _fmt_var(m_ses_v), vc(m_ses_v)),
        ('CONVERSION', f'{m_conv_a:.2f}%', f'vs {m_conv_p:.2f}%', vc(_var_pct(m_conv_a, m_conv_p))),
        ('REVENUE', f'${mes_ga4["totalRevenue"]/1e6:.1f}M', _fmt_var(m_rev_v), vc(m_rev_v)),
        ('PEDIDOS OMS', f'{mes_oms["total_pedidos"]:,}', _fmt_var(m_ped_v), vc(m_ped_v)),
    ], kpi_w)

    y -= 5

    c.setFillColor(black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y, 'OMS Ecommerce')
    y -= 8

    ent_v = _var_pct(mes_oms["entregados"], mes_oms_ant["entregados"])
    proc_v = _var_pct(mes_oms["en_proceso"], mes_oms_ant["en_proceso"])
    anul_v = _var_pct(mes_oms["anulados"], mes_oms_ant["anulados"])

    y = draw_kpi_row(c, y, [
        ('PEDIDOS', f'{mes_oms["total_pedidos"]:,}', _fmt_var(m_ped_v), vc(m_ped_v)),
        ('ENTREGADOS', f'{mes_oms["entregados"]:,}', _fmt_var(ent_v), vc(ent_v)),
        ('EN PROCESO', f'{mes_oms["en_proceso"]:,}', _fmt_var(proc_v), vc(proc_v, inv=True)),
        ('ANULADOS', f'{mes_oms["anulados"]:,}', _fmt_var(anul_v), vc(anul_v, inv=True)),
    ], kpi_w)

    # Insight
    y -= 5
    checkout_v = _var_pct(mes_ga4["checkouts"], mes_ga4_ant["checkouts"])
    atc_v = _var_pct(mes_ga4["addToCarts"], mes_ga4_ant["addToCarts"])
    conv_diff = m_conv_a - m_conv_p

    c.setFillColor(ORANGE_BG)
    c.roundRect(40, y - 45, W - 80, 45, 6, fill=1, stroke=0)
    c.setStrokeColor(ORANGE_BD)
    c.setLineWidth(3)
    c.line(40, y - 45, 40, y)
    c.setLineWidth(1)
    c.setFillColor(HexColor('#5d4a00'))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(55, y - 14, f'{mes_nombre}: Sesiones {_fmt_var(m_ses_v)} | ATC {_fmt_var(atc_v)} | '
                 f'Checkout {_fmt_var(checkout_v)} | Pedidos OMS {_fmt_var(m_ped_v)}')
    c.setFont('Helvetica', 9)
    c.drawString(55, y - 30, f'Conversion: {m_conv_a:.2f}% ({"+" if conv_diff>=0 else ""}{conv_diff:.2f}pp vs {anio_ant}) | '
                 f'Revenue: ${mes_ga4["totalRevenue"]/1e6:.1f}M ({_fmt_var(m_rev_v)})')

    # Footer pag 1
    c.setFillColor(HexColor('#999999'))
    c.setFont('Helvetica', 7)
    c.drawString(40, 40, f'Fuente: GA4 Property {ga4.PROPERTY_ID} + OMS Reporteria Ecommerce | Generado {date.today().strftime("%Y-%m-%d")}')

    # ═══════════════════ PAGINA 2: Detalle diario ═══════════════════
    c.showPage()
    y = H - 40

    c.setFillColor(DARK_BLUE)
    c.roundRect(40, y - 40, W - 80, 45, 8, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 15)
    c.drawString(55, y - 18, f'Detalle diario — {mes_nombre} {anio}')
    c.setFont('Helvetica', 10)
    c.drawString(55, y - 33, f'Conversion por dia vs {anio_ant}')

    y -= 60

    # Legend
    c.setFillColor(BLUE_C)
    c.rect(40, y - 2, 10, 10, fill=1, stroke=0)
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 9)
    c.drawString(54, y, str(anio_ant))
    c.setFillColor(ORANGE_C)
    c.rect(110, y - 2, 10, 10, fill=1, stroke=0)
    c.setFillColor(GRAY)
    c.drawString(124, y, str(anio))
    y -= 18

    # Build daily lookup
    daily_ant_map = {}
    for d in mes_daily_ant:
        day_num = int(d["date"][6:8])
        daily_ant_map[day_num] = d

    daily_data = [['Dia', f'Ses {anio_ant}', f'Conv', f'Ses {anio}', f'Conv', 'Delta']]
    for d in mes_daily:
        day_num = int(d["date"][6:8])
        pedidos_oms_dia = oms_diario_map.get(d["date"], 0)
        c_a = pedidos_oms_dia / d["sessions"] * 100 if d["sessions"] else 0
        ant = daily_ant_map.get(day_num, {})
        s_ant = ant.get("sessions", 0)
        p_ant = oms_diario_ant_map.get(ant.get("date", ""), 0)
        c_p = p_ant / s_ant * 100 if s_ant else 0
        delta = _var_pct(c_a, c_p) if c_p else 0
        daily_data.append([
            f'{day_num}',
            f'{s_ant:,}' if s_ant else '-',
            f'{c_p:.2f}%' if s_ant else '-',
            f'{d["sessions"]:,}',
            f'{c_a:.2f}%',
            _fmt_var(delta) if c_p else '-',
        ])

    col_w = [35, 75, 55, 75, 55, 60]
    y = draw_table(c, y, daily_data, col_w)

    # Funnel del mes
    y -= 10
    c.setFillColor(black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, f'Funnel {mes_nombre}')
    y -= 15

    def pct_s(v, s):
        return f'{v/s*100:.1f}%' if s else '-'

    funnel_data = [
        ['Etapa', str(anio_ant), '% ses.', str(anio), '% ses.', 'Var %'],
        ['Sesiones', f'{mes_ga4_ant["sessions"]:,}', '100%', f'{mes_ga4["sessions"]:,}', '100%', _fmt_var(m_ses_v)],
        ['Add to Cart', f'{mes_ga4_ant["addToCarts"]:,}', pct_s(mes_ga4_ant["addToCarts"], mes_ga4_ant["sessions"]),
         f'{mes_ga4["addToCarts"]:,}', pct_s(mes_ga4["addToCarts"], mes_ga4["sessions"]),
         _fmt_var(_var_pct(mes_ga4["addToCarts"], mes_ga4_ant["addToCarts"]))],
        ['Checkout', f'{mes_ga4_ant["checkouts"]:,}', pct_s(mes_ga4_ant["checkouts"], mes_ga4_ant["sessions"]),
         f'{mes_ga4["checkouts"]:,}', pct_s(mes_ga4["checkouts"], mes_ga4["sessions"]),
         _fmt_var(_var_pct(mes_ga4["checkouts"], mes_ga4_ant["checkouts"]))],
        ['Compra GA4', f'{mes_ga4_ant["ecommercePurchases"]:,}', pct_s(mes_ga4_ant["ecommercePurchases"], mes_ga4_ant["sessions"]),
         f'{mes_ga4["ecommercePurchases"]:,}', pct_s(mes_ga4["ecommercePurchases"], mes_ga4["sessions"]),
         _fmt_var(_var_pct(mes_ga4["ecommercePurchases"], mes_ga4_ant["ecommercePurchases"]))],
        ['Pedidos OMS', f'{mes_oms_ant["total_pedidos"]:,}', '', f'{mes_oms["total_pedidos"]:,}', '', _fmt_var(m_ped_v)],
    ]
    y = draw_table(c, y, funnel_data, [90, 75, 50, 75, 50, 60], bold_last=True)

    # Footer pag 2
    c.setFillColor(HexColor('#999999'))
    c.setFont('Helvetica', 7)
    c.drawString(40, 40, f'Fuente: GA4 Property {ga4.PROPERTY_ID} + OMS Reporteria Ecommerce | Generado {date.today().strftime("%Y-%m-%d")}')

    # ═══════════════════ PAGINA 3: Clarity UX ═══════════════════
    if clarity_funnel:
        c.showPage()
        y = H - 40

        PURPLE = HexColor('#6a1b9a')
        PURPLE_LIGHT = HexColor('#f3e5f5')

        c.setFillColor(PURPLE)
        c.roundRect(40, y - 40, W - 80, 45, 8, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 15)
        c.drawString(55, y - 18, 'Analisis UX — Microsoft Clarity')
        c.setFont('Helvetica', 10)
        c.drawString(55, y - 33, f'Friccion por etapa del funnel | Ultimos 3 dias')

        y -= 65

        c.setFillColor(black)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, 'Metricas de friccion por etapa')
        y -= 15

        clarity_table = [['Etapa', 'Sesiones', 'Rage Click', 'Dead Click', 'Quickback', 'Scroll', 'T. Activo']]
        for stage in clarity.FUNNEL_ORDER:
            d = clarity_funnel.get(stage, {})
            if d.get("sessions", 0) == 0 and stage == "Confirmacion":
                continue
            clarity_table.append([
                stage,
                f'{d.get("sessions", 0):,}',
                f'{d.get("rage_pct", 0):.1f}%',
                f'{d.get("dead_pct", 0):.1f}%',
                f'{d.get("quickback_pct", 0):.1f}%',
                f'{d.get("scroll_depth", 0):.0f}%',
                f'{d.get("active_time_s", 0):.0f}s',
            ])

        ct = Table(clarity_table, colWidths=[85, 60, 65, 65, 65, 55, 60])
        ct_style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('TEXTCOLOR', (0, 0), (-1, 0), GRAY),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, PURPLE_LIGHT]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        for ri in range(1, len(clarity_table)):
            row = clarity_table[ri]
            rage_val = float(row[2].replace('%', ''))
            dead_val = float(row[3].replace('%', ''))
            qb_val = float(row[4].replace('%', ''))
            scroll_val = float(row[5].replace('%', ''))
            if rage_val >= 5:
                ct_style.append(('TEXTCOLOR', (2, ri), (2, ri), RED))
                ct_style.append(('FONTNAME', (2, ri), (2, ri), 'Helvetica-Bold'))
            if dead_val >= 10:
                ct_style.append(('TEXTCOLOR', (3, ri), (3, ri), RED))
                ct_style.append(('FONTNAME', (3, ri), (3, ri), 'Helvetica-Bold'))
            if qb_val >= 20:
                ct_style.append(('TEXTCOLOR', (4, ri), (4, ri), RED))
                ct_style.append(('FONTNAME', (4, ri), (4, ri), 'Helvetica-Bold'))
            if scroll_val <= 30:
                ct_style.append(('TEXTCOLOR', (5, ri), (5, ri), RED))
                ct_style.append(('FONTNAME', (5, ri), (5, ri), 'Helvetica-Bold'))

        ct.setStyle(TableStyle(ct_style))
        tw, th = ct.wrap(0, 0)
        ct.drawOn(c, 40, y - th)
        y -= th + 20

        # Top friction pages
        if clarity_friction:
            c.setFillColor(black)
            c.setFont('Helvetica-Bold', 11)
            c.drawString(40, y, 'Top paginas con mayor friccion')
            y -= 15

            fp_data = [['Pagina', 'Etapa', 'Ses.', 'Rage%', 'Dead%', 'QB%', 'Scroll%', 'Score']]
            for p in clarity_friction[:10]:
                url_short = p["url"]
                if len(url_short) > 35:
                    url_short = url_short[:32] + "..."
                fp_data.append([
                    url_short,
                    p.get("stage", ""),
                    str(p.get("sessions", 0)),
                    f'{p.get("rage", 0):.0f}',
                    f'{p.get("dead", 0):.0f}',
                    f'{p.get("quickback", 0):.0f}',
                    f'{p.get("scroll", 0):.0f}',
                    f'{p.get("friction_score", 0):.0f}',
                ])

            fp_t = Table(fp_data, colWidths=[140, 65, 35, 40, 40, 35, 45, 40])
            fp_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR', (0, 0), (-1, 0), GRAY),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]
            for ri in range(1, len(fp_data)):
                score = float(fp_data[ri][-1])
                if score >= 300:
                    fp_style.append(('TEXTCOLOR', (-1, ri), (-1, ri), RED))
                    fp_style.append(('FONTNAME', (-1, ri), (-1, ri), 'Helvetica-Bold'))
                elif score >= 100:
                    fp_style.append(('TEXTCOLOR', (-1, ri), (-1, ri), ORANGE_C))
                    fp_style.append(('FONTNAME', (-1, ri), (-1, ri), 'Helvetica-Bold'))
            fp_t.setStyle(TableStyle(fp_style))
            fw, fh = fp_t.wrap(0, 0)
            fp_t.drawOn(c, 40, y - fh)
            y -= fh + 20

        # Insight box
        insights = []
        home = clarity_funnel.get("Home", {})
        cat = clarity_funnel.get("Categoria", {})
        checkout = clarity_funnel.get("Checkout", {})

        if home.get("scroll_depth", 100) < 30:
            insights.append(f'Home: scroll {home["scroll_depth"]:.0f}% — usuarios no ven el contenido bajo el fold')
        if cat.get("quickback_pct", 0) >= 20:
            insights.append(f'Categoria: {cat["quickback_pct"]:.0f}% quickback — usuarios rebotan rapidamente')
        if checkout.get("dead_pct", 0) >= 10:
            insights.append(f'Checkout: {checkout["dead_pct"]:.0f}% dead clicks — problemas de interaccion en formulario')
        if home.get("quickback_pct", 0) >= 15:
            insights.append(f'Home: {home["quickback_pct"]:.0f}% quickback — landing no engancha')

        if insights:
            box_h = 15 + len(insights) * 14
            c.setFillColor(PURPLE_LIGHT)
            c.roundRect(40, y - box_h, W - 80, box_h, 6, fill=1, stroke=0)
            c.setStrokeColor(PURPLE)
            c.setLineWidth(3)
            c.line(40, y - box_h, 40, y)
            c.setLineWidth(1)
            c.setFillColor(PURPLE)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(55, y - 12, 'Diagnostico UX (Clarity)')
            c.setFont('Helvetica', 8)
            c.setFillColor(HexColor('#4a0072'))
            for i, txt in enumerate(insights):
                c.drawString(55, y - 26 - i * 14, f'• {txt}')

        # Footer pag 3
        c.setFillColor(HexColor('#999999'))
        c.setFont('Helvetica', 7)
        c.drawString(40, 40, f'Fuente: Microsoft Clarity (Project o8vc0cwjrq) | Generado {date.today().strftime("%Y-%m-%d")}')

    c.save()
    print(f"[CONVERSION] PDF generado: {path.name}")
    return path


def _sync_cro(mes_ga4, mes_ga4_ant, mes_daily, mes_daily_ant, mes_oms,
               rangos_mes, anio, anio_ant, clarity_funnel, clarity_friction,
               mes_oms_ant=None, gopersonal_diario=None, gopersonal_eventos=None):
    """Genera CSVs para el proyecto CRO y hace commit+push al repo."""
    import pandas as pd

    cro_dir = Path(__file__).parent / "data" / "clarity"
    cro_dir.mkdir(parents=True, exist_ok=True)

    # Helper: cargar reportería OMS y extraer ecommerce con columnas detectadas
    def _load_oms_ecom(csv_path):
        if not csv_path.exists():
            return None, {}
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(csv_path, dtype=str, encoding=enc, sep=";")
                break
            except Exception:
                continue
        else:
            return None, {}
        cols = {
            "canal": [c for c in df.columns if "canal" in c.lower() and "venta" in c.lower()][0],
            "envio": [c for c in df.columns if "envío" in c.lower() or "envio" in c.lower()][0],
            "estado": [c for c in df.columns if c.lower().strip() == "estado"][0],
            "fecha": [c for c in df.columns if "fecha trx" in c.lower()][0],
            "despacho": [c for c in df.columns if "tipo" in c.lower() and "despacho" in c.lower()][0],
        }
        ecom_df = df[df[cols["canal"]].str.strip().str.upper() == "ECOMMERCE"].drop_duplicates(subset=[cols["envio"]]).copy()
        ecom_df["fecha_parsed"] = pd.to_datetime(ecom_df[cols["fecha"]], format="%d/%m/%Y", errors="coerce")
        return ecom_df, cols

    # Cargar OMS mes actual y anterior
    csv_oms_path = OUTPUT_DIR / f"reporteria_{rangos_mes['actual_inicio']}_{rangos_mes['actual_fin']}.csv"
    csv_oms_ant_path = OUTPUT_DIR / f"reporteria_{rangos_mes['anterior_inicio']}_{rangos_mes['anterior_fin']}.csv"
    ecom, oms_cols = _load_oms_ecom(csv_oms_path)
    ecom_ant, _ = _load_oms_ecom(csv_oms_ant_path)

    # Mapa diario OMS: fecha YYYYMMDD -> n pedidos
    oms_diario_map = {}
    if ecom is not None:
        for fecha_dt, grupo in ecom.groupby("fecha_parsed"):
            if pd.notna(fecha_dt):
                oms_diario_map[fecha_dt.strftime("%Y%m%d")] = len(grupo)
    oms_diario_ant_map = {}
    if ecom_ant is not None:
        for fecha_dt, grupo in ecom_ant.groupby("fecha_parsed"):
            if pd.notna(fecha_dt):
                oms_diario_ant_map[fecha_dt.strftime("%Y%m%d")] = len(grupo)

    col_estado = oms_cols.get("estado")
    col_despacho = oms_cols.get("despacho")

    # 1. ventas_resumen.csv — diario cruzado GA4 + OMS
    if ecom is not None:
        ga4_map = {d["date"]: d for d in mes_daily}
        ventas = []
        for fecha_dt, grupo in ecom.groupby("fecha_parsed"):
            if pd.isna(fecha_dt):
                continue
            f = fecha_dt.strftime("%Y-%m-%d")
            f_key = fecha_dt.strftime("%Y%m%d")
            total = len(grupo)
            entregados = len(grupo[grupo[col_estado].str.strip().str.lower() == "entregado"])
            anulados = len(grupo[grupo[col_estado].str.strip().str.lower() == "anulado"])
            g = ga4_map.get(f_key, {})
            ses = g.get("sessions", 0)
            ventas.append({
                "Fecha": f,
                "Sesiones GA4": ses,
                "Add to Cart": g.get("addToCarts", 0),
                "Checkouts": g.get("checkouts", 0),
                "Pedidos OMS": total,
                "Revenue GA4": round(g.get("revenue", 0)),
                "Tasa Conversion": round(total / ses * 100, 2) if ses else 0,
                "Entregados": entregados,
                "Anulados": anulados,
                "En Proceso": total - entregados - anulados,
                "Despacho Domicilio": len(grupo[grupo[col_despacho].str.strip().str.lower() == "despacho a domicilio"]),
                "Retiro Tienda": len(grupo[grupo[col_despacho].str.strip().str.lower() == "retiro en tienda"]),
            })
        pd.DataFrame(ventas).sort_values("Fecha").to_csv(cro_dir / "ventas_resumen.csv", index=False, encoding="utf-8-sig")

    # 2. ga4_funnel.csv
    def pct(v, s):
        return round(v / s * 100, 2) if s else 0
    def var(a, b):
        return round((a - b) / b * 100, 1) if b else 0

    mes_nombre = MESES_ES.get(rangos_mes["actual_inicio"].month, "")
    oms_total = mes_oms["total_pedidos"]
    oms_ant_total = mes_oms_ant["total_pedidos"] if mes_oms_ant else 0
    funnel = [
        {"Etapa": "Sesiones", f"{mes_nombre} {anio_ant}": mes_ga4_ant["sessions"], f"{mes_nombre} {anio}": mes_ga4["sessions"],
         f"% {anio_ant}": "100%", f"% {anio}": "100%", "Var %": var(mes_ga4["sessions"], mes_ga4_ant["sessions"])},
        {"Etapa": "Add to Cart", f"{mes_nombre} {anio_ant}": mes_ga4_ant["addToCarts"], f"{mes_nombre} {anio}": mes_ga4["addToCarts"],
         f"% {anio_ant}": f'{pct(mes_ga4_ant["addToCarts"], mes_ga4_ant["sessions"])}%', f"% {anio}": f'{pct(mes_ga4["addToCarts"], mes_ga4["sessions"])}%',
         "Var %": var(mes_ga4["addToCarts"], mes_ga4_ant["addToCarts"])},
        {"Etapa": "Checkout", f"{mes_nombre} {anio_ant}": mes_ga4_ant["checkouts"], f"{mes_nombre} {anio}": mes_ga4["checkouts"],
         f"% {anio_ant}": f'{pct(mes_ga4_ant["checkouts"], mes_ga4_ant["sessions"])}%', f"% {anio}": f'{pct(mes_ga4["checkouts"], mes_ga4["sessions"])}%',
         "Var %": var(mes_ga4["checkouts"], mes_ga4_ant["checkouts"])},
        {"Etapa": "Pedidos OMS", f"{mes_nombre} {anio_ant}": oms_ant_total, f"{mes_nombre} {anio}": oms_total,
         f"% {anio_ant}": f'{pct(oms_ant_total, mes_ga4_ant["sessions"])}%', f"% {anio}": f'{pct(oms_total, mes_ga4["sessions"])}%',
         "Var %": var(oms_total, oms_ant_total) if oms_ant_total else 0},
        {"Etapa": "Revenue GA4", f"{mes_nombre} {anio_ant}": round(mes_ga4_ant["totalRevenue"]), f"{mes_nombre} {anio}": round(mes_ga4["totalRevenue"]),
         f"% {anio_ant}": "", f"% {anio}": "", "Var %": var(mes_ga4["totalRevenue"], mes_ga4_ant["totalRevenue"])},
    ]
    pd.DataFrame(funnel).to_csv(cro_dir / "ga4_funnel.csv", index=False, encoding="utf-8-sig")

    # 3. ventas_abandono_carrito.csv (compras = pedidos OMS reales)
    abandono = []
    for label, daily, oms_map in [
        (str(anio_ant), mes_daily_ant, oms_diario_ant_map),
        (str(anio), mes_daily, oms_diario_map),
    ]:
        for d in daily:
            ses, atc, chk = d["sessions"], d["addToCarts"], d["checkouts"]
            pedidos = oms_map.get(d["date"], 0)
            abandono.append({
                "Fecha": f'{d["date"][:4]}-{d["date"][4:6]}-{d["date"][6:]}',
                "Periodo": label,
                "Sesiones": ses, "ATC": atc,
                "Drop Sesion>ATC": ses - atc,
                "% Abandono Sesion>ATC": round((ses - atc) / ses * 100, 1) if ses else 0,
                "Checkout": chk,
                "Drop ATC>Checkout": atc - chk,
                "% Abandono ATC>Checkout": round((atc - chk) / atc * 100, 1) if atc else 0,
                "Pedidos OMS": pedidos,
                "Drop Checkout>Compra": chk - pedidos,
                "% Abandono Checkout>Compra": round((chk - pedidos) / chk * 100, 1) if chk else 0,
            })
    pd.DataFrame(abandono).sort_values(["Periodo", "Fecha"]).to_csv(cro_dir / "ventas_abandono_carrito.csv", index=False, encoding="utf-8-sig")

    # 4. ga4_conversion_diario.csv — serie diaria con pedidos OMS reales
    ga4_conv = []
    for label, daily, yr, oms_map in [
        (str(anio_ant), mes_daily_ant, anio_ant, oms_diario_ant_map),
        (str(anio), mes_daily, anio, oms_diario_map),
    ]:
        for d in daily:
            ses, atc, chk, rev = d["sessions"], d["addToCarts"], d["checkouts"], d["revenue"]
            pedidos_oms = oms_map.get(d["date"], 0)
            ga4_conv.append({
                "Fecha": f'{d["date"][:4]}-{d["date"][4:6]}-{d["date"][6:]}',
                "Anio": yr,
                "Sesiones": ses, "Add to Cart": atc, "Checkouts": chk,
                "Pedidos OMS": pedidos_oms, "Revenue GA4": round(rev),
                "Tasa ATC": round(atc / ses * 100, 2) if ses else 0,
                "Tasa Checkout": round(chk / ses * 100, 2) if ses else 0,
                "Tasa Conversion": round(pedidos_oms / ses * 100, 2) if ses else 0,
            })
    pd.DataFrame(ga4_conv).sort_values(["Anio", "Fecha"]).to_csv(
        cro_dir / "ga4_conversion_diario.csv", index=False, encoding="utf-8-sig")

    # 5. funnel_mensual.csv — comparativo mes actual vs anterior (pedidos OMS reales)
    oms_t = mes_oms["total_pedidos"]
    oms_at = mes_oms_ant["total_pedidos"] if mes_oms_ant else 0
    ses_t = mes_ga4["sessions"]
    ses_at = mes_ga4_ant["sessions"]
    funnel_m = [
        {"Metrica": "Sesiones", f"{mes_nombre} {anio_ant}": ses_at,
         f"{mes_nombre} {anio}": ses_t,
         "Var %": var(ses_t, ses_at) if ses_at else 0},
        {"Metrica": "Add to Cart", f"{mes_nombre} {anio_ant}": mes_ga4_ant["addToCarts"],
         f"{mes_nombre} {anio}": mes_ga4["addToCarts"],
         "Var %": var(mes_ga4["addToCarts"], mes_ga4_ant["addToCarts"]) if mes_ga4_ant["addToCarts"] else 0},
        {"Metrica": "Checkout", f"{mes_nombre} {anio_ant}": mes_ga4_ant["checkouts"],
         f"{mes_nombre} {anio}": mes_ga4["checkouts"],
         "Var %": var(mes_ga4["checkouts"], mes_ga4_ant["checkouts"]) if mes_ga4_ant["checkouts"] else 0},
        {"Metrica": "Pedidos OMS Ecommerce", f"{mes_nombre} {anio_ant}": oms_at,
         f"{mes_nombre} {anio}": oms_t,
         "Var %": var(oms_t, oms_at) if oms_at else 0},
        {"Metrica": "Revenue GA4", f"{mes_nombre} {anio_ant}": round(mes_ga4_ant["totalRevenue"]),
         f"{mes_nombre} {anio}": round(mes_ga4["totalRevenue"]),
         "Var %": var(mes_ga4["totalRevenue"], mes_ga4_ant["totalRevenue"]) if mes_ga4_ant["totalRevenue"] else 0},
        {"Metrica": "Tasa Conversion", f"{mes_nombre} {anio_ant}": round(oms_at / ses_at * 100, 2) if ses_at else 0,
         f"{mes_nombre} {anio}": round(oms_t / ses_t * 100, 2) if ses_t else 0,
         "Var %": ""},
    ]
    pd.DataFrame(funnel_m).to_csv(cro_dir / "funnel_mensual.csv", index=False, encoding="utf-8-sig")

    # 6. oms_pedidos_diario.csv — desglose diario OMS
    if csv_oms_path.exists():
        oms_daily = []
        for fecha_dt, grupo in ecom.groupby("fecha_parsed"):
            if pd.isna(fecha_dt):
                continue
            total = len(grupo)
            entregados = len(grupo[grupo[col_estado].str.strip().str.lower() == "entregado"])
            anulados_g = len(grupo[grupo[col_estado].str.strip().str.lower() == "anulado"])
            oms_daily.append({
                "Fecha": fecha_dt.strftime("%Y-%m-%d"),
                "Pedidos Total": total,
                "Entregados": entregados,
                "Anulados": anulados_g,
                "En Proceso": total - entregados - anulados_g,
                "Despacho Domicilio": len(grupo[grupo[col_despacho].str.strip().str.lower() == "despacho a domicilio"]),
                "Retiro Tienda": len(grupo[grupo[col_despacho].str.strip().str.lower() == "retiro en tienda"]),
            })
        pd.DataFrame(oms_daily).sort_values("Fecha").to_csv(
            cro_dir / "oms_pedidos_diario.csv", index=False, encoding="utf-8-sig")

    # 7. Clarity CSVs (ya se guardan via clarity.guardar_snapshot)
    if clarity_funnel:
        df_cf = pd.DataFrame([{"Etapa": k, **v} for k, v in clarity_funnel.items()])
        df_cf.columns = ["Etapa", "Rage%", "Dead%", "Quickback%", "Scroll%", "Tiempo Activo (s)", "Sesiones"]
        df_cf.to_csv(cro_dir / "clarity_funnel.csv", index=False, encoding="utf-8-sig")

    if clarity_friction:
        df_fp = pd.DataFrame(clarity_friction)
        df_fp = df_fp[["url", "stage", "sessions", "rage", "dead", "quickback", "scroll", "friction_score"]]
        df_fp.columns = ["Pagina", "Etapa", "Sesiones", "Rage%", "Dead%", "Quickback%", "Scroll%", "Score Friccion"]
        df_fp.to_csv(cro_dir / "clarity_paginas.csv", index=False, encoding="utf-8-sig")

    # 8. gopersonal_diario.csv + gopersonal_eventos.csv
    if gopersonal_diario:
        pd.DataFrame(gopersonal_diario).to_csv(cro_dir / "gopersonal_diario.csv", index=False, encoding="utf-8-sig")
    if gopersonal_eventos:
        pd.DataFrame(gopersonal_eventos).to_csv(cro_dir / "gopersonal_eventos.csv", index=False, encoding="utf-8-sig")

    # 10. _meta_actualizacion.json
    meta = {
        "last_updated": date.today().isoformat(),
        "period_main": f"{rangos_mes['actual_inicio']} a {rangos_mes['actual_fin']}",
        "period_comparison": f"{rangos_mes['anterior_inicio']} a {rangos_mes['anterior_fin']}",
        "fuente_ga4": f"GA4 Property {ga4.PROPERTY_ID}",
        "fuente_oms": "OMS Reporteria canal Ecommerce",
        "fuente_clarity": "Microsoft Clarity Project o8vc0cwjrq",
        "sitio": "cannonhome.cl",
        "archivos": {
            "ventas_resumen.csv": "Venta diaria cruzada GA4 + OMS",
            "ga4_funnel.csv": "Funnel consolidado mes actual vs anterior",
            "ventas_abandono_carrito.csv": "Abandono por etapa del funnel diario",
            "clarity_funnel.csv": "Friccion UX por etapa",
            "clarity_paginas.csv": "Top paginas con mayor friccion",
            "clarity_historial.json": "Historial diario acumulado Clarity",
            "ga4_conversion_diario.csv": "Serie diaria GA4 con tasas por etapa",
            "funnel_mensual.csv": "Funnel comparativo mes actual vs anterior",
            "oms_pedidos_diario.csv": "Pedidos OMS diarios por estado y tipo despacho",
            "gopersonal_diario.csv": "Funnel diario del canal gopersonal (personalizacion/leads)",
            "gopersonal_eventos.csv": "Eventos GA4 del canal gopersonal, mes en curso",
        }
    }
    with open(cro_dir / "_meta_actualizacion.json", "w", encoding="utf-8") as f:
        _json.dump(meta, f, indent=2, ensure_ascii=False)

    # 6. Git commit + push
    repo_dir = str(Path(__file__).parent)
    try:
        subprocess.run(["git", "add", "data/clarity/"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"[AUTO] Sync CRO data {date.today()}"],
                       cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=repo_dir, check=True, capture_output=True)
        print("[CONVERSION] CRO sync: commit + push OK")
    except subprocess.CalledProcessError as e:
        print(f"[CONVERSION] CRO sync git: {e.stderr.decode()[:200] if e.stderr else 'sin cambios'}")


def _enviar_email(pdf_path, rangos_mes, anio):
    host = os.environ["MAIL_HOST"]
    user = os.environ["MAIL_USER"]
    pwd = os.environ["MAIL_PASS"]

    mes_nombre = MESES_ES.get(rangos_mes["actual_inicio"].month, "")
    periodo = f'{rangos_mes["actual_inicio"].strftime("%d/%m")} al {rangos_mes["actual_fin"].strftime("%d/%m")}'

    msg = MIMEMultipart()
    msg["Subject"] = f"Reporte Conversion {mes_nombre} {anio} ({periodo})"
    msg["From"] = user
    msg["To"] = DESTINATARIO

    body = (f"Adjunto reporte de conversion GA4 + OMS para {mes_nombre} {anio}.\n"
            f"Periodo mes: {periodo} | Acumulado YTD: Ene-{MESES_ES.get(rangos_mes['actual_inicio'].month - 1, 'Dic')}\n"
            f"Comparado vs mismo periodo {anio - 1}.\n\n"
            f"Generado automaticamente.")
    msg.attach(MIMEText(body, "plain"))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={pdf_path.name}")
        msg.attach(part)

    with smtplib.SMTP(host, 587) as s:
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, [DESTINATARIO], msg.as_string())
    print(f"[CONVERSION] Email enviado a {DESTINATARIO}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rangos_mes, rangos_ytd, anio, anio_ant = _rangos()

    print(f"[CONVERSION] Mes: {rangos_mes['actual_inicio']} -> {rangos_mes['actual_fin']}")
    if rangos_ytd:
        print(f"[CONVERSION] YTD: {rangos_ytd['actual_inicio']} -> {rangos_ytd['actual_fin']}")

    # ── GA4 mes en curso ──
    print("[CONVERSION] GA4 mes actual...")
    mes_ga4, mes_daily = _ga4_data(rangos_mes["actual_inicio"], rangos_mes["actual_fin"])
    print(f"[CONVERSION] GA4 mes: {mes_ga4['sessions']:,} sesiones, {mes_ga4['ecommercePurchases']:,} compras")

    print("[CONVERSION] GA4 mes anterior...")
    mes_ga4_ant, mes_daily_ant = _ga4_data(rangos_mes["anterior_inicio"], rangos_mes["anterior_fin"])

    # ── OMS mes en curso ──
    print("[CONVERSION] OMS mes actual...")
    mes_oms = _oms_pedidos(rangos_mes["actual_inicio"], rangos_mes["actual_fin"])
    print(f"[CONVERSION] OMS mes: {mes_oms['total_pedidos']:,} pedidos Ecommerce")

    print("[CONVERSION] OMS mes anterior...")
    mes_oms_ant = _oms_pedidos(rangos_mes["anterior_inicio"], rangos_mes["anterior_fin"])

    oms_diario_map, oms_diario_ant_map = _oms_diario_maps(rangos_mes)

    # ── YTD (si no es enero) ──
    ytd_ga4 = ytd_ga4_ant = ytd_oms = ytd_oms_ant = None
    if rangos_ytd:
        print("[CONVERSION] GA4 YTD actual...")
        ytd_ga4, _ = _ga4_data(rangos_ytd["actual_inicio"], rangos_ytd["actual_fin"])
        print(f"[CONVERSION] GA4 YTD: {ytd_ga4['sessions']:,} sesiones")

        print("[CONVERSION] GA4 YTD anterior...")
        ytd_ga4_ant, _ = _ga4_data(rangos_ytd["anterior_inicio"], rangos_ytd["anterior_fin"])

        print("[CONVERSION] OMS YTD actual...")
        ytd_oms = _oms_pedidos(rangos_ytd["actual_inicio"], rangos_ytd["actual_fin"])
        print(f"[CONVERSION] OMS YTD: {ytd_oms['total_pedidos']:,} pedidos")

        print("[CONVERSION] OMS YTD anterior...")
        ytd_oms_ant = _oms_pedidos(rangos_ytd["anterior_inicio"], rangos_ytd["anterior_fin"])

    # ── Clarity UX ──
    clarity_funnel = None
    clarity_friction = None
    try:
        print("[CONVERSION] Clarity UX data...")
        clarity_funnel = clarity.get_funnel_metrics(3)
        clarity_friction = clarity.get_top_friction_pages(3, top_n=10)
        clarity.guardar_snapshot(1)
        print(f"[CONVERSION] Clarity: {len(clarity_funnel)} etapas, {len(clarity_friction)} pages friction, snapshot guardado")
    except Exception as e:
        print(f"[CONVERSION] Clarity error (continuando sin UX): {e}")

    pdf_name = f"conversion_{rangos_mes['actual_fin'].strftime('%Y-%m-%d')}.pdf"
    pdf_path = OUTPUT_DIR / pdf_name
    _generar_pdf(mes_ga4, mes_ga4_ant, mes_oms, mes_oms_ant, mes_daily, mes_daily_ant,
                 ytd_ga4, ytd_ga4_ant, ytd_oms, ytd_oms_ant,
                 rangos_mes, rangos_ytd, anio, anio_ant, pdf_path,
                 clarity_funnel, clarity_friction,
                 oms_diario_map, oms_diario_ant_map)
    _enviar_email(pdf_path, rangos_mes, anio)

    # ── gopersonal ──
    gopersonal_diario = gopersonal_eventos = None
    try:
        print("[CONVERSION] gopersonal...")
        gopersonal_diario, gopersonal_eventos = _gopersonal_data(rangos_mes)
        print(f"[CONVERSION] gopersonal: {len(gopersonal_diario)} dias, {len(gopersonal_eventos)} tipos de evento")
    except Exception as e:
        print(f"[CONVERSION] gopersonal error (no bloqueante): {e}")

    # ── Sync datos para proyecto CRO ──
    try:
        print("[CONVERSION] Sync CRO...")
        _sync_cro(mes_ga4, mes_ga4_ant, mes_daily, mes_daily_ant, mes_oms,
                  rangos_mes, anio, anio_ant, clarity_funnel, clarity_friction,
                  mes_oms_ant=mes_oms_ant, gopersonal_diario=gopersonal_diario,
                  gopersonal_eventos=gopersonal_eventos)
    except Exception as e:
        print(f"[CONVERSION] CRO sync error (no bloqueante): {e}")


if __name__ == "__main__":
    main()
