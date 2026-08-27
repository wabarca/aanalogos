# Registro de Cambios (CHANGELOG)

Todas las modificaciones notables realizadas en el proyecto **AAnalogos** se documentan en este archivo.

---

## [3.1.0] - 2026-08-27 (Fase 3: Documentación, Saneamiento y Despliegue Linux)
### Añadido
- Suite formal de pruebas automatizadas en `tests/` (`test_regression.py`, `test_invariance.py`, `test_windows.py`, `test_validation.py`, `test_multi_cases.py`).
- Manifiesto declarativo estructurado de fuentes en `config/data_sources.yaml`.
- Scripts operacionales en `scripts/` (`download_data.py` y `audit_sources.py`).
- Configuración para despliegue Linux en `deploy/` (`aanalogos.service` y `run_server.sh` con binding `0.0.0.0:8501`).
- Documentación completa en `docs/` (11 documentos científicos, técnicos y operacionales).
- `.gitignore` profesional para Python, Streamlit, OS e IDEs.
- `requirements.txt` y `pyproject.toml` para empaquetado estándar.

---

## [3.0.0] - 2026-08-27 (Fase 2: Motor Modular y Aplicación Streamlit)
### Añadido
- Paquete modular `aanalogos/` (`engine.py`, `results.py`, `data.py`, `config.py`, `quality.py`, `windows.py`, `metrics.py`).
- Aplicación interactiva `app.py` en Streamlit con visualizaciones climatológicas, trazabilidad mensual y exportación CSV/TXT.
- Preservación de precisión flotante completa `float64` en el motor de cálculo.
- Validación estricta de índices solicitados con rechazo explícito ante falta de cobertura (cero reducción silenciosa).

---

## [2.0.0] - 2026-08-27 (Fase 1: Auditoría y Corrección Metodológica)
### Corregido
- Alineación estricta por `YEAR` eliminando dependencias de orden de filas `iloc` (corrección del desfase de 4 años en PDO).
- Aislamiento total de sentinelas (`-99.99`, `99.99`, `-999.0` $	o$ `NaN`) evitando su entrada a correlaciones.
- Exclusión formal del año objetivo ($Y_{\text{obj}}$) del universo de candidatos.
- Corrección de ventanas móviles retrospectivas de 6 meses interanuales ($m < 6$) etiquetadas al año de cierre $t$.
