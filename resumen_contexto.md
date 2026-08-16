# Resumen pedidos atrasados Canontex — 2026-08-16

## KPIs
- Pedidos abiertos: 63,073
- Atrasados: 762 (1.2%)
- OTIF: 98.8%
- Dias atraso promedio: 20.2
- Sin ingreso WMS: 544
- Venta futura: 544
- Reservas sin OV: 8
- SLA Ecommerce: 84.6%
- SLA Operacion: 74.8%
- SLA Courier: 88.0%

## Atrasados por diagnostico
- En tienda, esperando retiro cliente: 480
- Courier tiene pedido, estado no actualizado en OMS: 88
- SAC devolución de dinero: 39
- Recontactar cliente: 39
- En ruta (atraso courier): 28
- validar con SAC: 21
- Quiebre SAP: 16
- Aún no sale, empujar operación: 15
- FedEx no recolectó, revisar en bodega: 10
- Revisar WMS: no despachado: 8
- Courier no encontró destino: 7
- Quiebre SAP/WMS: 5
- Investigar por qué no llegó al WMS: 3
- Quiebre WMS: 2
- REVISAR MANUAL: 1

## Atrasados por tipo despacho
- Cross Docking: 361
- Retiro en Tienda: 205
- Despacho a Domicilio: 192
- Fecha Pactada: 4

## Atrasados por transportista
- Transporte propio: 554
- BigTicket: 100
- Fedex2: 65
- -: 43

## Atrasados por region
- Metropolitana: 345
- Libertador General Bernardo OHiggins: 106
- Los Lagos: 58
- Antofagasta: 46
- Bío Bío: 33
- Valparaiso: 28
- Bio Bio: 25
- Ñuble: 25
- Valparaíso: 24
- Coquimbo: 22

## Top 20 pedidos mas atrasados
| envio_norm | orden_compra_norm | canal | estado | tipo_despacho | transportista | dias_atraso | diagnostico | region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000987598 | 1648150 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 159.0 | SAC devolución de dinero | Metropolitana |
| 000988600 | 1648750 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 155.0 | SAC devolución de dinero | Metropolitana |
| 000990691 | 1650526 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 155.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000987613 | 1648159 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 148.0 | En tienda, esperando retiro cliente | Metropolitana |
| 000990556 | 1650358 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 148.0 | SAC devolución de dinero | Valparaíso |
| 000990697 | 1650376 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 148.0 | SAC devolución de dinero | Valparaíso |
| 000991006 | 1650937 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 147.0 | En tienda, esperando retiro cliente | Libertador General Bernardo OHiggins |
| 000992632 | 1653022 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 147.0 | SAC devolución de dinero | Metropolitana |
| 000998042 | 1659935 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 137.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001003244 | 1666706 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 133.0 | SAC devolución de dinero | Metropolitana |
| 001004570 | 1668428 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 133.0 | SAC devolución de dinero | Metropolitana |
| 001010417 | 1676213 | ECOMMERCE | Listo Para Retiro | Retiro en Tienda | Transporte propio | 122.0 | En tienda, esperando retiro cliente | Metropolitana |
| 001011143 | 1677251 | ECOMMERCE | Rechazado | Retiro en Tienda | Transporte propio | 122.0 | SAC devolución de dinero | Libertador General Bernardo OHiggins |
| 001012565 | 1679051 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 120.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015721 | 1683335 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 118.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001013879 | 1680836 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 117.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001014950 | 1682285 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 117.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015034 | 1682405 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 117.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015196 | 1682639 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 117.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |
| 001015637 | 1683224 | ECOMMERCE | Preparado | Despacho a Domicilio | BigTicket | 117.0 | Courier tiene pedido, estado no actualizado en OMS | Metropolitana |

## Retiro en tienda por tienda (top 15)
- Metropolitana: 175
- Libertador General Bernardo OHiggins: 99
- Los Lagos: 44
- Antofagasta: 41
- Ñuble: 23
- Bio Bio: 21
- Coquimbo: 20
- Valparaiso: 19
- Bío Bío: 17
- Araucania: 9
- Valparaíso: 9
- Los Rios: 2
- Araucanía: 1

*Generado automaticamente el 2026-08-16 por el pipeline de atrasos.*