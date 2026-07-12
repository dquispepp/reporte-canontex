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
