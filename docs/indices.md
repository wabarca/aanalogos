# Catálogo de Índices y Oscilaciones Climáticas

## Contenido

1. [Resumen del Catálogo de 19 Series](#1-resumen-del-catálogo-de-19-series)
2. [Oscilaciones del Pacífico Tropical y ENOS](#2-oscilaciones-del-pacífico-tropical-y-enos)
3. [Oscilaciones del Atlántico y Mar Caribe](#3-oscilaciones-del-atlántico-y-mar-caribe)
4. [Teleconexiones Atmosféricas del Hemisferio Norte y Ártico](#4-teleconexiones-atmosféricas-del-hemisferio-norte-y-ártico)
5. [Umbrales Metodológicos Oficiales](#5-umbrales-metodológicos-oficiales)

---

## 1. Resumen del Catálogo de 19 Series

| Código | Nombre Científico | Institución | Región | Variable | Unidades | Umbral $r$ | Umbral MAD |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **AMO** | Atlantic Multidecadal Oscillation | NOAA PSL | Atlántico Norte (0°–70°N) | Anomalía TSM Kaplan | °C | 0.60 | 0.30 |
| **AO** | Arctic Oscillation | NOAA CPC | Ártico / HN (20°N–90°N) | Anomalía Geopotencial 1000 hPa | Estandarizado | 0.40 | 1.00 |
| **MEI** | Multivariate ENSO Index v2 | NOAA PSL | Pacífico Tropical | Combinación Multivariada | Estandarizado | 0.40 | 0.50 |
| **ONI** | Oceanic Niño Index | NOAA CPC | Niño 3.4 (5°N–5°S, 120°–170°W) | Media Móvil 3m Anomalía TSM | °C | 0.60 | 0.60 |
| **NAO** | North Atlantic Oscillation | NOAA CPC/PSL | Atlántico Norte | Diferencia SLP normalizada | Estandarizado | 0.60 | 0.80 |
| **PDO** | Pacific Decadal Oscillation | NCEI NOAA | Pacífico Norte (> 20°N) | Patrón EOF 1 Anomalía TSM | Estandarizado | 0.40 | 0.60 |
| **TNA** | Tropical Northern Atlantic | NOAA PSL | Atlántico Norte Tropical | Anomalía promedio TSM | °C | 0.50 | 0.30 |
| **SSTA_12** | Niño 1+2 SST Anomaly | NOAA CPC | Pacífico Oriental (0°–10°S) | Anomalía TSM OISST.v2 | °C | 0.60 | 0.60 |
| **SSTA_3** | Niño 3 SST Anomaly | NOAA CPC | Pacífico Central-Oriental | Anomalía TSM OISST.v2 | °C | 0.50 | 0.70 |
| **SSTA_4** | Niño 4 SST Anomaly | NOAA CPC | Pacífico Central-Occidental | Anomalía TSM OISST.v2 | °C | 0.38 | 0.70 |
| **SSTA_34** | Niño 3.4 SST Anomaly | NOAA CPC | Pacífico Central (5°N–5°S) | Anomalía TSM OISST.v2 | °C | 0.60 | 0.60 |
| **AtlTROP** | Tropical Atlantic SST Anomaly | NOAA CPC | Atlántico Ecuatorial | Anomalía TSM OISST.v2 | °C | 0.60 | 0.30 |
| **SAtl** | South Atlantic SST Anomaly | NOAA CPC | Atlántico Sur (Eq–20°S) | Anomalía TSM OISST.v2 | °C | 0.60 | 0.30 |
| **NAtl** | North Atlantic SST Anomaly | NOAA CPC | Atlántico Norte (5°–20°N) | Anomalía TSM OISST.v2 | °C | 0.60 | 0.30 |
| **CAR** | Caribbean SST Index | NOAA PSL | Mar Caribe (10°–20°N) | Anomalía TSM | °C | 0.60 | 0.30 |
| **WHWP** | Western Hemisphere Warm Pool | NOAA PSL | Pacífico y Atlántico Cálido | Área TSM > 28.5°C | $10^6	ext{ km}^2$ | 0.60 | 0.60 |
| **PNA** | Pacific-North American Pattern | NOAA CPC/PSL | Pacífico Norte y Norteamérica | Geopotencial 500 hPa | Estandarizado | 0.60 | 0.60 |
| **SOI** | Southern Oscillation Index | NOAA CPC/PSL | Pacífico Sur (Tahiti vs Darwin) | Diferencia SLP estandarizada | Estandarizado | 0.60 | 0.30 |
| **AMO_CSU** | AMO (Colorado State University) | CSU | Atlántico Norte (0°–60°N) | Anomalía TSM destrended | °C | 0.60 | 0.30 |

---

## 2. Oscilaciones del Pacífico Tropical y ENOS
* **ONI, SSTA_34, SSTA_12, SSTA_3, SSTA_4:** Indicadores térmicos del ciclo El Niño / Oscilación del Sur.
* **MEI:** Índice multivariado que integra campos de presión, viento, temperatura superficial y radiación saliente de onda larga.
* **SOI:** Indicador barométrico de la fluctuación atmosférica de Walker entre Tahiti y Darwin.

---

## 3. Oscilaciones del Atlántico y Mar Caribe
* **AMO / AMO_CSU:** Variabilidad multidecadal de la temperatura superficial del Atlántico Norte con fuerte impacto en la actividad ciclónica tropical del Atlántico y lluvias en Centroamérica.
* **TNA, CAR, AtlTROP, NAtl, SAtl:** Monitorean anomalías térmicas en las principales cuencas atlánticas que modulan la Zona de Convergencia Intertropical (ZCIT) y el ingreso de humedad hacia El Salvador.

---

## 4. Teleconexiones Atmosféricas del Hemisferio Norte y Ártico
* **AO, NAO, PNA:** Patrones de circulación troposférica que condicionan las trayectorias de frentes fríos, dorsales y ondas atmosféricas durante la temporada seca y de transición.

---

## 5. Umbrales Metodológicos Oficiales
Los umbrales predeterminados fueron calibrados empíricamente en la metodología de referencia para equilibrar sensibilidad y especificidad física. En la aplicación pueden modificarse en tiempo de ejecución o restaurarse mediante el módulo de configuración de umbrales.

---

### Navegación

**[← Anterior](manual_usuario.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](referencias.md)**
