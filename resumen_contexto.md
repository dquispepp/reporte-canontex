# Resumen pedidos atrasados Canontex — 2026-08-27

## KPIs
- Pedidos abiertos: 64,919
- Atrasados: 809 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 20.6
- Sin ingreso WMS: 20
- Venta futura: 20
- Reservas sin OV: 11
- SLA Ecommerce: 84.3%
- SLA Operacion: 75.0%
- SLA Courier: 87.9%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 608
- Courier tiene pedido, estado no actualizado en OMS: 73
- SAC devolución de dinero: 44
- Recontactar cliente: 20
- En ruta (atraso courier): 15
- Revisar WMS: no despachado: 15
- Quiebre SAP: 14
- FedEx no recolectó, revisar en bodega: 4
- Investigar por qué no llegó al WMS: 4
- Quiebre WMS: 3
- Aún no sale, empujar operación: 3
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 3
- Quiebre SAP/WMS: 2
- Courier no encontró destino: 1

## Atrasados por tipo despacho
- Cross Docking: 477
- Retiro en Tienda: 233
- Despacho a Domicilio: 98
- Fecha Pactada: 1

## Atrasados por transportista
- Transporte propio: 708
- BigTicket: 59
- Fedex2: 34
- -: 8

## Atrasados por region
- Metropolitana: 325
- Libertador General Bernardo OHiggins: 105
- Los Lagos: 71
- Antofagasta: 60
- Coquimbo: 45
- Valparaiso: 41
- Bío Bío: 39
- Bio Bio: 36
- Ñuble: 31
- Valparaíso: 19

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 167.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 163.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 163.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 156.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 156.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 155.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 155.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 145.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 141.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 141.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 130.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 130.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 128.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015691 | 1683287 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 207
- Libertador General Bernardo OHiggins: 99
- Los Lagos: 58
- Antofagasta: 57
- Coquimbo: 41
- Valparaiso: 34
- Bio Bio: 33
- Ñuble: 29
- Bío Bío: 25
- Araucania: 10
- Valparaíso: 10
- Los Rios: 4
- Araucanía: 1

*Generado automaticamente el 2026-08-27 por el pipeline de atrasos.*