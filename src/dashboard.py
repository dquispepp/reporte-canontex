"""Genera el dashboard HTML autocontenido (Chart.js por CDN, datos embebidos)."""
import json

import pandas as pd
from jinja2 import Template

TEMPLATE = Template(r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>Dashboard Atrasos — Canontex — {{ fecha }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
 *{box-sizing:border-box} body{font-family:Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#f4f6f8;color:#1a2233}
 header{background:#1F4E78;color:#fff;padding:18px 26px} header h1{margin:0;font-size:21px} header p{margin:4px 0 0;opacity:.85;font-size:13px}
 main{padding:22px 26px 60px;max-width:1400px;margin:0 auto}
 .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:24px}
 .kpi{background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 .kpi .label{font-size:11.5px;color:#667;text-transform:uppercase;letter-spacing:.04em} .kpi .value{font-size:26px;font-weight:700;margin-top:6px;color:#1F4E78}
 .kpi.alert .value{color:#c0392b}
 .charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px;margin-bottom:24px}
 .card{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)} .card h3{margin:0 0 8px;font-size:13.5px;color:#33415c} .card canvas{max-height:290px}
 .filters{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:12px;background:#fff;padding:12px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 .filters select,.filters input{padding:7px 9px;border:1px solid #ccd3dd;border-radius:6px;font-size:13px} .filters button{padding:7px 14px;border:none;border-radius:6px;background:#1F4E78;color:#fff;cursor:pointer;font-size:13px}
 .table-wrap{background:#fff;border-radius:10px;padding:4px;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow-x:auto}
 table{border-collapse:collapse;width:100%;font-size:12.5px} th,td{padding:8px 10px;border-bottom:1px solid #eef0f3;text-align:left;white-space:nowrap} th{background:#f0f3f7;position:sticky;top:0;cursor:pointer}
 .badge{padding:2px 7px;border-radius:999px;font-size:11px;font-weight:600} .badge.a{background:#fdecea;color:#c0392b} .badge.o{background:#eafaf1;color:#1e8449}
 .rc{font-size:12px;color:#667;padding:8px 10px}
</style></head><body>
<header><h1>Dashboard de Pedidos Atrasados — Ecommerce/Omnicanal</h1><p>Generado: {{ generado }} · Cruce WMS + Reporte</p></header>
<main>
 <section class="kpis">
  <div class="kpi"><div class="label">Pedidos abiertos</div><div class="value">{{ k.total_abiertos }}</div></div>
  <div class="kpi"><div class="label">% OTIF</div><div class="value">{{ k.pct_otif }}%</div></div>
  <div class="kpi alert"><div class="label">Atrasados</div><div class="value">{{ k.atrasados }} ({{ k.pct_atrasados }}%)</div></div>
  <div class="kpi"><div class="label">Días atraso prom.</div><div class="value">{{ k.dias_atraso_prom }}</div></div>
  <div class="kpi alert"><div class="label">Reserva sin OV</div><div class="value">{{ k.reserva_sin_ov }}</div></div>
  <div class="kpi alert"><div class="label">No están en WMS</div><div class="value">{{ k.no_wms }}</div></div>
 </section>
 <section class="charts">
  <div class="card"><h3>Atrasos por diagnóstico</h3><canvas id="cDiag"></canvas></div>
  <div class="card"><h3>Atrasos por transportista</h3><canvas id="cTrans"></canvas></div>
  <div class="card"><h3>Atrasos por región</h3><canvas id="cReg"></canvas></div>
  <div class="card"><h3>Atrasos por familia</h3><canvas id="cFam"></canvas></div>
  <div class="card" style="grid-column:1/-1"><h3>Evolución diaria: creación vs despacho (WMS)</h3><canvas id="cEvo"></canvas></div>
 </section>
 <section class="filters">
  <select id="fCanal"><option value="">Canal (todos)</option></select>
  <select id="fEstado"><option value="">Estado (todos)</option></select>
  <select id="fReg"><option value="">Región (todas)</option></select>
  <select id="fTrans"><option value="">Transportista (todos)</option></select>
  <select id="fDesp"><option value="">Tipo despacho (todos)</option></select>
  <select id="fFam"><option value="">Familia (todas)</option></select>
  <select id="fDiag"><option value="">Diagnóstico (todos)</option></select>
  <input type="date" id="fD1" title="Fecha Trx desde"><input type="date" id="fD2" title="Fecha Trx hasta">
  <input type="text" id="fQ" placeholder="Buscar OC / N° envío...">
  <button id="btnExp">Exportar CSV</button>
 </section>
 <div class="table-wrap"><div class="rc"><span id="rc"></span> pedidos</div>
  <table id="t"><thead><tr>
   <th data-k="envio">N° Envío</th><th data-k="oc">OC</th><th data-k="canal">Canal</th><th data-k="fecha_trx">Fecha Trx</th>
   <th data-k="region">Región</th><th data-k="transportista">Transportista</th><th data-k="tipo_despacho">Tipo Despacho</th>
   <th data-k="familia">Familia</th><th data-k="estado_reporte">Estado Reporte</th><th data-k="estado_wms">Estado WMS</th>
   <th data-k="diagnostico">Diagnóstico</th><th data-k="dias_atraso">Días Atraso</th>
  </tr></thead><tbody id="tb"></tbody></table>
 </div>
</main>
<script>
const DATA={{ pedidos_json | safe }}, AGG={{ agg_json | safe }};
function fill(id,vals){const s=document.getElementById(id);[...new Set(vals)].filter(Boolean).sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;s.appendChild(o)})}
fill('fCanal',DATA.map(d=>d.canal));fill('fEstado',DATA.map(d=>d.estado_reporte));fill('fReg',DATA.map(d=>d.region));fill('fTrans',DATA.map(d=>d.transportista));fill('fDesp',DATA.map(d=>d.tipo_despacho));fill('fFam',DATA.map(d=>d.familia));fill('fDiag',DATA.map(d=>d.diagnostico));
let sk=null,sa=true;
function render(){
 const g=id=>document.getElementById(id).value;
 const ca=g('fCanal'),es=g('fEstado'),reg=g('fReg'),tr=g('fTrans'),de=g('fDesp'),fa=g('fFam'),di=g('fDiag'),d1=g('fD1'),d2=g('fD2'),q=g('fQ').trim().toLowerCase();
 let rows=DATA.filter(d=>(!ca||d.canal===ca)&&(!es||d.estado_reporte===es)&&(!reg||d.region===reg)&&(!tr||d.transportista===tr)&&(!de||d.tipo_despacho===de)&&(!fa||d.familia===fa)&&(!di||d.diagnostico===di)&&(!d1||(d.fecha_trx&&d.fecha_trx>=d1))&&(!d2||(d.fecha_trx&&d.fecha_trx<=d2))&&(!q||(d.oc||'').toLowerCase().includes(q)||(d.envio||'').toLowerCase().includes(q)));
 if(sk){rows=rows.slice().sort((a,b)=>{const x=a[sk]??'',y=b[sk]??'';return x<y?(sa?-1:1):x>y?(sa?1:-1):0})}
 document.getElementById('rc').textContent=rows.length;
 document.getElementById('tb').innerHTML=rows.slice(0,3000).map(d=>`<tr><td>${d.envio}</td><td>${d.oc}</td><td>${d.canal??''}</td><td>${d.fecha_trx??''}</td><td>${d.region??''}</td><td>${d.transportista??''}</td><td>${d.tipo_despacho??''}</td><td>${d.familia??''}</td><td>${d.estado_reporte??''}</td><td>${d.estado_wms??''}</td><td>${d.diagnostico??''}</td><td>${d.atrasado?`<span class="badge a">${d.dias_atraso??''}</span>`:'<span class="badge o">0</span>'}</td></tr>`).join('');
 return rows;
}
document.querySelectorAll('#t th').forEach(th=>th.addEventListener('click',()=>{const k=th.dataset.k;sa=sk===k?!sa:true;sk=k;render()}));
['fCanal','fEstado','fReg','fTrans','fDesp','fFam','fDiag','fD1','fD2','fQ'].forEach(id=>document.getElementById(id).addEventListener('input',render));
document.getElementById('btnExp').addEventListener('click',()=>{const rows=render();const h=['envio','oc','canal','fecha_trx','region','transportista','tipo_despacho','familia','estado_reporte','estado_wms','diagnostico','dias_atraso'];const csv=[h.join(',')].concat(rows.map(r=>h.map(k=>`"${(r[k]??'').toString().replace(/"/g,'""')}"`).join(','))).join('\n');const b=new Blob([csv],{type:'text/csv;charset=utf-8;'});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='atrasos_filtrado.csv';a.click();URL.revokeObjectURL(u)});
function bar(id,d,color){new Chart(document.getElementById(id),{type:'bar',data:{labels:d.map(x=>x.k),datasets:[{data:d.map(x=>x.v),backgroundColor:color}]},options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}})}
bar('cDiag',AGG.diag,'#c0392b');bar('cTrans',AGG.trans,'#1F4E78');bar('cReg',AGG.reg,'#2980b9');bar('cFam',AGG.fam,'#8e44ad');
new Chart(document.getElementById('cEvo'),{type:'line',data:{labels:AGG.evo.map(x=>x.f),datasets:[{label:'Creación',data:AGG.evo.map(x=>x.c),borderColor:'#1F4E78',tension:.2},{label:'Despacho',data:AGG.evo.map(x=>x.d),borderColor:'#c0392b',tension:.2}]},options:{scales:{y:{beginAtZero:true}}}});
render();
</script></body></html>""")


def _iso(v):
    return None if pd.isna(v) else pd.Timestamp(v).strftime("%Y-%m-%d")


def _pedidos(df):
    out = []
    for _, r in df.iterrows():
        out.append({
            "envio": r.get("num_envio", ""),
            "oc": str(r.get("orden_compra", "") or ""),
            "canal": r.get("canal"),
            "fecha_trx": _iso(r.get("fecha_trx")),
            "region": r.get("region"),
            "transportista": r.get("transportista_norm"),
            "tipo_despacho": r.get("tipo_despacho"),
            "familia": r.get("familia"),
            "estado_reporte": r.get("estado"),
            "estado_wms": None if pd.isna(r.get("estado_wms")) else r.get("estado_wms"),
            "diagnostico": r.get("diagnostico"),
            "atrasado": bool(r.get("atrasado")),
            "dias_atraso": None if pd.isna(r.get("dias_atraso")) else int(r.get("dias_atraso")),
        })
    return out


def _agg(df):
    a = df[df["atrasado"]]

    def cnt(col):
        return [{"k": str(k), "v": int(v)} for k, v in a[col].value_counts().items()]

    crea = df["fecha_creacion"].dropna().dt.strftime("%Y-%m-%d").value_counts().sort_index() if "fecha_creacion" in df.columns else pd.Series(dtype=int)
    desp = df["fecha_despacho"].dropna().dt.strftime("%Y-%m-%d").value_counts().sort_index() if "fecha_despacho" in df.columns else pd.Series(dtype=int)
    fechas = sorted(set(crea.index) | set(desp.index))
    return {
        "diag": cnt("diagnostico"),
        "trans": cnt("transportista_norm"),
        "reg": cnt("region"),
        "fam": cnt("familia"),
        "evo": [{"f": f, "c": int(crea.get(f, 0)), "d": int(desp.get(f, 0))} for f in fechas],
    }


def build_dashboard(resultado, kpis, output_path, generado):
    html = TEMPLATE.render(
        fecha=kpis["fecha"], generado=generado, k=kpis,
        pedidos_json=json.dumps(_pedidos(resultado), ensure_ascii=False),
        agg_json=json.dumps(_agg(resultado), ensure_ascii=False),
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _iso_dt(v):
    return None if pd.isna(v) else pd.Timestamp(v).strftime("%Y-%m-%d")


def _detalle_pedidos(df: pd.DataFrame) -> list:
    """Detalle compacto por pedido: campos suficientes para filtros y KPIs cliente-side."""
    out = []
    for _, r in df.iterrows():
        out.append({
            "envio": r.get("num_envio", ""),
            "canal": r.get("canal", ""),
            "tipo_despacho": r.get("tipo_despacho", ""),
            "familia": r.get("familia", ""),
            "region": r.get("region", ""),
            "estado": r.get("estado", ""),
            "fecha_trx": _iso_dt(r.get("fecha_trx")),
            "atrasado": bool(r.get("atrasado", False)),
            "sla_ecommerce": None if pd.isna(r.get("sla_ecommerce")) else bool(r.get("sla_ecommerce")),
            "sla_operacion": None if pd.isna(r.get("sla_operacion")) else bool(r.get("sla_operacion")),
            "sla_courier": None if pd.isna(r.get("sla_courier")) else bool(r.get("sla_courier")),
            "diagnostico": r.get("diagnostico", ""),
            "dias_atraso": None if pd.isna(r.get("dias_atraso")) else int(r.get("dias_atraso")),
        })
    return out


def export_dashboard_json(resultado, hoy_str, output_path, anulados: int = 0):
    """Exporta detalle + metadata. Los KPIs y filtros se calculan cliente-side en el HTML."""
    # Solo canales relevantes y con fecha_trx valida
    df = resultado[resultado["canal"].isin(("ECOMMERCE", "KIOSCO"))].copy()
    detalle = _detalle_pedidos(df)

    # Universos disponibles para armar los selectores
    canales = sorted({p["canal"] for p in detalle if p["canal"]})
    tipos_desp = sorted({p["tipo_despacho"] for p in detalle if p["tipo_despacho"]})
    familias = sorted({p["familia"] for p in detalle if p["familia"]})
    meses = sorted({p["fecha_trx"][:7] for p in detalle if p["fecha_trx"]})

    data = {
        "fecha": hoy_str,
        "total_pedidos": len(detalle),
        "anulados_excluidos": int(anulados),
        "filtros": {
            "canales": canales,
            "tipos_despacho": tipos_desp,
            "familias": familias,
            "meses": meses,
        },
        "detalle": detalle,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
