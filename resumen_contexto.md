# Resumen pedidos atrasados Canontex — 2026-08-20

## KPIs
- Pedidos abiertos: 63,730
- Atrasados: 775 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 19.8
- Sin ingreso WMS: 121
- Venta futura: 121
- Reservas sin OV: 10
- SLA Ecommerce: 84.3%
- SLA Operacion: 74.9%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 508
- Courier tiene pedido, estado no actualizado en OMS: 90
- SAC devolución de dinero: 44
- En ruta (atraso courier): 24
- Recontactar cliente: 24
- Aún no sale, empujar operación: 24
- Revisar WMS: no despachado: 16
- Quiebre SAP: 16
- FedEx no recolectó, revisar en bodega: 8
- Quiebre SAP/WMS: 5
- validar con SAC: 4
- Operación: WMS despachó pero OMS sigue en Creado, validar medio de despacho: 4
- Courier no encontró destino: 3
- Investigar por qué no llegó al WMS: 3
- Quiebre WMS: 2

## Atrasados por tipo despacho
- Cross Docking: 391
- Retiro en Tienda: 227
- Despacho a Domicilio: 153
- Fecha Pactada: 4

## Atrasados por transportista
- Transporte propio: 594
- BigTicket: 97
- Fedex2: 52
- -: 32

## Atrasados por region
- Metropolitana: 343
- Libertador General Bernardo OHiggins: 78
- Coquimbo: 56
- Los Lagos: 54
- Antofagasta: 46
- Bio Bio: 36
- Bío Bío: 35
- Valparaiso: 33
- Ñuble: 28
- Valparaíso: 27

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 162.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 158.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 158.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 151.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 151.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 151.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 150.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 150.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 140.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 136.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 136.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 125.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 125.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 123.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 121.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 189
- Libertador General Bernardo OHiggins: 71
- Los Lagos: 44
- Antofagasta: 40
- Coquimbo: 35
- Bio Bio: 31
- Valparaiso: 27
- Ñuble: 25
- Bío Bío: 20
- Valparaíso: 15
- Araucania: 8
- Los Rios: 2
- Araucanía: 1

*Generado automaticamente el 2026-08-20 por el pipeline de atrasos.*