# Resumen pedidos atrasados Canontex — 2026-08-28

## KPIs
- Pedidos abiertos: 65,054
- Atrasados: 811 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 21.5
- Sin ingreso WMS: 23
- Venta futura: 23
- Reservas sin OV: 10
- SLA Ecommerce: 84.3%
- SLA Operacion: 74.9%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 611
- Courier tiene pedido, estado no actualizado en OMS: 72
- SAC devolución de dinero: 44
- Recontactar cliente: 19
- En ruta (atraso courier): 14
- Quiebre SAP: 14
- Aún no sale, empujar operación: 11
- Revisar WMS: no despachado: 9
- FedEx no recolectó, revisar en bodega: 5
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 4
- Quiebre WMS: 3
- Investigar por qué no llegó al WMS: 2
- Quiebre SAP/WMS: 2
- Courier no encontró destino: 1

## Atrasados por tipo despacho
- Cross Docking: 478
- Retiro en Tienda: 226
- Despacho a Domicilio: 101
- Fecha Pactada: 6

## Atrasados por transportista
- Transporte propio: 701
- BigTicket: 62
- Fedex2: 34
- -: 14

## Atrasados por region
- Metropolitana: 326
- Libertador General Bernardo OHiggins: 111
- Los Lagos: 72
- Antofagasta: 60
- Coquimbo: 44
- Valparaiso: 41
- Bío Bío: 39
- Bio Bio: 36
- Ñuble: 32
- Valparaíso: 20

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 168.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 164.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 164.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 157.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 157.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 156.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 156.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 146.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 142.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 142.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 131.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 131.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 129.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 127.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015691 | 1683287 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 126.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 204
- Libertador General Bernardo OHiggins: 105
- Los Lagos: 58
- Antofagasta: 57
- Coquimbo: 41
- Valparaiso: 34
- Bio Bio: 33
- Ñuble: 30
- Bío Bío: 25
- Valparaíso: 10
- Araucania: 9
- Los Rios: 4
- Araucanía: 1

*Generado automaticamente el 2026-08-28 por el pipeline de atrasos.*