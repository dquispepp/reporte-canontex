@echo off
REM Rutina diaria de pedidos atrasados (descarga automatica OMSWeb + WMS -> Excel + dashboard).
REM Agendada en Task Scheduler a las 07:00. Requiere estar en la red de Cannon (WMS interno).
REM Las credenciales se leen de las variables de entorno de usuario:
REM   OMS_USER / OMS_PASS / WMS_USER / WMS_PASS

cd /d "C:\Users\dquispe\OneDrive - Representaciones Canontex Ltda\Escritorio\reporte-canontex"
set PYTHONIOENCODING=utf-8

if not exist "logs" mkdir "logs"

"C:\Users\dquispe\AppData\Local\Programs\Python\Python312\python.exe" run_daily_auto.py >> "logs\atrasos_last.log" 2>&1
