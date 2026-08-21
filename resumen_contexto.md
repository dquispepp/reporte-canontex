# Resumen pedidos atrasados Canontex — 2026-08-21

## KPIs
- Pedidos abiertos: 63,869
- Atrasados: 806 (1.3%)
- OTIF: 98.7%
- Dias atraso promedio: 19.6
- Sin ingreso WMS: 66
- Venta futura: 66
- Reservas sin OV: 9
- SLA Ecommerce: 84.2%
- SLA Operacion: 74.9%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 546
- Courier tiene pedido, estado no actualizado en OMS: 90
- SAC devolución de dinero: 46
- Aún no sale, empujar operación: 24
- Recontactar cliente: 23
- En ruta (atraso courier): 18
- Revisar WMS: no despachado: 16
- Quiebre SAP: 15
- FedEx no recolectó, revisar en bodega: 9
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 5
- Courier no encontró destino: 3
- Quiebre SAP/WMS: 3
- Investigar por qué no llegó al WMS: 3
- validar con SAC: 3
- Quiebre WMS: 2

## Atrasados por tipo despacho
- Cross Docking: 426
- Retiro en Tienda: 234
- Despacho a Domicilio: 145
- Fecha Pactada: 1

## Atrasados por transportista
- Transporte propio: 636
- BigTicket: 93
- Fedex2: 45
- -: 32

## Atrasados por region
- Metropolitana: 361
- Libertador General Bernardo OHiggins: 103
- Coquimbo: 56
- Los Lagos: 55
- Antofagasta: 46
- Bío Bío: 33
- Valparaiso: 33
- Ñuble: 31
- Bio Bio: 31
- Valparaíso: 24

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 163.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 159.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 159.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 152.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 152.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 152.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 151.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 151.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 141.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 137.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 137.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 126.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 126.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 124.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 204
- Libertador General Bernardo OHiggins: 97
- Los Lagos: 44
- Antofagasta: 40
- Coquimbo: 35
- Ñuble: 28
- Valparaiso: 26
- Bio Bio: 26
- Bío Bío: 19
- Valparaíso: 15
- Araucania: 9
- Los Rios: 2
- Araucanía: 1

*Generado automaticamente el 2026-08-21 por el pipeline de atrasos.*