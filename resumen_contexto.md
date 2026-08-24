# Resumen pedidos atrasados Canontex — 2026-08-24

## KPIs
- Pedidos abiertos: 64,434
- Atrasados: 815 (1.3%)
- OTIF: 98.7%
- Dias atraso promedio: 20.0
- Sin ingreso WMS: 369
- Venta futura: 369
- Reservas sin OV: 15
- SLA Ecommerce: 84.2%
- SLA Operacion: 74.9%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 562
- Courier tiene pedido, estado no actualizado en OMS: 92
- SAC devolución de dinero: 46
- Aún no sale, empujar operación: 25
- Recontactar cliente: 21
- En ruta (atraso courier): 16
- Quiebre SAP: 14
- Revisar WMS: no despachado: 12
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 7
- FedEx no recolectó, revisar en bodega: 6
- Quiebre WMS: 4
- Investigar por qué no llegó al WMS: 3
- validar con SAC: 3
- Courier no encontró destino: 2
- Quiebre SAP/WMS: 2

## Atrasados por tipo despacho
- Cross Docking: 456
- Retiro en Tienda: 222
- Despacho a Domicilio: 136
- Fecha Pactada: 1

## Atrasados por transportista
- Transporte propio: 654
- BigTicket: 89
- Fedex2: 38
- -: 34

## Atrasados por region
- Metropolitana: 351
- Libertador General Bernardo OHiggins: 103
- Los Lagos: 71
- Antofagasta: 64
- Coquimbo: 55
- Bío Bío: 33
- Valparaiso: 29
- Ñuble: 29
- Bio Bio: 29
- Valparaíso: 20

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 164.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 160.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 160.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 153.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 153.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 153.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 152.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 152.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 142.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 138.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 138.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 127.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 127.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 125.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 199
- Libertador General Bernardo OHiggins: 97
- Los Lagos: 58
- Antofagasta: 58
- Coquimbo: 34
- Ñuble: 26
- Bio Bio: 24
- Valparaiso: 23
- Bío Bío: 19
- Valparaíso: 10
- Araucania: 9
- Los Rios: 4
- Araucanía: 1

*Generado automaticamente el 2026-08-24 por el pipeline de atrasos.*