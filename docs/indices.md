# Catálogo de Índices y Oscilaciones Climáticas

## Contenido

1. [Inventario Maestro de las 22 Series Climáticas](#1-inventario-maestro-de-las-22-series-climáticas)
2. [Auditoría de Variables y Selección de Anomalías](#2-auditoría-de-variables-y-selección-de-anomalías)
3. [Fichas Estructuradas por Índice](#3-fichas-estructuradas-por-índice)
   * [3.1 Familia ENSO (Pacífico Tropical)](#31-familia-enso-pacífico-tropical)
   * [3.2 Regiones Térmicas del Pacífico (SSTA)](#32-regiones-térmicas-del-pacífico-ssta)
   * [3.3 Cuencas del Atlántico y Mar Caribe](#33-cuencas-del-atlántico-y-mar-caribe)
   * [3.4 Teleconexiones Atmosféricas del Hemisferio Norte y Ártico](#34-teleconexiones-atmosféricas-del-hemisferio-norte-y-ártico)
4. [Umbrales Metodológicos Oficiales](#4-umbrales-metodológicos-oficiales)

---

## 1. Inventario Maestro de las 22 Series Climáticas

El sistema **AAnalogos** integra 22 series climáticas operacionales con identificación inequívoca de la variable exacta utilizada en los cálculos matemáticos:

| Código | Nombre Científico | Institución | Tipo de Variable | Variable en Motor | Columna Fuente | Unidades | $r_{\text{umbral}}$ | $\text{MAD}_{\text{umbral}}$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **AMO** | Atlantic Multidecadal Oscillation | NOAA PSL | Anomalía | Anomalía mensual TSM desestacionalizada y sin tendencia | Matriz ENE..DIC | °C | 0.60 | 0.30 |
| **AO** | Arctic Oscillation | NOAA CPC | Índice estandarizado | Anomalía geopotencial 1000 hPa estandarizada | Matriz ENE..DIC | Estandarizado | 0.40 | 1.00 |
| **MEI** | Multivariate ENSO Index v2 | NOAA PSL | Índice estandarizado | Combinación multivariada EOF estandarizada | Matriz ENE..DIC | Estandarizado | 0.40 | 0.50 |
| **ONI** | Oceanic Niño Index (Estándar) | NOAA CPC | Anomalía | Media móvil trimestral anomalía TSM Niño 3.4 | Medias DJF..NDJ | °C | 0.60 | 0.60 |
| **ONIv5** | Oceanic Niño Index (ERSSTv5) | NOAA CPC | Anomalía | Media trimestral anomalía TSM basada en ERSSTv5 | Medias DJF..NDJ | °C | 0.60 | 0.60 |
| **ONIv6** | Oceanic Niño Index (ERSSTv6) | NOAA CPC | Anomalía | Media trimestral anomalía TSM basada en ERSSTv6 | Medias DJF..NDJ | °C | 0.60 | 0.60 |
| **RONI** | Relative Oceanic Niño Index | NOAA CPC | Índice derivado | Anomalía relativa Niño 3.4 ajustada por fondo tropical | Medias DJF..NDJ | °C | 0.60 | 0.60 |
| **NAO** | North Atlantic Oscillation | NOAA CPC/PSL | Índice estandarizado | Diferencia normalizada de presión a nivel del mar | Matriz ENE..DIC | Estandarizado | 0.60 | 0.80 |
| **PDO** | Pacific Decadal Oscillation | NOAA NCEI/PSL | Índice estandarizado | Serie temporal de componente principal EOF1 TSM | Matriz ENE..DIC | Estandarizado | 0.40 | 0.60 |
| **TNA** | Tropical Northern Atlantic | NOAA PSL | Anomalía | Anomalía mensual promedio de TSM cuenca tropical | Matriz ENE..DIC | °C | 0.50 | 0.30 |
| **SSTA_12** | Niño 1+2 SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM1+2` | °C | 0.60 | 0.60 |
| **SSTA_3** | Niño 3 SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM3` | °C | 0.50 | 0.70 |
| **SSTA_4** | Niño 4 SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM4` | °C | 0.38 | 0.70 |
| **SSTA_34** | Niño 3.4 SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM3.4` | °C | 0.60 | 0.60 |
| **AtlTROP** | Tropical Atlantic SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM_TROP` | °C | 0.60 | 0.60 |
| **SAtl** | South Atlantic SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM_SAtl` | °C | 0.60 | 0.60 |
| **NAtl** | North Atlantic SST Anomaly | NOAA CPC | Anomalía | Anomalía mensual observada de TSM | `ANOM_NAtl` | °C | 0.60 | 0.60 |
| **CAR** | Caribbean SST Index | NOAA PSL | Anomalía | Anomalía mensual promedio TSM Mar Caribe | Matriz ENE..DIC | °C | 0.60 | 0.60 |
| **WHWP** | Western Hemisphere Warm Pool | NOAA PSL | Anomalía | Anomalía de área oceánica con TSM > 28.5 °C | Matriz ENE..DIC | $10^6\text{ km}^2$ | 0.60 | 0.60 |
| **PNA** | Pacific-North American Pattern | NOAA CPC/PSL | Índice estandarizado | Patrón de teleconexión geopotencial en 500 hPa | Matriz ENE..DIC | Estandarizado | 0.60 | 0.60 |
| **SOI** | Southern Oscillation Index | NOAA CPC/PSL | Índice estandarizado | Diferencia estandarizada de presión Tahití–Darwin | Matriz ENE..DIC | Estandarizado | 0.60 | 0.30 |
| **AMO_CSU** | AMO (Colorado State Univ.) | CSU TMP | Anomalía | Anomalía mensual TSM según formulación CSU | Matriz ENE..DIC | °C | 0.60 | 0.30 |

---

## 2. Auditoría de Variables y Selección de Anomalías

> [!IMPORTANT]
> **Regla Científica Fundamental de Entrada:**  
> El motor climatológico de años análogos opera **exclusivamente sobre anomalías publicadas o índices normalizados**. En ningún caso se utilizan valores físicos absolutos (como temperaturas en grados absolutos de 20 a 30 °C).

### Auditoría de Series SST Compuestas (`sstoi.indices` y `sstoi.atl.indices`):
Las fuentes oficiales de NOAA CPC publican matrices multivariable con columnas de temperatura superficial absoluta (°C) y anomalía térmica (°C). El módulo de procesamiento `aanalogos/data.py` (`acomodaParaCSV_3`) realiza la discriminación:

* **`SSTA_12`**: Extrae la columna `ANOM1+2` (rango térmico $[-3.0, +4.5]\ ^\circ\text{C}$), descartando la temperatura absoluta `NINO1+2` ($22	ext{--}28\ ^\circ\text{C}$).
* **`SSTA_3`**: Extrae la columna `ANOM3` (rango $[-2.5, +3.8]\ ^\circ\text{C}$), descartando `NINO3` ($24	ext{--}29\ ^\circ\text{C}$).
* **`SSTA_4`**: Extrae la columna `ANOM4` (rango $[-2.0, +2.5]\ ^\circ\text{C}$), descartando `NINO4` ($27	ext{--}30\ ^\circ\text{C}$).
* **`SSTA_34`**: Extrae la columna `ANOM3.4` (rango $[-2.5, +3.2]\ ^\circ\text{C}$), descartando `NINO3.4` ($25	ext{--}29\ ^\circ\text{C}$).
* **`AtlTROP` / `NAtl` / `SAtl`**: Extraen las columnas `ANOM_TROP`, `ANOM_NAtl`, `ANOM_SAtl` de `sstoi.atl.indices`.

---

## 3. Fichas Estructuradas por Índice

### 3.1 Familia ENSO (Pacífico Tropical)

#### ONIv5 — Oceanic Niño Index (ERSSTv5)
* **Identificador interno:** `ONIv5`
* **Nombre completo:** Oceanic Niño Index basado en ERSST versión 5
* **Tipo:** Anomalía térmica trimestral
* **Variable exacta en motor:** Media móvil de 3 meses de la anomalía de TSM en la región Niño 3.4 (5°N–5°S, 120°–170°W) (°C)
* **Columna fuente:** Matriz trimestral `DJF..NDJ`
* **Unidades:** °C
* **Fuente operacional:** NOAA Climate Prediction Center (CPC)
* **URL:** [https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v5/](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v5/)
* **Referencia científica:** Huang, B., Thorne, P. W., et al. (2017). *Extended Reconstructed Sea Surface Temperature, Version 5 (ERSSTv5)*. J. Climate, 30(20), 8179-8205. [DOI: 10.1175/JCLI-D-16-0836.1](https://doi.org/10.1175/JCLI-D-16-0836.1)

#### ONIv6 — Oceanic Niño Index (ERSSTv6)
* **Identificador interno:** `ONIv6`
* **Nombre completo:** Oceanic Niño Index basado en ERSST versión 6
* **Tipo:** Anomalía térmica trimestral
* **Variable exacta en motor:** Media móvil de 3 meses de la anomalía de TSM en la región Niño 3.4 con climatología base centrada (°C)
* **Columna fuente:** Matriz trimestral `DJF..NDJ`
* **Unidades:** °C
* **Fuente operacional:** NOAA Climate Prediction Center (CPC)
* **URL:** [https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/)
* **Referencia científica:** Huang, B., et al. (2025). *Extended Reconstructed Sea Surface Temperature, Version 6 (ERSSTv6): Upgrades and Intercomparisons*. J. Climate, 38(4), 945-965. [DOI: 10.1175/JCLI-D-23-0707.1](https://doi.org/10.1175/JCLI-D-23-0707.1)

#### RONI — Relative Oceanic Niño Index
* **Identificador interno:** `RONI`
* **Nombre completo:** Relative Oceanic Niño Index (ERSSTv6)
* **Tipo:** Índice derivado (Anomalía relativa)
* **Variable exacta en motor:** Media móvil trimestral de la anomalía de TSM en Niño 3.4 restando la anomalía promedio del cinturón tropical global (20°N–20°S) y ajustada por varianza (°C)
* **Columna fuente:** Matriz trimestral `DJF..NDJ`
* **Unidades:** °C
* **Fuente operacional:** NOAA Climate Prediction Center (CPC)
* **URL:** [https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/)
* **Referencia científica:** Van Oldenborgh, G. J., et al. (2021). *Pathways of global warming impacts on ENSO teleconnections*. J. Climate, 34(7), 2633-2647. [DOI: 10.1175/JCLI-D-20-0588.1](https://doi.org/10.1175/JCLI-D-20-0588.1)

#### MEI — Multivariate ENSO Index Version 2
* **Identificador interno:** `MEI`
* **Nombre completo:** Multivariate ENSO Index Version 2
* **Tipo:** Índice estandarizado
* **Variable exacta en motor:** Componente principal EOF1 de seis variables acopladas océano-atmósfera (SLP, SST, vientos $u, v$, OLR)
* **Columna fuente:** Bimensual emparejado a meses
* **Unidades:** Estandarizado (adimensional)
* **Fuente operacional:** NOAA Physical Sciences Laboratory (PSL)
* **URL:** [https://psl.noaa.gov/enso/mei/data/meiv2.data](https://psl.noaa.gov/enso/mei/data/meiv2.data)
* **Referencia científica:** Zhang, T., et al. (2019). *The Multivariate ENSO Index Version 2*. Int. J. Climatol., 39(8), 3467-3482. [DOI: 10.1002/joc.6033](https://doi.org/10.1002/joc.6033)

#### SOI — Southern Oscillation Index
* **Identificador interno:** `SOI`
* **Nombre completo:** Southern Oscillation Index (Troup / Trenberth)
* **Tipo:** Índice estandarizado
* **Variable exacta en motor:** Diferencia estandarizada mensual de presión a nivel del mar entre Tahití y Darwin
* **Columna fuente:** Matriz mensual `ENE..DIC`
* **Unidades:** Estandarizado
* **Fuente operacional:** NOAA CPC / PSL
* **URL:** [https://psl.noaa.gov/data/correlation/soi.data](https://psl.noaa.gov/data/correlation/soi.data)
* **Referencia científica:** Troup, A. J. (1965). *The 'southern oscillation'*. Q. J. R. Meteorol. Soc., 91(390), 490-506. [DOI: 10.1002/qj.49709139009](https://doi.org/10.1002/qj.49709139009)

---

### 3.2 Regiones Térmicas del Pacífico (SSTA)
* **`SSTA_12`**: Niño 1+2 (0°–10°S, 90°–80°W) — Costas de Ecuador y Perú. Anomalía mensual observada de TSM (°C).
* **`SSTA_3`**: Niño 3 (5°N–5°S, 150°W–90°W) — Pacífico Oriental Ecuatorial. Anomalía mensual observada de TSM (°C).
* **`SSTA_4`**: Niño 4 (5°N–5°S, 160°E–150°W) — Pacífico Centro-Occidental. Anomalía mensual observada de TSM (°C).
* **`SSTA_34`**: Niño 3.4 (5°N–5°S, 170°W–120°W) — Región Central ENOS. Anomalía mensual observada de TSM (°C).

---

### 3.3 Cuencas del Atlántico y Mar Caribe
* **`AMO` / `AMO_CSU`**: Atlantic Multidecadal Oscillation — Variabilidad decadal de TSM en el Atlántico Norte (°C).
* **`TNA`**: Tropical Northern Atlantic — Anomalía promedio de TSM (5.5°N–23.5°N, 15°W–57.5°W) (°C).
* **`CAR`**: Caribbean SST Index — Anomalía promedio de TSM en el Mar Caribe (10°N–22°N, 85°W–60°W) (°C).
* **`WHWP`**: Western Hemisphere Warm Pool — Anomalía superficial de agua con TSM > 28.5 °C ($10^6\text{ km}^2$).
* **`AtlTROP`**: Tropical Atlantic SST Anomaly (20°N–20°S) (°C).
* **`NAtl`**: North Atlantic SST Anomaly (5°N–20°N) (°C).
* **`SAtl`**: South Atlantic SST Anomaly (0°–20°S) (°C).

---

### 3.4 Teleconexiones Atmosféricas del Hemisferio Norte y Ártico
* **`AO`**: Arctic Oscillation — Anomalía de geopotencial en 1000 hPa estandarizada.
* **`NAO`**: North Atlantic Oscillation — Dipolo de presión entre Islandia y Azores estandarizado.
* **`PDO`**: Pacific Decadal Oscillation — Primer modo EOF de anomalías de TSM en el Pacífico Norte (> 20°N).
* **`PNA`**: Pacific-North American Pattern — Patrón de geopotencial en 500 hPa estandarizado.

---

## 4. Umbrales Metodológicos Oficiales
Los umbrales predeterminados fueron calibrados empíricamente en la metodología de referencia para equilibrar sensibilidad y especificidad física:

* Oscilaciones térmicas atlánticas de baja frecuencia (AMO, TNA, AMO_CSU): $r \ge 0.50\text{--}0.60$, $\text{MAD} \le 0.30\ ^\circ\text{C}$.
* Índices de anomalía superficial del Pacífico (ONI, ONIv5, ONIv6, RONI, SSTA): $r \ge 0.60$, $\text{MAD} \le 0.60\ ^\circ\text{C}$.
* Teleconexiones barométricas y patrones de onda (AO, NAO, PNA, SOI, PDO): $r \ge 0.40\text{--}0.60$, $\text{MAD} \le 0.60\text{--}1.00$.

---

### Navegación

**[← Anterior: Manual de Usuario](manual_usuario.md)** · **[Índice de Documentación](README.md)** · **[Siguiente: Referencias Científicas →](referencias.md)**
