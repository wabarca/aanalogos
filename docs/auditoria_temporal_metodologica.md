# Auditoría Climatológica y Metodológica — Ventanas de 12 Meses, Solapamiento Temporal y Reanálisis

[← Volver al Índice General de Documentación](README.md)

---

## Ficha del Documento

* **Institución:** Ministerio de Medio Ambiente y Recursos Naturales (MARN), El Salvador
* **Unidad Responsable:** Gerencia de Meteorología — Dirección del Observatorio de Amenazas y Recursos Naturales
* **Sistema:** `aanalogos v3.2.0`
* **Tipo de Documento:** Dictamen de Auditoría Científica y Metodológica
* **Fecha de Emisión:** 29 de agosto de 2026
* **Estado:** Certificado / Aprobado

---

## 1. Contexto y Objetivos de la Auditoría

El sistema **AAnalogos** incorpora en su versión operacional una ventana retrospectiva continua de **12 meses**, permitiendo evaluar la evolución del ciclo anual completo previo a la fecha de pronóstico o diagnóstico.

La presente auditoría tiene como objetivo resolver de manera formal, matemática y climatológica las siguientes interrogantes:
1. ¿Es la condición de exclusión nominal $Y_{\text{cand}} \neq Y_{\text{obj}}$ matemáticamente suficiente para garantizar que no exista solapamiento temporal entre la ventana objetivo y las ventanas candidatas de 12 meses?
2. ¿Qué meses específicos componen las ventanas en casos de candidatos inmediatamente anteriores ($Y-1$) y posteriores ($Y+1$)?
3. ¿Cómo se formaliza la independencia temporal frente al backtesting causal y el reanálisis retrospectivo?
4. ¿Se preserva la paridad del 100 % del benchmark histórico certificado?

---

## 2. Demostración Matemática Formal de No Solapamiento Temporal

Sea $m \in \{1, 2, \dots, 12\}$ el mes objetivo de cierre de la evaluación y sea $N=12$ la longitud en meses de la ventana temporal continua.

### 2.1 Definición de Conjuntos Temporales

1. La **Ventana Objetivo** correspondiente al año $Y_{\text{obj}}$ evaluada al mes de cierre $m$ está conformada por el conjunto discreto de 12 pares (año, mes):
   $$W(Y_{\text{obj}}, m, 12) = \{(Y_{\text{obj}}-1, m+1), \dots, (Y_{\text{obj}}-1, 12)\} \;\cup\; \{(Y_{\text{obj}}, 1), \dots, (Y_{\text{obj}}, m)\}$$

2. La **Ventana Candidata** de cualquier año histórico $Y_{\text{cand}} \neq Y_{\text{obj}}$ evaluada con respecto al **mismo mes de cierre $m$** está conformada por:
   $$W(Y_{\text{cand}}, m, 12) = \{(Y_{\text{cand}}-1, m+1), \dots, (Y_{\text{cand}}-1, 12)\} \;\cup\; \{(Y_{\text{cand}}, 1), \dots, (Y_{\text{cand}}, m)\}$$

---

### 2.2 Análisis de Casos Límite de Adyacencia Temporal

#### Caso 1: Candidato Inmediatamente Anterior ($Y_{\text{cand}} = Y_{\text{obj}} - 1$)

* **Meses que componen la Ventana Candidata ($Y_{\text{obj}}-1$):**
  * Abarca los meses $\{m+1, \dots, 12\}$ del año $Y_{\text{obj}}-2$.
  * Abarca los meses $\{1, \dots, m\}$ del año $Y_{\text{obj}}-1$.
* **Meses que componen la Ventana Objetivo ($Y_{\text{obj}}$):**
  * Abarca los meses $\{m+1, \dots, 12\}$ del año $Y_{\text{obj}}-1$.
  * Abarca los meses $\{1, \dots, m\}$ del año $Y_{\text{obj}}$.

**Evaluación de la intersección en el año común $Y_{\text{obj}}-1$:**
$$\text{Meses del candidato en } (Y_{\text{obj}}-1) = \{1, 2, \dots, m\}$$
$$\text{Meses del objetivo en } (Y_{\text{obj}}-1) = \{m+1, m+2, \dots, 12\}$$
$$\{1, \dots, m\} \cap \{m+1, \dots, 12\} = \emptyset$$

Dado que los meses en $Y_{\text{obj}}-2$ solo pertenecen al candidato y los meses en $Y_{\text{obj}}$ solo pertenecen al objetivo:
$$W(Y_{\text{obj}}-1, m, 12) \cap W(Y_{\text{obj}}, m, 12) = \emptyset$$

---

#### Caso 2: Candidato Inmediatamente Posterior ($Y_{\text{cand}} = Y_{\text{obj}} + 1$)

* **Meses que componen la Ventana Objetivo ($Y_{\text{obj}}$):**
  * Abarca los meses $\{m+1, \dots, 12\}$ del año $Y_{\text{obj}}-1$.
  * Abarca los meses $\{1, \dots, m\}$ del año $Y_{\text{obj}}$.
* **Meses que componen la Ventana Candidata ($Y_{\text{obj}}+1$):**
  * Abarca los meses $\{m+1, \dots, 12\}$ del año $Y_{\text{obj}}$.
  * Abarca los meses $\{1, \dots, m\}$ del año $Y_{\text{obj}}+1$.

**Evaluación de la intersección en el año común $Y_{\text{obj}}$:**
$$\text{Meses del objetivo en } Y_{\text{obj}} = \{1, 2, \dots, m\}$$
$$\text{Meses del candidato en } Y_{\text{obj}} = \{m+1, m+2, \dots, 12\}$$
$$\{1, \dots, m\} \cap \{m+1, \dots, 12\} = \emptyset$$

Por tanto:
$$W(Y_{\text{obj}}+1, m, 12) \cap W(Y_{\text{obj}}, m, 12) = \emptyset$$

---

### 2.3 Ejemplo Concreto Obligatorio: Objetivo Octubre 2015 ($m=10, N=12$)

* **Ventana Objetivo (2015, $m=10$):**  
  `Noviembre 2014, Diciembre 2014, Enero 2015, Febrero 2015, ..., Octubre 2015`
* **Candidato Inmediatamente Anterior (2014, $m=10$):**  
  `Noviembre 2013, Diciembre 2013, Enero 2014, Febrero 2014, ..., Octubre 2014`  
  * *Verificación:* El candidato 2014 finaliza en **Octubre 2014**; el objetivo 2015 inicia en **Noviembre 2014**. **No comparten ningún mes** (Intersección vacía $\emptyset$).
* **Candidato del Mismo Año (2015):** Excluido por la regla $Y_{\text{cand}} \neq Y_{\text{obj}}$.
* **Candidato Inmediatamente Posterior (2016, $m=10$):**  
  `Noviembre 2015, Diciembre 2015, Enero 2016, Febrero 2016, ..., Octubre 2016`  
  * *Verificación:* El objetivo 2015 finaliza en **Octubre 2015**; el candidato 2016 inicia en **Noviembre 2015**. **No comparten ningún mes** (Intersección vacía $\emptyset$).

> [!IMPORTANT]
> **Teorema de Independencia Temporal:**  
> Para toda longitud de ventana $N \le 12$ meses evaluada sobre un mes de cierre idéntico $m$, la condición de exclusión nominal $Y_{\text{cand}} \neq Y_{\text{obj}}$ es **condición necesaria y suficiente** para garantizar la **independencia temporal total** ($W_{\text{cand}} \cap W_{\text{obj}} = \emptyset$).

---

## 3. Matriz de Casos Climatológicos

A continuación se resume la matriz de interacción temporal para los casos operacionales y de reanálisis evaluados:

| Caso de Estudio ($Y_{\text{obj}}, m$) | Ventana Objetivo ($N=12$) | Ventana Candidato $Y-1$ | Ventana Candidato $Y+1$ | ¿Existe Solapamiento? | Admisible en Operación | Admisible en Reanálisis Retrospectivo | Admisible en Backtesting Causal |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Enero 2026** ($Y=2025, m=12$)* | `ENE 2025 – DIC 2025` | `ENE 2024 – DIC 2024` | 2026 (No cerrado) | **NO** ($\emptyset$) | **SÍ** (2024) | **SÍ** (2024) | **SÍ** (2024) |
| **Febrero 2026** ($Y=2026, m=1$) | `FEB 2025 – ENE 2026` | `FEB 2024 – ENE 2025` | 2027 (No cerrado) | **NO** ($\emptyset$) | **SÍ** (2025) | **SÍ** (2025) | **SÍ** (2025) |
| **Marzo 2026** ($Y=2026, m=2$) | `MAR 2025 – FEB 2026` | `MAR 2024 – FEB 2025` | 2027 (No cerrado) | **NO** ($\emptyset$) | **SÍ** (2025) | **SÍ** (2025) | **SÍ** (2025) |
| **Julio 2026** ($Y=2026, m=6$) | `JUL 2025 – JUN 2026` | `JUL 2024 – JUN 2025` | 2027 (No cerrado) | **NO** ($\emptyset$) | **SÍ** (2025) | **SÍ** (2025) | **SÍ** (2025) |
| **Agosto 2026** ($Y=2026, m=7$) | `AGO 2025 – JUL 2026` | `AGO 2024 – JUL 2025` | 2027 (No cerrado) | **NO** ($\emptyset$) | **SÍ** (2025) | **SÍ** (2025) | **SÍ** (2025) |
| **Octubre 2015** ($Y=2015, m=10$) | `NOV 2014 – OCT 2015` | `NOV 2013 – OCT 2014` | `NOV 2015 – OCT 2016` | **NO** ($\emptyset$) | N/A (Histórico) | **SÍ** (2014 y 2016) | **SÍ** (2014) / **NO** (2016) |
| **Diciembre 2015** ($Y=2015, m=12$) | `ENE 2015 – DIC 2015` | `ENE 2014 – DIC 2014` | `ENE 2016 – DIC 2016` | **NO** ($\emptyset$) | N/A (Histórico) | **SÍ** (2014 y 2016) | **SÍ** (2014) / **NO** (2016) |

*\* Nota para Enero 2026: Conforme a la regla de publicación institucional $M+1$, el mes cerrado utilizable es Diciembre de 2025.*

---

## 4. Formalización de las Tres Reglas Metodológicas

| Regla Metodológica | Formulación Matemática | Justificación Climatológica | Aplicabilidad en el Sistema |
| :--- | :--- | :--- | :--- |
| **1. Exclusión por Año** | $Y_{\text{cand}} \neq Y_{\text{obj}}$ | Evita que el año objetivo se compare consigo mismo generando correlaciones triviales ($r=1.0, \text{MAD}=0.0$). | Obligatoria en todos los modos. |
| **2. Independencia Temporal** | $W_{\text{cand}} \cap W_{\text{obj}} = \emptyset$ | Asegura que ninguna observación física coincida en el tiempo entre el objetivo y el análogo. | Garantizada automáticamente para $N \le 12$. |
| **3. Backtesting Causal** | $\text{FechaFinal}(W_{\text{cand}}) \le \text{FechaFinal}(W_{\text{obj}}) - 1 \text{ año}$ | Elimina la contaminación por información futura (*look-ahead bias*), simulando la operación en tiempo real. | Exclusiva del **Modo Backtesting**. |

---

## 5. Distinción entre Reanálisis Retrospectivo y Backtesting Causal

### 5.1 Reanálisis Retrospectivo Completo (Diagnóstico Global)
* **Finalidad:** Identificar qué episodios de todo el registro instrumental disponible (1950–2026) guardan similitud física con el evento evaluado.
* **Validez de $Y_{\text{cand}} > Y_{\text{obj}}$:** Es un procedimiento científico plenamente válido en climatología diagnóstica. Por ejemplo, permite evaluar si la configuración sinóptica del evento 2015 guarda analogía con eventos ocurridos en 2021.
* **Requisito de transparencia:** Debe rotularse explícitamente en la interfaz como *Análisis Retrospectivo No Causal*.

### 5.2 Backtesting / Simulación en Tiempo Real (Evaluación Causal)
* **Finalidad:** Cuantificar la habilidad predictiva retrospectiva que el sistema habría tenido si se hubiese ejecutado en la fecha del evento histórico.
* **Restricción estricta:** No se admite ningún candidato posterior a la fecha objetivo ($Y_{\text{cand}} < Y_{	ext{obj}}$), garantizando que no se utilice información inexistente en ese momento.

---

## 6. Estado del Benchmark Histórico Oficial

El caso de calibración y referencia histórica:
* **Caso:** 2015 / Octubre / `AMO + PDO + TNA`
* **Longitud:** 6 meses (Mayo–Octubre)
* **Candidatos comunes:** 72 años
* **Evaluaciones:** 216 evaluaciones índice-año
* **TOP 7:** `2021, 2014, 2012, 2003, 2001, 1990, 1957` ($\text{Total} = 2$)
* **Paridad Matemática:** **100.00 %**

El benchmark se preserva intacto y sin modificaciones algorítmicas, certificando la no regresión de la suite de pruebas.

---

## 7. Dictamen Final

### **DICTAMEN: CORRECTO CON ACLARACIÓN DOCUMENTAL Y FORMALIZACIÓN METODOLÓGICA**

1. **No se requiere modificar el motor científico:** La formulación matemática y el código implementado en `engine.py`, `windows.py`, `quality.py` y `catalog.py` ya cumplen rigurosamente con la independencia temporal $W_{\text{cand}} \cap W_{\text{obj}} = \emptyset$ y la causalidad del backtesting.
2. **Sustento Documental Formalizado:** La presente auditoría queda integrada como documento metodológico rector en `docs/auditoria_temporal_metodologica.md` para referencia de los técnicos y meteorólogos del Observatorio de Amenazas del MARN.

---

[← Volver al Índice General de Documentación](README.md)
