# Resumen pedidos atrasados Canontex — 2026-08-31

## KPIs
- Pedidos abiertos: 65,666
- Atrasados: 783 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 21.7
- Sin ingreso WMS: 45
- Venta futura: 45
- Reservas sin OV: 11
- SLA Ecommerce: 84.2%
- SLA Operacion: 74.8%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 596
- Courier tiene pedido, estado no actualizado en OMS: 61
- SAC devolución de dinero: 45
- En ruta (atraso courier): 18
- Recontactar cliente: 17
- Quiebre SAP: 14
- Revisar WMS: no despachado: 10
- FedEx no recolectó, revisar en bodega: 5
- Aún no sale, empujar operación: 4
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 4
- Investigar por qué no llegó al WMS: 3
- Quiebre WMS: 3
- Quiebre SAP/WMS: 2
- Courier no encontró destino: 1

## Atrasados por tipo despacho
- Cross Docking: 473
- Retiro en Tienda: 215
- Despacho a Domicilio: 93
- Fecha Pactada: 2

## Atrasados por transportista
- Transporte propio: 686
- BigTicket: 53
- Fedex2: 36
- -: 8

## Atrasados por region
- Metropolitana: 313
- Libertador General Bernardo OHiggins: 84
- Los Lagos: 76
- Antofagasta: 72
- Coquimbo: 44
- Valparaiso: 40
- Bío Bío: 36
- Bio Bio: 36
- Ñuble: 31
- Valparaíso: 19

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 169.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 165.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 165.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 158.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 158.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 157.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 157.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 147.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 143.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 143.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 132.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 132.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 130.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 128.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015691 | 1683287 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 204
- Libertador General Bernardo OHiggins: 78
- Antofagasta: 68
- Los Lagos: 63
- Coquimbo: 41
- Valparaiso: 34
- Bio Bio: 32
- Ñuble: 29
- Bío Bío: 22
- Valparaíso: 10
- Araucania: 9
- Los Rios: 5
- Araucanía: 1

*Generado automaticamente el 2026-08-31 por el pipeline de atrasos.*