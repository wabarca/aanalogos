# Directorio de Datos Históricos de Índices Climáticos

Este directorio almacena las series temporales de las 19 oscilaciones climáticas utilizadas por **AAnalogos**.

## Estructura de Archivos

Cada índice se almacena como una matriz mensual estructurada con encabezado estándar:
`YEAR,ENE,FEB,MAR,ABR,MAY,JUN,JUL,AGO,SET,OCT,NOV,DIC`

| Código | Archivo CSV | Fuente Oficial | Cobertura |
| :--- | :--- | :--- | :---: |
| **AMO** | `dataAMO.csv` | NOAA PSL (Kaplan SST) | 1950–2023 |
| **AO** | `dataAO.csv` | NOAA CPC (Height 1000 hPa) | 1950–2026 |
| **MEI** | `dataMEI_2.csv` | NOAA PSL (MEI v2) | 1950–2026 |
| **ONI** | `dataONI.csv` | NOAA CPC (ERSSTv5) | 1950–2026 |
| **NAO** | `dataNAO.csv` | NOAA CPC / PSL | 1950–2026 |
| **PDO** | `dataPDO.csv` | NOAA NCEI (ERSSTv5) | 1946–2026 |
| **TNA** | `dataTNA.csv` | NOAA PSL | 1950–2026 |
| **SSTA_12** | `dataSSTA_12.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **SSTA_3** | `dataSSTA_3.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **SSTA_4** | `dataSSTA_4.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **SSTA_34** | `dataSSTA_34.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **AtlTROP** | `dataAtlTROP.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **SAtl** | `dataSAtl.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **NAtl** | `dataNAtl.csv` | NOAA CPC (OISSTv2) | 1982–2026 |
| **CAR** | `dataCAR.csv` | NOAA PSL | 1950–2020 |
| **WHWP** | `dataWHWP.csv` | NOAA PSL | 1950–2026 |
| **PNA** | `dataPNA.csv` | NOAA CPC / PSL | 1950–2026 |
| **SOI** | `dataSOI.csv` | NOAA CPC / PSL | 1953–2021 |
| **AMO_CSU** | `dataAMO_CSU.csv` | Colorado State University | 1950–2026 |

## Control de Calidad y Sentinelas

El motor sanitiza automáticamente valores sentinela (`-99.99`, `-99.90`, `99.99`, `-999.0`) convirtiéndolos a `NaN`.
Cualquier ventana semestral con valores `NaN` es invalidada antes del cálculo estadístico.

## Actualización

Para actualizar las series desde sus fuentes remotas, ejecute:
```bash
python scripts/download_data.py
python scripts/audit_sources.py
```
