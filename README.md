# Reporte diario de ventas - Canontex

Extrae datos de https://canontex.bbr.cl (login + endpoint /webapp/wsrest/getDashboardVenta)
y genera un Excel con: resumen, ventas por canal, top SKU y ventas por marca.

## Uso local

pip install -r requirements.txt
export OMS_USER=tu_usuario
export OMS_PASS=tu_password
python reporte_diario.py

El archivo queda en ./reportes/reporte_ventas_<fecha>.xlsx.

## Automatización diaria

Ya incluido en .github/workflows/reporte-diario.yml: corre todos los días a las 09:00 (Chile).
Falta: en GitHub, Settings → Secrets and variables → Actions, agregar OMS_USER y OMS_PASS.
El reporte queda como artefacto descargable en cada ejecución (pestaña Actions).

---

## Rutina diaria de Pedidos Atrasados (Cruce WMS + Reporte)

Cruza el gestor de pedidos ("Reporte", multi-CSV) con el WMS ("Documento de Salida", xlsx)
para detectar pedidos atrasados y su causa raíz. Genera un Excel ejecutivo y un dashboard HTML.

### Uso

```
pip install -r requirements.txt
python run_daily.py
```

Lee los inputs desde OneDrive (`Documentos\DOC DANI`):
- `Reporte\*.csv` — todos los CSV por bimestre (sep=`;`, latin-1). Se cargan **todos** y se
  deduplican por línea, porque los nombres de bimestre se solapan; el rango real está en `Fecha Trx`.
- `Reporte WMS\DocumentoSalida*.xlsx` — se toma el más reciente por fecha de modificación.

Genera en la misma carpeta `DOC DANI`:
- `resumen_atrasos_YYYY-MM-DD.xlsx` — Excel ejecutivo (3 hojas: Resumen Ejecutivo, Retiro Tienda
  y CrossDocking, Domicilio y Fecha Pactada), solo pedidos atrasados a hoy.
- `dashboard_YYYY-MM-DD.html` + `dashboard.html` (latest) — dashboard autocontenido con KPIs,
  gráficos Chart.js y tabla filtrable con export CSV.
- Resumen ejecutivo impreso en consola (listo para pegar en correo).

### Estructura

- `src/load.py` — carga y consolidación de fuentes, dedupe, filtros de scope, cruce (left join Reporte→WMS)
- `src/keys.py` — normalización de llaves de cruce y resolución de nombres de columna
- `src/rules.py` — días hábiles (feriados Chile), OTIF interno, atraso, familia, diagnóstico y marcas de gestión
- `src/report.py` — Excel ejecutivo de 3 hojas con formato condicional y glosario
- `src/dashboard.py` — genera el dashboard HTML (plantilla Jinja2 embebida)
- `run_daily.py` — orquesta la rutina completa e imprime el resumen

### Alcance temporal

El WMS solo cubre el año en curso (arranca en enero). El análisis de atrasos se acota a las
cabeceras con `Fecha Trx >= min(FechaCreacion del WMS)`, para no marcar como "NO EXISTE EN WMS"
pedidos anteriores al alcance del WMS. (Los CSV se cargan igual completos para el dedupe por solape.)

### Automatización con Task Scheduler (Windows)

Programar diario 8:00 AM:

```
schtasks /Create /SC DAILY /ST 08:00 /TN "Atrasos Canontex" ^
  /TR "python \"C:\Users\dquispe\OneDrive - Representaciones Canontex Ltda\Escritorio\reporte-canontex\run_daily.py\""
```

O vía la GUI de "Programador de tareas": acción = iniciar programa `python`, argumento = ruta a
`run_daily.py`, iniciar en la carpeta del repo.

### Roadmap MCP Hub (SAP/DOMS)

Cuando el MCP Hub esté conectado, reemplazar solo `src/load.py` por llamadas MCP,
dejando `keys.py`, `rules.py`, `report.py` y `dashboard.py` intactos:
- WMS y Reporte → conectores internos vía MCP en lugar de leer OneDrive.
- SAP → validar facturación cruzando `NroReferencia2` (DocNum SAP), ya disponible en el merge.
