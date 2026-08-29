# Informe de Validación Climatológica y Regresión Numérica

## Contenido

1. [Marco de Validación y Regresión Científica](#1-marco-de-validación-y-regresión-científica)
2. [Benchmark Oficial: 2015 / Octubre / AMO + PDO + TNA](#2-benchmark-oficial-2015--octubre--amo--pdo--tna)
3. [Preservación del Algoritmo y Extensiones Operacionales](#3-preservación-del-algoritmo-y-extensiones-operacionales)
4. [Validación de Ventanas Operacionales (12 meses)](#4-validación-de-ventanas-operacionales-12-meses)
5. [Aislamiento de Look-Ahead Bias y Modos de Reanálisis](#5-aislamiento-de-look-ahead-bias-y-modos-de-reanálisis)
6. [Resumen de la Suite Automatizada](#6-resumen-de-la-suite-automatizada)

---

## 1. Marco de Validación y Regresión Científica

El sistema `aanalogos` ha sido sometido a auditorías científicas y pruebas de regresión automatizadas para certificar que cualquier extensión de la interfaz, catalogación o actualización de datos conserve con exactitud la física del cálculo validado.

---

## 2. Benchmark Oficial: 2015 / Octubre / AMO + PDO + TNA

* **Año Objetivo ($Y_{\text{obj}}$):** 2015
* **Mes Objetivo ($m_{\text{obj}}$):** 10 (Octubre)
* **Oscilaciones Evaluadas:** `AMO`, `PDO`, `TNA`
* **Longitud de Ventana:** 6 meses (Mayo a Octubre)
* **Años Candidatos Evaluados:** 72
* **Evaluaciones Totales Índice-Año:** 216
* **TOP 7 Años Análogos Identificados:**
  $$\mathbf{2021, 2014, 2012, 2003, 2001, 1990, 1957} \quad (\text{Total} = 2)$$
* **Paridad Matemática:** **100.00 %** respecto a la línea base certificada.

---

## 3. Preservación del Algoritmo y Extensiones Operacionales

La formulación matemática fundamental de similitud, incluyendo la correlación de Pearson, la distancia absoluta media (MAD), el tratamiento de valores faltantes, la exclusión del año objetivo y los criterios históricos de coincidencia, se preserva respecto al benchmark validado. La aplicación incorpora extensiones operacionales explícitas, particularmente una ventana retrospectiva de doce meses y mecanismos de actualización y determinación automática del período disponible.

---

## 4. Validación de Ventanas Operacionales (12 meses)

Se certificó la generalización paramétrica de la ventana de 12 meses en todos los casos de cruce interanual:
* **Enero ($m=1$):** Febrero a Diciembre de $Y-1$ ($11$ meses) $+$ Enero de $Y$ ($1$ mes).
* **Febrero ($m=2$):** Marzo a Diciembre de $Y-1$ ($10$ meses) $+$ Enero a Febrero de $Y$ ($2$ meses).
* **Octubre ($m=10$):** Noviembre a Diciembre de $Y-1$ ($2$ meses) $+$ Enero a Octubre de $Y$ ($10$ meses).
* **Diciembre ($m=12$):** Enero a Diciembre de $Y$ ($12$ meses del mismo año).

---

## 5. Aislamiento de Look-Ahead Bias y Modos de Reanálisis

* **Reanálisis Retrospectivo Completo:** $Y_{\text{cand}} \neq Y_{\text{obj}}$, compara frente a todo el registro histórico disponible.
* **Backtesting Estricto:** $Y_{\text{cand}} \le Y_{\text{obj}}$ y $Y_{\text{cand}} \neq Y_{\text{obj}}$, cortando temporalmente cualquier dato posterior al año analizado.

---

## 6. Resumen de la Suite Automatizada

La suite `tests/` ejecuta **23 pruebas unitarias** con **100% de éxito**:
* Regresión y Benchmark Oficial (`test_regression.py`).
* Ventanas de 6 y 12 meses (`test_windows.py`, `test_operational_windows.py`).
* Look-Ahead Bias y Reanálisis (`test_reanalysis_lookahead.py`).
* Calidad, Sentinelas, Exclusión de $Y_{\text{obj}}$ y float64 (`test_validation.py`).
* Determinación de Fecha Operacional (`test_operational_date.py`).
* Umbrales y Catálogo (`test_thresholds_config.py`, `test_catalog_integrity.py`).

---

### Navegación

**[← Anterior](manual_usuario.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](indices.md)**
