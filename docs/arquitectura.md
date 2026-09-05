# Arquitectura Técnica del Software AAnalogos

## Contenido

1. [Visión General de la Arquitectura](#1-visión-general-de-la-arquitectura)
2. [Capas del Sistema](#2-capas-del-sistema)
3. [Motor Climatológico Modular (`aanalogos/`)](#3-motor-climatológico-modular-aanalogos)
4. [Catálogo y Gestión de Datos](#4-catálogo-y-gestión-de-datos)
5. [Capa de Presentación Web (Streamlit `app.py`)](#5-capa-de-presentación-web-streamlit-apppy)
6. [Suite de Pruebas Automatizadas (`tests/`)](#6-suite-de-pruebas-automatizadas-tests)

---

## 1. Visión General de la Arquitectura

```text
┌─────────────────────────────────────────────────────────────┐
│                    app.py (Streamlit UI)                    │
│ ├── 🌦️ Análisis (Operacional & Reanálisis Histórico)       │
│ ├── 📊 Explorador de Índices (Fichas Técnicas & Series)      │
│ ├── 📚 Metodología Interactiva                              │
│ ├── 📈 Estado y Actualización de Series Climáticas          │
│ └── ⚙️ Configuración y Calibración de Umbrales              │
└──────────────────────────────┬──────────────────────────────┘
                               │ Consume API Pública
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              aanalogos/ (Motor Climatológico)                │
│ ├── engine.py     → Orquestador de Años Análogos            │
│ ├── catalog.py    → Diagnóstico de fuentes y fechas op.     │
│ ├── windows.py    → Ventanas móviles (12m / 6m / Cruce año) │
│ ├── metrics.py    → Pearson float64 y MAD                   │
│ ├── quality.py    → Aislamiento de sentinelas y limpieza    │
│ ├── data.py       → Carga, parsing y actualización segura   │
│ ├── results.py    → Dataclasses de resultados y trazabilidad│
│ └── config.py     → Constantes y umbrales metodológicos     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Lee / Escribe
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ ├── data/ (Archivos CSV de las 19 series climáticas)        │
│ └── config/data_sources.yaml (Catálogo estructurado YAML)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Capas del Sistema

1. **Capa de Datos:** Repositorio local de matrices mensuales en `data/` y manifiesto estructurado `config/data_sources.yaml`.
2. **Capa de Negocio (Motor Científico):** Módulos en `aanalogos/` que procesan las series, extraen ventanas, calculan correlaciones y construyen rankings.
3. **Capa de Presentación:** Aplicación Streamlit en `app.py` organizada en 5 secciones modulares.
4. **Capa de Infraestructura:** Scripts de despliegue en `deploy/` y servicio continuo `systemd`.

---

## 3. Motor Climatológico Modular (`aanalogos/`)

* **`engine.py`:** Expone `calcular_analogos()`, orquestando la validación estricta de cobertura, intersección de años candidatos, cálculo de métricas y ranking.
* **`windows.py`:** Implementa la extracción continua de ventanas de $N$ meses ($N=12$ operacional, $N=6$ metodológico) generalizando cruces interanuales.
* **`catalog.py`:** Determina fechas operacionales disponibles y compila la tabla de salud de fuentes.
* **`data.py`:** Gestiona la carga y actualización segura de series, con validación estructural previa antes del reemplazo atómico de archivos locales.

---

## 4. Catálogo y Gestión de Datos

La configuración de metadatos de las 19 series climáticas reside en `config/data_sources.yaml`, manteniendo una **única fuente estructurada de verdad** para nombres, regiones, variables, unidades, fuentes operacionales y DOIs.

---

## 5. Capa de Presentación Web (Streamlit `app.py`)

Implementa reactividad mediante `st.session_state` y optimización de rendimiento con `st.cache_resource` y `st.cache_data`.

---

## 6. Suite de Pruebas Automatizadas (`tests/`)

* `test_regression.py`: Benchmark oficial 2015/10/AMO+PDO+TNA (100% de paridad matemática).
* `test_operational_windows.py`: Validación de ventanas de 12 meses en todos los meses del año.
* `test_reanalysis_lookahead.py`: Verificación de aislamiento estricto de datos posteriores en reanálisis.
* `test_operational_date.py`: Determinación dinámica del año actual y mes operacional.
* `test_thresholds_config.py`: Aplicación y restauración de umbrales personalizados.
* `test_catalog_integrity.py`: Cobertura completa de los 19 índices en el catálogo.
* `test_validation.py`, `test_windows.py`, `test_invariance.py`, `test_multi_cases.py`: Suite base de 9 pruebas científicas.

---

### Navegación

**[← Anterior](referencias.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](reproducibilidad.md)**
