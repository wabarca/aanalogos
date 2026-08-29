# Metodología Científica de Selección de Años Análogos Climáticos

## Contenido

1. [Fundamentos y Justificación Climatológica](#1-fundamentos-y-justificación-climatológica)
2. [Ventanas Temporales: Metodológica Histórica (6 meses) vs Operacional (12 meses)](#2-ventanas-temporales-metodológica-histórica-6-meses-vs-operacional-12-meses)
3. [Construcción de Vectores y Exclusión Estricta del Año Objetivo](#3-construcción-de-vectores-y-exclusión-estricta-del-año-objetivo)
4. [Métricas Estadísticas de Similitud (Pearson y MAD)](#4-métricas-estadísticas-de-similitud-pearson-y-mad)
5. [Criterio Booleano de Coincidencia y Ranking Multivariado](#5-criterio-booleano-de-coincidencia-y-ranking-multivariado)
6. [Modos de Análisis: Operacional, Reanálisis Retrospectivo y Backtesting](#6-modos-de-análisis-operacional-reanálisis-retrospectivo-y-backtesting)
7. [Tratamiento de Datos Faltantes y Aislamiento de Sentinelas](#7-tratamiento-de-datos-faltantes-y-aislamiento-de-sentinelas)
8. [Preservación del Algoritmo y Extensiones Operacionales](#8-preservación-del-algoritmo-y-extensiones-operacionales)
9. [Limitaciones Metodológicas y Consideraciones Físicas](#9-limitaciones-metodológicas-y-consideraciones-físicas)

---

## 1. Fundamentos y Justificación Climatológica

El método de **años análogos climatológicos** es una técnica empírica multivariada ampliamente utilizada en los servicios meteorológicos e hidrológicos nacionales para la predicción climática estacional. Su principio físico rector establece que configuraciones oceánicas y patrones de teleconexión atmosférica globales similares en el pasado tienden a producir respuestas climáticas regionales semejantes en los meses subsiguientes.

El sistema evalúa de manera conjunta hasta **19 índices y oscilaciones climáticas** del Océano Pacífico, Atlántico, Ártico y la atmósfera global.

---

## 2. Ventanas Temporales: Metodológica Histórica (6 meses) vs Operacional (12 meses)

El sistema distingue formalmente dos longitudes de ventana retrospectiva móvil:

* **Ventana Metodológica Histórica ($N = 6$ meses):** Corresponde a la configuración científica original utilizada para validar la metodología heredada y el benchmark oficial de referencia.
* **Ventana Operacional Retrospectiva ($N = 12$ meses):** Corresponde a una extensión operacional incorporada para evaluar el ciclo anual completo previo al período de pronóstico en la rutina institucional.

### Reglas de Construcción y Cruce Interanual
Sea $Y$ el año de evaluación y $m \in \{1, \dots, 12\}$ el mes objetivo de cierre:

1. **Caso Intra-anual ($m \ge N$):** Los $N$ meses pertenecen íntegramente al mismo año $Y$, extrayendo las columnas desde $(m - N + 1)$ hasta $m$.
2. **Caso Interanual ($m < N$):** La ventana cruza el cambio de año. Se extraen $(N - m)$ meses del año previo $Y - 1$ (columnas desde $13 - N + m$ hasta $12$) y $m$ meses del año actual $Y$ (columnas desde $1$ hasta $m$).
3. **Etiquetado:** El vector resultante de longitud $N$ queda indexado y etiquetado con el **año de cierre $Y$**.

---

## 3. Construcción de Vectores y Exclusión Estricta del Año Objetivo

Para un año y mes objetivo ($Y_{\text{obj}}, m_{\text{obj}}$), se extrae el vector objetivo $\mathbf{y} \in \mathbb{R}^N$.

### Exclusión Estricta del Año Objetivo
El año objetivo **jamás** se incluye dentro del universo de años candidatos:
$$Y_{\text{cand}} \neq Y_{\text{obj}}$$
Incluirlo generaría una correlación trivial $r = 1.0000$ y $\text{MAD} = 0.0000$, distorsionando el ranking estadístico. Esta exclusión aplica idénticamente para $N=6$ y $N=12$.

---

## 4. Métricas Estadísticas de Similitud (Pearson y MAD)

Para cada índice seleccionado $k$ y cada año candidato $Y_{\text{cand}}$, se calculan dos métricas complementarias entre el vector candidato $\mathbf{x}$ y el vector objetivo $\mathbf{y}$:

### 4.1 Coeficiente de Correlación Lineal de Pearson ($r$)
Evalúa la **sincronía, fase y tendencia temporal** de la oscilación durante los $N$ meses:
$$r = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}$$

* $r \in [-1, 1]$.
* $r > 0$ indica que ambas trayectorias evolucionaron en la misma dirección temporal.

### 4.2 Distancia Absoluta Media (MAD)
En esta formulación climatológica, **MAD representa la diferencia absoluta media (Mean Absolute Difference)** entre los valores de ambos vectores, evaluando la **cercanía en magnitud física y amplitud de la anomalía**:
$$\text{MAD} = \frac{1}{N} \sum_{i=1}^{N} |x_i - y_i|$$

* $\text{MAD} \ge 0$.
* Valores pequeños de MAD aseguran que las anomalías térmicas o báricas posean intensidades comparables en magnitud absoluta.

---

## 5. Criterio Booleano de Coincidencia y Ranking Multivariado

### 5.1 Criterio Booleano de Coincidencia Univariada
Un año histórico $Y_{\text{cand}}$ se declara **coincidente** para el índice $k$ si y solo si cumple simultáneamente ambas condiciones umbral:

$$C_k(Y_{\text{cand}}) = \begin{cases} 
1 & \text{si } (r_k > r_{\text{umbral}, k}) \;\land\; (\text{MAD}_k < \text{MAD}_{\text{umbral}, k}) \\ 
0 & \text{en caso contrario} 
\end{cases}$$

### 5.2 Conteo Total y Ranking Final
Para una combinación de $K$ índices seleccionados, el puntaje total de coincidencia del año candidato es:
$$\text{Total}(Y_{\text{cand}}) = \sum_{k=1}^{K} C_k(Y_{\text{cand}}) \quad \in \{0, 1, \dots, K\}$$

Los años análogos se ordenan en forma **descendente por la columna `Total`**, desempatando por el año más reciente.

---

## 6. Modos de Análisis: Operacional, Reanálisis Retrospectivo y Backtesting

1. **Modo Operacional:** Determina automáticamente el año actual y el último mes publicado según la regla de publicación ($M+1$), aplicando la ventana de 12 meses.
2. **Modo Reanálisis Retrospectivo Completo:** Evalúa el año objetivo $Y_{\text{obj}}$ frente a **todo el registro histórico** ($Y_{\text{cand}} \neq Y_{\text{obj}}$, incluyendo años posteriores a $Y_{\text{obj}}$). Responde a la pregunta: *¿Qué años de todo el registro histórico guardan similitud física con el caso estudiado?*
3. **Modo Reproducción Histórica / Backtesting:** Aplica el corte estricto $Y_{\text{cand}} \le Y_{\text{obj}}$ ($Y_{\text{cand}} \neq Y_{\text{obj}}$). Responde a la pregunta: *¿Qué años análogos habrían podido identificarse en tiempo real utilizando únicamente datos disponibles hasta el año objetivo?*

---

## 7. Tratamiento de Datos Faltantes y Aislamiento de Sentinelas

1. **Sentinelas Oficiales:** Valores como `-99.99`, `-99.90`, `99.99`, `-999.0` se transforman en `NaN`.
2. **Aislamiento Estricto:** Si algún mes de la ventana contiene `NaN`, la ventana se invalida y el año queda excluido de la evaluación.
3. **Cero Imputación Artificial:** Se prohíbe rellenar datos faltantes para preservar la pureza observacional.

---

## 8. Preservación del Algoritmo y Extensiones Operacionales

La formulación matemática fundamental de similitud, incluyendo la correlación de Pearson, la distancia absoluta media (MAD), el tratamiento de valores faltantes, la exclusión del año objetivo y los criterios históricos de coincidencia, se preserva respecto al benchmark validado. La aplicación incorpora extensiones operacionales explícitas, particularmente una ventana retrospectiva de doce meses y mecanismos de actualización y determinación automática del período disponible.

---

## 9. Limitaciones Metodológicas y Consideraciones Físicas

1. **Herramienta de Diagnóstico:** El método identifica análogos históricos estadísticos; no constituye por sí mismo un pronóstico determinista.
2. **No Estacionariedad y Cambio Climático:** Tendencias de calentamiento global pueden alterar los patrones de respuesta regional ante anomalías de TSM equivalentes.
3. **Intersección Temporal:** A mayor cantidad de índices seleccionados, el universo candidato común se acota al registro del índice más corto.

---

### Navegación

**[← Anterior](README.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](manual_usuario.md)**
