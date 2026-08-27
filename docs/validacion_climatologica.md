# Validación Climatológica y Protocolo Metodológico

**Documento Técnico:** `docs/validacion_climatologica.md`  
**Institución:** Gerencia de Meteorología, MARN, El Salvador

---

## 1. Fundamentos de Validación Climatológica

La evaluación automatizada de años análogos requiere garantizar tanto la **corrección computacional** como la **validez física y metodológica** de cada cálculo.

### 1.1 Exclusión Obligatoria del Año Objetivo ($Y_{\text{obj}}$)
* **Justificación Física:** Si el año objetivo no se excluye de la lista de candidatos, la comparación consigo mismo produce de forma trivial $r = 1.0000$ y $\text{MAD} = 0.0000$. En un contexto operativo de pronóstico estacional, evaluar el año objetivo como candidato de sí mismo distorsiona el ranking y carece de sentido climatológico.
* **Implementación:** El motor excluye formalmente $Y_{\text{obj}}$ antes de calcular métricas ($Y_{\text{cand}} \neq Y_{\text{obj}}$).

### 1.2 Requisito de Ventana Completa (6 Meses Continuos)
* **Justificación Física:** La similitud de la trayectoria de un modo climático requiere evaluar la evolución temporal continua durante los 6 meses seleccionados.
* **Implementación:** Si un año candidato o el año objetivo posee al menos un dato faltante (`NaN`) dentro de los 6 meses de la ventana, la ventana queda invalidada. No se permite interpolación o sustitución por ceros para no alterar la dinámica del forzante oceánico/atmosférico.

### 1.3 Aislamiento Estricto de Valores Sentinela
* **Justificación Física:** Las series de la NOAA y otros centros utilizan valores numéricos específicos (`-99.99`, `-99.90`, `99.99`, `-999.0`) para indicar meses no medidos o futuros. Si estos sentinelas entran a la fórmula de Pearson o MAD, provocan correlaciones artificiales desastrosas.
* **Implementación:** El módulo `aanalogos.quality` sanitiza cualquier valor $|x| > 50$ transformándolo en `NaN` antes de la extracción de ventanas.

### 1.4 Intersección Temporal Común ($\mathcal{H}_{\text{común}}$)
* **Justificación Física:** Cuando un climatólogo selecciona $K$ oscilaciones (e.g. `AMO`, `PDO`, `SSTA_34`), cada año histórico candidato debe ser evaluado contra **todos y cada uno de los $K$ índices bajo exactamente el mismo período común**.
* **Implicaciones Climatológicas de Índices Asimétricos:**
  * Índices con registros largos (`AMO`, `PDO`, `NAO`) inician en $1950$ (o $1946$).
  * Índices basados en satélite (`SSTA_34`, `AtlTROP`) inician en $1982$.
  * Al combinar un índice de $1950$ con uno de $1982$, el universo común $\mathcal{H}_{\text{común}}$ queda acotado al período $1982–2026$. Esto asegura que ningún candidato sea favorecido o penalizado por falta de datos en un índice respecto a otro.

---

## 2. Benchmark Oficial Certificado (Caso de Referencia)

Para verificar que cualquier instalación o réplica del sistema reproduce con exactitud matemática la metodología, se ha definido el siguiente caso oficial de prueba:

* **Año Objetivo:** `2015`
* **Mes Objetivo:** `10` (Octubre — Cierre de ventana)
* **Ventana Retrospectiva:** `MAY(2015) - JUN(2015) - JUL(2015) - AGO(2015) - SET(2015) - OCT(2015)`
* **Índices Evaluados:** `AMO` + `PDO` + `TNA`

### Métricas y Resultados del Benchmark
* **Años Históricos Evaluados ($\mathcal{H}_{\text{común}}$):** Exactamente **72 años** ($1950..2022 \setminus \{2015\}$; 2023 excluido por NaNs en AMO).
* **Evaluaciones Índice-Año:** Exactamente **216 registros**.
* **TOP 7 Años Análogos (Total Coincidencias = 2):**
  1. **2021** (AMO: 1, PDO: 1, TNA: 0)
  2. **2014** (AMO: 1, PDO: 1, TNA: 0)
  3. **2012** (AMO: 1, PDO: 1, TNA: 0)
  4. **2003** (AMO: 1, PDO: 1, TNA: 0)
  5. **2001** (AMO: 1, PDO: 1, TNA: 0)
  6. **1990** (AMO: 1, PDO: 1, TNA: 0)
  7. **1957** (AMO: 1, PDO: 1, TNA: 0)

### Trazabilidad Exacta del Año 1957
* **AMO:** $r = 0.8322$, $\text{MAD} = 0.0868$ $\to$ **Coincide (1)**
* **PDO:** $r = 0.6445$, $\text{MAD} = 0.5517$ $\to$ **Coincide (1)**
* **TNA:** $r = 0.7439$, $\text{MAD} = 0.3367$ $\to$ **No Coincide (0, MAD > 0.30)**
* **Total 1957:** **2 coincidencias**.

**Paridad Matemática del Motor:** **100.00%**.

---

### Navegación

**[← Anterior](metodologia.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](indices.md)**
