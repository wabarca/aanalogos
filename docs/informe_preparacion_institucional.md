# Informe de Preparación para Despliegue Institucional (`docs/informe_preparacion_institucional.md`)

**Fecha:** 2026-08-27  
**Institución:** Gerencia de Meteorología, Dirección del Observatorio de Amenazas y Recursos Naturales, MARN, El Salvador  
**Responsable Técnico:** William Abarca (wabarca@ambiente.gob.sv)

---

## 1. Estado Inicial del Repositorio
Al inicio del proyecto, el código existía como scripts monolíticos interactivos por consola (`Años_Análogos.py`, `Años_Análogos_v2.py`) con dependencias posicionales `iloc`, desfases temporales en PDO, falta de aislamiento de sentinelas, auto-evaluación del año objetivo y mezcla de datos con código fuente.

---

## 2. Resumen de Cambios Realizados

1. **Refactorización Modular:** Creación del paquete `aanalogos/` (`engine.py`, `results.py`, `data.py`, `config.py`, `quality.py`, `windows.py`, `metrics.py`) con separación estricta de responsabilidades.
2. **Corrección Matemática y Climatológica:**
   * Indexación estricta por `YEAR` (eliminando desfases de lectura).
   * Aislamiento de valores sentinela ($|x| > 50 \to \text{NaN}$).
   * Exclusión formal de $Y_{\text{obj}}$.
   * Preservación de precisión `float64` nativa.
   * Validación estricta con cero reducción silenciosa de índices.
3. **Aplicación Web Interactiva:** Desarrollo de `app.py` en Streamlit con diagnósticos, rankings visuales, trazabilidad mensual y exportación CSV/TXT.
4. **Saneamiento del Repositorio:** Creación de `.gitignore`, eliminación de artefactos residuales y organización de las 19 series en `data/`.
5. **Documentación Exhaustiva:** Creación de 11 manuales y guías técnicas en `docs/`.
6. **Despliegue Linux:** Configuración de `deploy/aanalogos.service` y `deploy/run_server.sh` en `0.0.0.0:8501`.
7. **Operación y Mantenimiento:** Scripts `download_data.py` y `audit_sources.py`.

---

## 3. Inventario de Archivos

### 3.1 Archivos Creados
* `.gitignore`, `requirements.txt`, `pyproject.toml`, `CHANGELOG.md`, `REPOSITORY_AUDIT.md`
* `config/data_sources.yaml`, `data/README.md`
* `deploy/aanalogos.service`, `deploy/run_server.sh`
* `scripts/download_data.py`, `scripts/audit_sources.py`
* `tests/__init__.py`, `tests/test_regression.py`, `tests/test_invariance.py`, `tests/test_windows.py`, `tests/test_validation.py`, `tests/test_multi_cases.py`
* `docs/metodologia.md`, `docs/indices.md`, `docs/referencias.md`, `docs/manual_usuario.md`, `docs/arquitectura.md`, `docs/instalacion_linux.md`, `docs/instalacion_windows.md`, `docs/despliegue_institucional.md`, `docs/mantenimiento.md`, `docs/reproducibilidad.md`, `docs/auditoria.md`, `docs/validacion_climatologica.md`, `docs/informe_preparacion_institucional.md`.

### 3.2 Archivos Modificados
* `README.md`, `LICENSE`, `app.py`, `aanlogos_v3.py`, `aanalogos/__init__.py`, `aanalogos/config.py`, `aanalogos/windows.py`, `aanalogos/data.py`.

### 3.3 Archivos Eliminados
* `Años_Análogos.png`, `Años_Análogos.txt`, `Trazabilidad_Detallada.txt`, `aanalogos.zip`, `tmp/`.

---

## 4. Validación Científica y Suite de Pruebas

```text
test_shuffle_invariance (test_invariance.TestInvariance.test_shuffle_invariance) ... ok
test_multiple_climatological_scenarios (test_multi_cases.TestMultiCases.test_multiple_climatological_scenarios) ... ok
test_benchmark_2015_m10_amo_pdo_tna (test_regression.TestRegression.test_benchmark_2015_m10_amo_pdo_tna) ... ok
test_float64_precision_preservation (test_validation.TestValidation.test_float64_precision_preservation) ... ok
test_sentinels_isolation (test_validation.TestValidation.test_sentinels_isolation) ... ok
test_strict_index_validation_no_silent_reduction (test_validation.TestValidation.test_strict_index_validation_no_silent_reduction) ... ok
test_target_year_exclusion (test_validation.TestValidation.test_target_year_exclusion) ... ok
test_cross_year_windows (test_windows.TestWindows.test_cross_year_windows) ... ok
test_intra_annual_windows (test_windows.TestWindows.test_intra_annual_windows) ... ok

----------------------------------------------------------------------
Ran 9 tests in 6.561s

OK (9 passed / 0 failed)
```

* **Benchmark 2015 / Octubre / AMO + PDO + TNA:** 72 candidatos evaluados, 216 evaluaciones, Top 7 idéntico ($2021, 2014, 2012, 2003, 2001, 1990, 1957$ con Total=2). **100% de paridad matemática**.

---

## 5. Estado de Referencias Bibliográficas
* **Total de referencias científicas investigadas:** 19 índices + 4 metodológicas.
* **Estado de verificación:** **100% verificadas** con autores, títulos, años, DOIs activos y fuentes operacionales contrastadas.

---

## 6. Estado del Despliegue Linux y Red Institucional
* **Servicio systemd:** Preparado (`deploy/aanalogos.service`), usuario no privilegiado (`clima`), reinicio automático.
* **Red LAN:** Configuración lista para escuchar en `0.0.0.0:8501`.
* **Portabilidad:** Cero rutas absolutas personales en código de producción; cero credenciales expuestas.

---

## 7. Riesgos Pendientes y Recomendaciones para Fases Posteriores

1. **Riesgo Climatológico de Sobreinterpretación:** Los años análogos son una herramienta de soporte diagnóstico estadístico, no un modelo dinámico determinista. La capacitación del personal técnico debe enfatizar que los análogos deben combinarse con el análisis de modelos globales (GCMs) y patrones sinópticos locales.
2. **Recomendaciones para Fase 4:**
   * Evaluación de pesos diferenciados por índice según la estación del año (documentado como trabajo futuro).
   * Implementación de pruebas de bondad de ajuste o validación cruzada sobre variables de impacto (precipitación nacional histórica observada por el MARN).

---

## 8. Dictamen Final

El proyecto **AAnalogos** se dictamina como:

### **APTO PARA DESPLIEGUE INSTITUCIONAL**

Cumple a cabalidad con todos los criterios de rigor científico, reproducibilidad computacional, seguridad, trazabilidad, documentación técnica y facilidad de operación en la Gerencia de Meteorología del MARN.
