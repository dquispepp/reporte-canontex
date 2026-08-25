# Resumen pedidos atrasados Canontex — 2026-08-25

## KPIs
- Pedidos abiertos: 64,636
- Atrasados: 838 (1.3%)
- OTIF: 98.7%
- Dias atraso promedio: 19.9
- Sin ingreso WMS: 59
- Venta futura: 59
- Reservas sin OV: 15
- SLA Ecommerce: 84.2%
- SLA Operacion: 74.9%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 598
- Courier tiene pedido, estado no actualizado en OMS: 87
- SAC devolución de dinero: 45
- Revisar WMS: no despachado: 34
- Recontactar cliente: 20
- En ruta (atraso courier): 16
- Quiebre SAP: 14
- FedEx no recolectó, revisar en bodega: 6
- Investigar por qué no llegó al WMS: 4
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 4
- Quiebre WMS: 3
- Courier no encontró destino: 2
- Quiebre SAP/WMS: 2
- Aún no sale, empujar operación: 2
- validar con SAC: 1

## Atrasados por tipo despacho
- Cross Docking: 483
- Retiro en Tienda: 227
- Despacho a Domicilio: 126
- Fecha Pactada: 2

## Atrasados por transportista
- Transporte propio: 708
- BigTicket: 88
- Fedex2: 33
- -: 9

## Atrasados por region
- Metropolitana: 351
- Libertador General Bernardo OHiggins: 103
- Los Lagos: 71
- Antofagasta: 62
- Coquimbo: 62
- Bío Bío: 41
- Bio Bio: 37
- Ñuble: 32
- Valparaiso: 31
- Valparaíso: 19

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 165.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 161.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 161.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 154.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 154.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 153.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 153.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 143.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 139.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 139.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 128.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 128.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 124.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015691 | 1683287 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 206
- Libertador General Bernardo OHiggins: 97
- Los Lagos: 58
- Antofagasta: 58
- Coquimbo: 41
- Bio Bio: 33
- Ñuble: 30
- Bío Bío: 26
- Valparaiso: 25
- Valparaíso: 10
- Araucania: 9
- Los Rios: 4
- Araucanía: 1

*Generado automaticamente el 2026-08-25 por el pipeline de atrasos.*