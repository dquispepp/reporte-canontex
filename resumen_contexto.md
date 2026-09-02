# Resumen pedidos atrasados Canontex — 2026-09-02

## KPIs
- Pedidos abiertos: 66,056
- Atrasados: 848 (1.3%)
- OTIF: 98.7%
- Dias atraso promedio: 19.2
- Sin ingreso WMS: 313
- Venta futura: 313
- Reservas sin OV: 13
- SLA Ecommerce: 84.2%
- SLA Operacion: 74.7%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 696
- SAC devolución de dinero: 46
- Courier tiene pedido, estado no actualizado en OMS: 38
- Revisar WMS: no despachado: 19
- Recontactar cliente: 16
- En ruta (atraso courier): 14
- Investigar por qué no llegó al WMS: 4
- FedEx no recolectó, revisar en bodega: 3
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 3
- validar con SAC: 3
- Aún no sale, empujar operación: 3
- Courier no encontró destino: 1
- Quiebre WMS: 1
- Fedex no va siempre en la semana: 1

## Atrasados por tipo despacho
- Cross Docking: 558
- Retiro en Tienda: 217
- Despacho a Domicilio: 71
- Fecha Pactada: 2

## Atrasados por transportista
- Transporte propio: 770
- BigTicket: 36
- Fedex2: 32
- -: 10

## Atrasados por region
- Metropolitana: 307
- Coquimbo: 90
- Libertador General Bernardo OHiggins: 84
- Los Lagos: 75
- Antofagasta: 69
- Bio Bio: 58
- Valparaiso: 49
- Bío Bío: 36
- Ñuble: 32
- Valparaíso: 19

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 171.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 167.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 167.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 160.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 160.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 159.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 159.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 149.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 145.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 145.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 134.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 134.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001016516 | 1684343 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 125.0 | SAC devolución de dinero | Metropolitana |
| 001028213 | 1695809 | ECOMMERCE | Preparado | Retiro en Tienda | Transporte propio | 111.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001030839 | 1699257 | ECOMMERCE | Preparado | Retiro en Tienda | Transporte propio | 103.0 | Courier tiene pedido, estado no actualizado en OMS | Bío Bío |
| 001030968 | 1699437 | ECOMMERCE | Preparado | Retiro en Tienda | Transporte propio | 103.0 | Courier tiene pedido, estado no actualizado en OMS | Bío Bío |
| 001031043 | 1699512 | ECOMMERCE | Preparado | Retiro en Tienda | Transporte propio | 103.0 | Courier tiene pedido, estado no actualizado en OMS | Bío Bío |
| 001032531 | 1701468 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 103.0 | En tienda, esperando retiro cliente | Bío Bío |
| 001033557 | 1702872 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 103.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001038888 | 1710003 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 102.0 | En tienda, esperando retiro cliente | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 225
- Coquimbo: 86
- Libertador General Bernardo OHiggins: 82
- Los Lagos: 69
- Antofagasta: 66
- Bio Bio: 51
- Valparaiso: 38
- Ñuble: 30
- Bío Bío: 23
- Araucania: 10
- Valparaíso: 10
- Los Rios: 5
- Araucanía: 1

*Generado automaticamente el 2026-09-02 por el pipeline de atrasos.*