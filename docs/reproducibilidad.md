# Protocolo de Reproducibilidad Científica y Benchmark de Referencia



## Contenido

1. [Caso de Referencia Certificado (Benchmark)](#caso-de-referencia-certificado-benchmark)
2. [Resultados Numéricos Esperados](#resultados-numéricos-esperados)
3. [Comando Automatizado de Verificación de Reproducibilidad](#comando-automatizado-de-verificación-de-reproducibilidad)

---
Este protocolo permite a cualquier investigador o técnico verificar de forma independiente y exacta la reproducibilidad matemática de **AAnalogos**.

---

## 1. Caso de Referencia Certificado (Benchmark)

* **Año Objetivo ($Y_{\text{obj}}$):** `2015`
* **Mes Objetivo ($m_{\text{obj}}$):** `10` (Octubre)
* **Oscilaciones Evaluadas:** `AMO`, `PDO`, `TNA`

### Parámetros de Entrada
* **Ventana Temporal Construida:** $\mathbf{x}_{\text{target}} = [\text{MAY}(2015), \text{JUN}(2015), \text{JUL}(2015), \text{AGO}(2015), \text{SET}(2015), \text{OCT}(2015)]$
* **Años Históricos Evaluados en $\mathcal{H}_{\text{común}}$:** Exactamente **72 años** ($1950..2022 \setminus \{2015\}$).

---

## 2. Resultados Numéricos Esperados

### Ranking TOP 10 de Años Análogos
| Posición | Año Análogo | Coincidencias AMO | Coincidencias PDO | Coincidencias TNA | Total Coincidencias |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **2021** | 1 | 1 | 0 | **2** |
| **2** | **2014** | 1 | 1 | 0 | **2** |
| **3** | **2012** | 1 | 1 | 0 | **2** |
| **4** | **2003** | 1 | 1 | 0 | **2** |
| **5** | **2001** | 1 | 1 | 0 | **2** |
| **6** | **1990** | 1 | 1 | 0 | **2** |
| **7** | **1957** | 1 | 1 | 0 | **2** |
| **8** | **2022** | 0 | 1 | 0 | **1** |
| **9** | **2018** | 0 | 1 | 0 | **1** |
| **10** | **2017** | 0 | 1 | 0 | **1** |

### Métricas de Trazabilidad para el Año 1957
| Índice | Pearson ($r$) Obtenido | Umbral $r$ | MAD Obtenido | Umbral MAD | ¿Coincide? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AMO** | `0.8322` | $> 0.60$ | `0.0868` | $< 0.60$ | **1 (SÍ)** |
| **PDO** | `0.6445` | $> 0.60$ | `0.5517` | $< 0.60$ | **1 (SÍ)** |
| **TNA** | `0.7439` | $> 0.60$ | `0.3367` | $< 0.30$ | **0 (NO: MAD excede 0.30)** |

---

## 3. Comando Automatizado de Verificación de Reproducibilidad

Ejecute la prueba de regresión automatizada:
```bash
python -m unittest tests/test_regression.py
```
Si el resultado es `OK`, la instalación reproduce con **100% de paridad matemática** el motor climatológico validado.

---

### Navegación

**[← Anterior](mantenimiento.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](auditoria.md)**
