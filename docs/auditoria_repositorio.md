# Informe de Auditoría Integral del Repositorio (`REPOSITORY_AUDIT.md`)

**Fecha de Auditoría:** 2026-08-27  
**Proyecto:** AAnalogos — Sistema de Selección de Años Análogos Climáticos  
**Institución:** Gerencia de Meteorología, Dirección del Observatorio de Amenazas y Recursos Naturales, MARN, El Salvador  
**Responsable:** William Abarca (wabarca@ambiente.gob.sv)



## Contenido

1. [Alcance de la Auditoría](#alcance-de-la-auditoría)
2. [Inventario y Clasificación de Archivos](#inventario-y-clasificación-de-archivos)
3. [Verificación de Seguridad, Rutas y Portabilidad](#verificación-de-seguridad-rutas-y-portabilidad)
4. [Dictamen de Auditoría](#dictamen-de-auditoría)

---
---

## 1. Alcance de la Auditoría
Se realizó una inspección exhaustiva de todos los directorios, archivos de código fuente, conjuntos de datos climáticos, módulos de empaquetado, scripts operativos, configuraciones, documentación técnica y artefactos temporales.

---

## 2. Inventario y Clasificación de Archivos

### 2.1 Código Fuente y Módulos de la Aplicación (Se Conservan)
* `app.py`: Aplicación web interactiva desarrollada en Streamlit para visualización, control y exportación.
* `aanlogos_v3.py`: Interfaz CLI de compatibilidad por terminal interactiva.
* `aanalogos/`: Paquete modular científico desacoplado:
  * `__init__.py`: API pública del paquete.
  * `engine.py`: Orquestador principal (`calcular_analogos`), sin prints, con validación estricta.
  * `results.py`: Dataclasses inmutables (`ResultadoAnalogos`, `MetricaDetallada`) y exportadores.
  * `data.py`: Ingesta, normalización y resolución automática de rutas en `data/` o directorio raíz.
  * `config.py`: Umbrales de coincidencia ($r$, MAD) y nombres de meses.
  * `quality.py`: Sanitización de sentinelas ($|x| > 50 \to \text{NaN}$) y validación de vectores.
  * `windows.py`: Construcción y etiquetado de ventanas móviles semestrales (intra e interanuales).
  * `metrics.py`: Cálculo estadístico de Pearson ($r$) y distancia $\text{MAD}$ en `float64` nativo.

### 2.2 Conjuntos de Datos Históricos (Se Conservan en `data/`)
* 19 series climáticas almacenadas en `data/` con matrices mensuales normalizadas y respaldadas en formato `.csv` y `.txt`:
  `dataAMO.*`, `dataAO.*`, `dataMEI_2.*`, `dataONI.*`, `dataNAO.*`, `dataPDO.*`, `dataTNA.*`, `dataSSTA_12.*`, `dataSSTA_3.*`, `dataSSTA_4.*`, `dataSSTA_34.*`, `dataAtlTROP.*`, `dataSAtl.*`, `dataNAtl.*`, `dataCAR.*`, `dataWHWP.*`, `dataPNA.*`, `dataSOI.*`, `dataAMO_CSU.*`.

### 2.3 Archivos de Configuración y Despliegue (Se Conservan)
* `config/data_sources.yaml`: Manifiesto declarativo estructurado de metadatos, URLs, variables y sentinelas.
* `deploy/aanalogos.service`: Unidad systemd para ejecución como servicio en servidores Linux.
* `deploy/run_server.sh`: Script ejecutable bash para lanzamiento en red local LAN (`0.0.0.0:8501`).
* `scripts/download_data.py`: Script de descarga segura, no destructiva y con reemplazo atómico.
* `scripts/audit_sources.py`: Script de diagnóstico y auditoría de calidad de datos.

### 2.4 Suite de Pruebas Automatizadas (Se Conserva en `tests/`)
* `tests/__init__.py`
* `tests/test_regression.py`: Prueba de regresión contra el caso oficial 2015/10/AMO+PDO+TNA (72 candidatos, 216 evaluaciones, 100% idéntico).
* `tests/test_invariance.py`: Prueba de invarianza matemática ante shuffle de filas.
* `tests/test_windows.py`: Validación de ventanas retrospectivas de 6 meses (intra e interanuales).
* `tests/test_validation.py`: Validación estricta (rechazo ante índices no disponibles, sentinelas $\to$ NaN, exclusión de año objetivo, float64).
* `tests/test_multi_cases.py`: Validación multi-caso climatológica (7 escenarios históricos).

### 2.5 Archivos Temporales y Salidas de Ejecución (Se Eliminan / Mantienen Fuera de Git)
* **Eliminados:** `Años_Análogos.png`, `Años_Análogos.txt`, `Trazabilidad_Detallada.txt`, `aanalogos.zip`, `tmp/`.
* **Excluidos mediante `.gitignore`:** Cachés de Python (`__pycache__`), entornos virtuales (`.venv`), salidas locales (`outputs/`, `results/`, `*.log`).

---

## 3. Verificación de Seguridad, Rutas y Portabilidad

1. **Credenciales y Secretos:**  
   Búsqueda exhaustiva con expresiones regulares de `password`, `secret`, `token`, `apikey`, `credential`.  
   *Resultado:* **0 credenciales encontradas**. El proyecto no requiere claves privadas ni expone secretos.
2. **Rutas Absolutas y Específicas de Usuario:**  
   Búsqueda de patrones `C:\Users\wabarca`, `/home/wabarca`, `OneDrive`.  
   *Resultado:* **0 rutas fijas en código de producción**. Todo el código utiliza `pathlib.Path` y resolución relativa al directorio del proyecto.
3. **Metadata de Autoría Heredada:**  
   Eliminados encabezados, variables `__author__` y mensajes en consola del código ejecutable. La atribución histórica se mantiene exclusivamente en la documentación institucional.

---

## 4. Dictamen de Auditoría
El repositorio cumple con los estándares institucionales de seguridad, orden, modularidad y portabilidad.

---

### Navegación

**[← Anterior](auditoria_final_cierre.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](informe_preparacion_institucional.md)**
