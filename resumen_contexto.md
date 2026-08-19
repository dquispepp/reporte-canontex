# Resumen pedidos atrasados Canontex — 2026-08-19

## KPIs
- Pedidos abiertos: 63,569
- Atrasados: 737 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 21.0
- Sin ingreso WMS: 34
- Venta futura: 34
- Reservas sin OV: 10
- SLA Ecommerce: 84.3%
- SLA Operacion: 74.7%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 483
- Courier tiene pedido, estado no actualizado en OMS: 87
- SAC devolución de dinero: 39
- Recontactar cliente: 38
- En ruta (atraso courier): 19
- Quiebre SAP: 17
- validar con SAC: 17
- FedEx no recolectó, revisar en bodega: 10
- Courier no encontró destino: 7
- Revisar WMS: no despachado: 6
- Quiebre SAP/WMS: 5
- Investigar por qué no llegó al WMS: 3
- Aún no sale, empujar operación: 3
- Quiebre WMS: 2
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 1

## Atrasados por tipo despacho
- Cross Docking: 359
- Retiro en Tienda: 204
- Despacho a Domicilio: 170
- Fecha Pactada: 4

## Atrasados por transportista
- Transporte propio: 556
- BigTicket: 101
- Fedex2: 52
- -: 28

## Atrasados por region
- Metropolitana: 329
- Libertador General Bernardo OHiggins: 78
- Los Lagos: 56
- Antofagasta: 46
- Coquimbo: 38
- Bío Bío: 36
- Bio Bio: 36
- Valparaiso: 28
- Ñuble: 28
- Valparaíso: 22

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 161.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 157.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 157.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 150.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 150.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 150.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 149.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 149.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 139.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 135.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 135.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 124.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 124.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 122.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 119.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 172
- Libertador General Bernardo OHiggins: 71
- Los Lagos: 44
- Antofagasta: 41
- Coquimbo: 36
- Bio Bio: 32
- Ñuble: 25
- Bío Bío: 21
- Valparaiso: 21
- Valparaíso: 9
- Araucania: 8
- Los Rios: 2
- Araucanía: 1

*Generado automaticamente el 2026-08-19 por el pipeline de atrasos.*