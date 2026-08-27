# Documentación Científica y Operacional de los 19 Índices Climáticos



## Contenido

1. [AMO — Atlantic Multidecadal Oscillation (Kaplan SST)](#amo--atlantic-multidecadal-oscillation-kaplan-sst)
2. [AO — Arctic Oscillation](#ao--arctic-oscillation)
3. [MEI — Multivariate ENSO Index (v2)](#mei--multivariate-enso-index-v2)
4. [ONI — Oceanic Niño Index](#oni--oceanic-niño-index)
5. [NAO — North Atlantic Oscillation](#nao--north-atlantic-oscillation)
6. [PDO — Pacific Decadal Oscillation](#pdo--pacific-decadal-oscillation)
7. [TNA — Tropical Northern Atlantic Index](#tna--tropical-northern-atlantic-index)
8. [8–11. Índices de Anomalías Térmicas del Pacífico Ecuatorial (SSTA 1+2, 3, 4, 3.4)](#811-índices-de-anomalías-térmicas-del-pacífico-ecuatorial-ssta-12-3-4-34)
9. [12–14. Índices del Atlántico Tropical y Subtropical (AtlTROP, SAtl, NAtl)](#1214-índices-del-atlántico-tropical-y-subtropical-atltrop-satl-natl)
10. [CAR — Caribbean SST Index](#car--caribbean-sst-index)
11. [WHWP — Western Hemisphere Warm Pool](#whwp--western-hemisphere-warm-pool)
12. [PNA — Pacific-North American Pattern](#pna--pacific-north-american-pattern)
13. [SOI — Southern Oscillation Index](#soi--southern-oscillation-index)
14. [AMO_CSU — AMO Colorado State University](#amo_csu--amo-colorado-state-university)

---
A continuación se detalla la descripción física, cobertura, fuente operacional y citas de los 19 índices implementados en **AAnalogos**.

---

## 1. AMO — Atlantic Multidecadal Oscillation (Kaplan SST)
* **Fenómeno:** Modo dominante de variabilidad multidecadal de la temperatura superficial del mar (TSM) en la cuenca del Atlántico Norte (ciclos de 60–80 años).
* **Región Geográfica:** Atlántico Norte ($0^\circ$ a $70^\circ\text{N}$).
* **Variable y Unidad:** Anomalías de TSM en $^{\circ}\text{C}$ (linealmente destrended).
* **Periodicidad:** Mensual ($1950 - 2023$).
* **Fuente Científica:** Enfield et al. (2001).
* **Fuente Operacional:** NOAA Physical Sciences Laboratory (PSL).
* **URL:** `https://psl.noaa.gov/data/correlation/amon.us.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-99.99`.

---

## 2. AO — Arctic Oscillation
* **Fenómeno:** Patrón anular del Hemisferio Norte que describe el intercambio de masa de aire entre el Ártico y las latitudes medias.
* **Región Geográfica:** $20^\circ\text{N}$ a $90^\circ\text{N}$.
* **Variable y Unidad:** Primera EOF de anomalías de altura geopotencial en 1000 hPa (adimensional / estandarizado).
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Thompson & Wallace (1998).
* **Fuente Operacional:** NOAA Climate Prediction Center (CPC).
* **URL:** `https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.

---

## 3. MEI — Multivariate ENSO Index (v2)
* **Fenómeno:** Índice multivariado que caracteriza el fenómeno El Niño-Oscilación del Sur combinando cinco variables oceánicas y atmosféricas.
* **Región Geográfica:** Pacífico Tropical ($30^\circ\text{S}-30^\circ\text{N}, 100^\circ\text{E}-70^\circ\text{W}$).
* **Variable y Unidad:** EOF combinada de SLP, TSM, vientos zonales/meridionales en superficie y radiación de onda larga (OLR). Estandarizado.
* **Periodicidad:** Bimensual / Mensual ($1950 - 2026$).
* **Fuente Científica:** Wolter & Timlin (2011); Zhang et al. (2019).
* **Fuente Operacional:** NOAA Physical Sciences Laboratory (PSL).
* **URL:** `https://psl.noaa.gov/enso/mei/data/meiv2.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-999.0`.

---

## 4. ONI — Oceanic Niño Index
* **Fenómeno:** Indicador estándar de la NOAA para identificar episodios cálidos (El Niño) y fríos (La Niña).
* **Región Geográfica:** Región Niño 3.4 ($5^\circ\text{N}-5^\circ\text{S}, 120^\circ-170^\circ\text{W}$).
* **Variable y Unidad:** Media móvil trimestral centrada de anomalías de TSM ERSST.v5 en $^{\circ}\text{C}$ con base en períodos climatológicos móviles de 30 años.
* **Periodicidad:** Trimestres móviles mensuales ($1950 - 2026$).
* **Fuente Científica:** Huang et al. (2017).
* **Fuente Operacional:** NOAA Climate Prediction Center (CPC).
* **URL:** `https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.

---

## 5. NAO — North Atlantic Oscillation
* **Fenómeno:** Fluctuación a gran escala en la masa de aire entre la Baja de Islandia y la Alta de las Azores.
* **Región Geográfica:** Atlántico Norte ($20^\circ\text{N}-80^\circ\text{N}$).
* **Variable y Unidad:** Diferencia normalizada de presión a nivel del mar (SLP) / EOF de 500 hPa. Estandarizado.
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Hurrell (1995).
* **Fuente Operacional:** NOAA CPC / PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/nao.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-99.90`.

---

## 6. PDO — Pacific Decadal Oscillation
* **Fenómeno:** Modo dominante de variabilidad decadal de la TSM en el Océano Pacífico extratropical.
* **Región Geográfica:** Pacífico Norte al norte de $20^\circ\text{N}$.
* **Variable y Unidad:** Primera EOF de anomalías de TSM mensuales (con el promedio global sustraído). Estandarizado.
* **Periodicidad:** Mensual ($1946 - 2026$).
* **Fuente Científica:** Mantua et al. (1997); Zhang et al. (1997).
* **Fuente Operacional:** NOAA National Centers for Environmental Information (NCEI).
* **URL:** `https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `99.99`.

---

## 7. TNA — Tropical Northern Atlantic Index
* **Fenómeno:** Anomalías térmicas superficiales en la cuenca del Atlántico Norte Tropical.
* **Región Geográfica:** $5.5^\circ\text{N}$ a $23.5^\circ\text{N}$, $15^\circ\text{W}$ a $57.5^\circ\text{W}$.
* **Variable y Unidad:** Promedio de anomalías de TSM en $^{\circ}\text{C}$ (base 1971–2000).
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Enfield et al. (1999).
* **Fuente Operacional:** NOAA PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/tna.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.30$.
* **Sentinela:** `-99.99`.

---

## 8–11. Índices de Anomalías Térmicas del Pacífico Ecuatorial (SSTA 1+2, 3, 4, 3.4)
* **Fenómeno:** Calentamiento/enfriamiento del Pacífico Ecuatorial asociado a la variabilidad de El Niño / La Niña.
* **Regiones:**
  * **SSTA_12 (Niño 1+2):** $0^\circ-10^\circ\text{S}, 90^\circ\text{W}-80^\circ\text{W}$ (Costa de Sudamérica).
  * **SSTA_3 (Niño 3):** $5^\circ\text{N}-5^\circ\text{S}, 150^\circ\text{W}-90^\circ\text{W}$ (Pacífico Oriental).
  * **SSTA_4 (Niño 4):** $5^\circ\text{N}-5^\circ\text{S}, 160^\circ\text{E}-150^\circ\text{W}$ (Pacífico Occidental/Central).
  * **SSTA_34 (Niño 3.4):** $5^\circ\text{N}-5^\circ\text{S}, 170^\circ\text{W}-120^\circ\text{W}$ (Zona de Acople ENOS).
* **Variable y Unidad:** Anomalías de TSM OISST.v2 en $^{\circ}\text{C}$.
* **Periodicidad:** Mensual ($1982 - 2026$).
* **Fuente Científica:** Reynolds et al. (2002).
* **Fuente Operacional:** NOAA Climate Prediction Center (CPC).
* **URL:** `https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.

---

## 12–14. Índices del Atlántico Tropical y Subtropical (AtlTROP, SAtl, NAtl)
* **Fenómeno:** Gradientes meridionales e interhemisféricos de TSM en el Atlántico que controlan la posición de la ZCIT.
* **Regiones:**
  * **AtlTROP:** $10^\circ\text{S}-10^\circ\text{N}, 0^\circ-360^\circ$.
  * **SAtl:** $0^\circ-20^\circ\text{S}, 30^\circ\text{E}-60^\circ\text{W}$.
  * **NAtl:** $5^\circ\text{N}-20^\circ\text{N}, 30^\circ\text{E}-60^\circ\text{W}$.
* **Variable y Unidad:** Anomalías TSM OISST.v2 en $^{\circ}\text{C}$.
* **Periodicidad:** Mensual ($1982 - 2026$).
* **Fuente Operacional:** NOAA CPC.
* **URL:** `https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.30$.

---

## 15. CAR — Caribbean SST Index
* **Fenómeno:** Variabilidad térmica del Mar Caribe, modulador directo del Chorro de Bajo Nivel del Caribe (CLLJ) y la precipitación en Centroamérica.
* **Región Geográfica:** $10^\circ\text{N}-20^\circ\text{N}, 85^\circ\text{W}-60^\circ\text{W}$.
* **Variable y Unidad:** Anomalía TSM en $^{\circ}\text{C}$.
* **Periodicidad:** Mensual ($1950 - 2020$).
* **Fuente Científica:** Enfield & Alfaro (1999).
* **Fuente Operacional:** NOAA PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/car.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.30$.
* **Sentinela:** `-99.99`.

---

## 16. WHWP — Western Hemisphere Warm Pool
* **Fenómeno:** Masa de agua cálida ($>28.5^\circ\text{C}$) en el Pacífico Oriental Tropical, Golfo de México, Mar Caribe y Atlántico Tropical.
* **Variable y Unidad:** Anomalía de área de la piscina cálida ($10^6\text{ km}^2$).
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Wang & Enfield (2001).
* **Fuente Operacional:** NOAA PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/whwp.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-99.99`.

---

## 17. PNA — Pacific-North American Pattern
* **Fenómeno:** Patrón de teleconexión atmosférica que comunica anomalías del Pacífico Tropical y Norte hacia Norteamérica y el Caribe.
* **Región Geográfica:** Pacífico Norte y Norteamérica.
* **Variable y Unidad:** EOF de altura geopotencial en 500 hPa. Estandarizado.
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Wallace & Gutzler (1981).
* **Fuente Operacional:** NOAA CPC / PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/pna.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-99.90`.

---

## 18. SOI — Southern Oscillation Index
* **Fenómeno:** Componente atmosférica del fenómeno ENOS, basada en el gradiente bárico interoceánico del Pacífico Sur.
* **Región Geográfica:** Tahití (Polinesia Francesa) vs Darwin (Australia).
* **Variable y Unidad:** Diferencia normalizada de presión a nivel del mar (Tahití - Darwin). Estandarizado.
* **Periodicidad:** Mensual ($1953 - 2021$).
* **Fuente Científica:** Troup (1965); Trenberth (1984).
* **Fuente Operacional:** NOAA CPC / PSL.
* **URL:** `https://psl.noaa.gov/data/correlation/soi.data`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.
* **Sentinela:** `-999.0`.

---

## 19. AMO_CSU — AMO Colorado State University
* **Fenómeno:** Variante del índice AMO calculada por el Tropical Meteorology Project de la Universidad Estatal de Colorado con remoción de tendencia polinomial.
* **Región Geográfica:** Atlántico Norte ($0^\circ-60^\circ\text{N}, 80^\circ\text{W}-0^\circ$).
* **Variable y Unidad:** Anomalía TSM filtrada ($^{\circ}\text{C}$).
* **Periodicidad:** Mensual ($1950 - 2026$).
* **Fuente Científica:** Klotzbach & Gray (2008).
* **Fuente Operacional:** Colorado State University (CSU).
* **URL:** `https://tropical.colostate.edu/amo.html`
* **Umbrales:** $r > 0.60$, $\text{MAD} < 0.60$.

---

### Navegación

**[← Anterior](validacion_climatologica.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](referencias.md)**
