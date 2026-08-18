# Resumen pedidos atrasados Canontex — 2026-08-18

## KPIs
- Pedidos abiertos: 63,391
- Atrasados: 736 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 20.3
- Sin ingreso WMS: 29
- Venta futura: 29
- Reservas sin OV: 12
- SLA Ecommerce: 84.3%
- SLA Operacion: 74.7%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 460
- Courier tiene pedido, estado no actualizado en OMS: 93
- SAC devolución de dinero: 39
- Recontactar cliente: 37
- En ruta (atraso courier): 28
- validar con SAC: 21
- Quiebre SAP: 16
- FedEx no recolectó, revisar en bodega: 10
- Courier no encontró destino: 7
- Aún no sale, empujar operación: 7
- Revisar WMS: no despachado: 6
- Quiebre SAP/WMS: 5
- Investigar por qué no llegó al WMS: 4
- Quiebre WMS: 2
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 1

## Atrasados por tipo despacho
- Cross Docking: 341
- Retiro en Tienda: 203
- Despacho a Domicilio: 188
- Fecha Pactada: 4

## Atrasados por transportista
- Transporte propio: 533
- BigTicket: 103
- Fedex2: 63
- -: 37

## Atrasados por region
- Metropolitana: 330
- Libertador General Bernardo OHiggins: 78
- Los Lagos: 57
- Antofagasta: 47
- Bío Bío: 39
- Bio Bio: 37
- Ñuble: 28
- Valparaiso: 27
- Valparaíso: 25
- Coquimbo: 22

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 160.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 156.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 156.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 149.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 149.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 149.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 148.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 148.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 138.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 134.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 134.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 123.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 123.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 165
- Libertador General Bernardo OHiggins: 71
- Los Lagos: 44
- Antofagasta: 41
- Bio Bio: 33
- Ñuble: 26
- Bío Bío: 22
- Coquimbo: 19
- Valparaiso: 19
- Valparaíso: 9
- Araucania: 8
- Los Rios: 2
- Araucanía: 1

*Generado automaticamente el 2026-08-18 por el pipeline de atrasos.*