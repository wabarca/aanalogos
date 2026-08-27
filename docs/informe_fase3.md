# Informe de Entrega — Fase 3: Documentación, Saneamiento y Preparación para Despliegue Linux



## Contenido

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Archivos Creados y Organizados](#archivos-creados-y-organizados)
3. [Resultados de Pruebas de Regresión](#resultados-de-pruebas-de-regresión)

---
---

## 1. Resumen Ejecutivo
Se ha completado la Fase 3 del proyecto **AAnalogos**, transformando el código en un repositorio institucional, modular, reproducible, completamente documentado y listo para despliegue en servidores Linux accesibles en red local (LAN), conservando con **cero alteraciones** la formulación matemática validada.

---

## 2. Archivos Creados y Organizados

### Documentación (`docs/`)
1. [`docs/metodologia.md`](metodologia.md): Fundamento científico, ventanas de 6 meses, Pearson, MAD y limitaciones.
2. [`docs/indices.md`](indices.md): Fichas científicas y operacionales de los 19 índices climáticos.
3. [`docs/referencias.md`](referencias.md): Citas bibliográficas primarias con DOIs y fuentes institucionales.
4. [`docs/manual_usuario.md`](manual_usuario.md): Guía paso a paso de uso de la interfaz web Streamlit.
5. [`docs/arquitectura.md`](arquitectura.md): Arquitectura de software en capas desacopladas.
6. [`docs/instalacion_linux.md`](instalacion_linux.md): Instalación, firewall y configuración en Ubuntu/Debian.
7. [`docs/instalacion_windows.md`](instalacion_windows.md): Instalación en Windows 10/11.
8. [`docs/mantenimiento.md`](mantenimiento.md): Tareas de mantenimiento periódico, actualización y logs.
9. [`docs/reproducibilidad.md`](reproducibilidad.md): Protocolo de reproducibilidad y benchmark 2015/10/AMO+PDO+TNA.
10. [`docs/auditoria.md`](auditoria.md): Síntesis de auditorías de Fases 1 y 2.
11. [`docs/informe_fase3.md`](informe_fase3.md): Informe de entrega de la Fase 3.

### Configuración, Datos y Despliegue
* [`config/data_sources.yaml`](../config/data_sources.yaml): Manifiesto estructurado de las 19 series climáticas.
* [`data/README.md`](../data/README.md): Descripción del directorio de datos y formatos.
* [`deploy/aanalogos.service`](../deploy/aanalogos.service): Unidad systemd para ejecución como servicio Linux.
* [`deploy/run_server.sh`](../deploy/run_server.sh): Script de arranque en red local (`0.0.0.0:8501`).
* [`scripts/download_data.py`](../scripts/download_data.py): Descarga automatizada y no destructiva.
* [`scripts/audit_sources.py`](../scripts/audit_sources.py): Auditoría automatizada de series temporales.
* [`tests/`](../tests/): Suite formal de 9 pruebas automatizadas (`test_regression.py`, `test_invariance.py`, `test_windows.py`, `test_validation.py`, `test_multi_cases.py`).
* [`.gitignore`](../.gitignore), [`requirements.txt`](../requirements.txt), [`pyproject.toml`](../pyproject.toml), [`CHANGELOG.md`](../CHANGELOG.md), [`README.md`](../README.md).

---

## 3. Resultados de Pruebas de Regresión
* **Total de Pruebas Ejecutadas:** 9
* **Estado:** **100% OK**
* **Benchmark 2015/10 (AMO+PDO+TNA):** 72 candidatos evaluados, Top 7 idéntico (2021, 2014, 2012, 2003, 2001, 1990, 1957 con Total=2).
