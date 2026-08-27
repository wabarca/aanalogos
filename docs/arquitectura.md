# Arquitectura Técnica del Software AAnalogos



## Contenido

1. [Diagrama de Arquitectura por Capas](#diagrama-de-arquitectura-por-capas)
2. [Responsabilidades por Módulo](#responsabilidades-por-módulo)
3. [Aislamiento y Estabilidad](#aislamiento-y-estabilidad)

---
El diseño de **AAnalogos** se fundamenta en una arquitectura modular desacoplada por capas (Layered Architecture), garantizando la separación de responsabilidades, la pureza matemática del motor científico y la portabilidad entre interfaces gráficas, líneas de comandos (CLI) o servicios web en red.

---

## 1. Diagrama de Arquitectura por Capas

```
+-------------------------------------------------------------------------------+
|                             CAPA DE PRESENTACIÓN                             |
|  - app.py (Streamlit Web Interface)                                           |
|  - Formateo de decimales a 4 dígitos, alertas visuales y exportación CSV/TXT   |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|                           CAPA DE APLICACIÓN / API                            |
|  - aanalogos.calcular_analogos(...)                                           |
|  - Validación estricta de parámetros y cobertura (cero reducción silenciosa)  |
|  - Estructuración en Dataclasses (ResultadoAnalogos, MetricaDetallada)        |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|                       CAPA CIENTÍFICA Y DE CÁLCULO                            |
|  - aanalogos.windows (Construcción de ventanas semestrales intra/interanual)   |
|  - aanalogos.metrics (Cálculo puro de Pearson r y MAD en float64)             |
|  - aanalogos.quality (Sanitización de sentinelas |x| > 50 -> NaN)              |
|  - aanalogos.config (Umbrales univariados validados por oscilación)          |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|                             CAPA DE DATOS E INGESTA                           |
|  - aanalogos.data (Carga y resolución de rutas en data/ y raíz)               |
|  - config/data_sources.yaml (Manifiesto estructurado de fuentes remotas)      |
|  - scripts/download_data.py (Descarga atómica no destructiva)                 |
|  - scripts/audit_sources.py (Auditoría automatizada de consistencia)          |
+-------------------------------------------------------------------------------+
```

---

## 2. Responsabilidades por Módulo

| Módulo / Archivo | Capa | Responsabilidad Principal |
| :--- | :---: | :--- |
| `app.py` | Presentación | Interfaz gráfica web en Streamlit, controles, gráficos y descargas. |
| `aanalogos/engine.py` | Aplicación | Orquestador del flujo de cálculo. Cero llamadas a `print()`. |
| `aanalogos/results.py` | Aplicación | Definición de estructuras de datos inmutables y exportadores. |
| `aanalogos/windows.py` | Científica | Construcción y etiquetado de ventanas móviles de 6 meses. |
| `aanalogos/metrics.py` | Científica | Cálculo estadístico de $r$, MAD y evaluación booleana de umbrales. |
| `aanalogos/quality.py` | Científica | Limpieza de sentinelas y conversión de tipos a matriz numérica. |
| `aanalogos/config.py` | Científica | Constantes, nombres de meses y diccionario de umbrales ($r$, MAD). |
| `aanalogos/data.py` | Datos | Carga de archivos CSV/TXT desde `data/` o directorio del proyecto. |
| `config/data_sources.yaml`| Datos | Manifiesto declarativo de URLs, instituciones y metadatos. |

---

## 3. Aislamiento y Estabilidad

1. **Independencia de Streamlit:** El paquete `aanalogos` no contiene ninguna importación ni dependencia de Streamlit. Puede importarse en scripts de procesamiento por lotes, notebooks de Jupyter o servicios REST.
2. **Inmutabilidad y Trazabilidad:** Cada cálculo genera una instancia autocontenida de `ResultadoAnalogos` con toda la trazabilidad detallada ($N \times K$ registros) en precisión completa `float64`.

---

### Navegación

**[← Anterior](referencias.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](manual_usuario.md)**
