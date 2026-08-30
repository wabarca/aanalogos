# Metodología Científica de Selección de Años Análogos Climáticos

## Contenido

1. [Fundamentos y Justificación Climatológica](#1-fundamentos-y-justificación-climatológica)
2. [Tipología y Tratamiento de Variables de Entrada](#2-tipología-y-tratamiento-de-variables-de-entrada)
3. [Ventanas Temporales: Metodológica Histórica (6 meses) vs Operacional (12 meses)](#3-ventanas-temporales-metodológica-histórica-6-meses-vs-operacional-12-meses)
4. [Construcción de Vectores y Exclusión Estricta del Año Objetivo](#4-construcción-de-vectores-y-exclusión-estricta-del-año-objetivo)
5. [Métricas Estadísticas de Similitud (Pearson y MAD)](#5-métricas-estadísticas-de-similitud-pearson-y-mad)
6. [Criterio Booleano de Coincidencia y Ranking Multivariado](#6-criterio-booleano-de-coincidencia-y-ranking-multivariado)
7. [Modos de Análisis: Operacional, Reanálisis Retrospectivo y Backtesting](#7-modos-de-análisis-operacional-reanálisis-retrospectivo-y-backtesting)
8. [Tratamiento de Datos Faltantes y Aislamiento de Sentinelas](#8-tratamiento-de-datos-faltantes-y-aislamiento-de-sentinelas)
9. [Preservación del Algoritmo y Extensiones Operacionales](#9-preservación-del-algoritmo-y-extensiones-operacionales)
10. [Limitaciones Metodológicas y Consideraciones Físicas](#10-limitaciones-metodológicas-y-consideraciones-físicas)

---

## 1. Fundamentos y Justificación Climatológica

El método de **años análogos climatológicos** es una técnica empírica multivariada ampliamente utilizada en los servicios meteorológicos e hidrológicos nacionales para la predicción climática estacional. Su principio físico rector establece que configuraciones oceánicas y patrones de teleconexión atmosférica globales similares en el pasado tienden a producir respuestas climáticas regionales semejantes en los meses subsiguientes.

El sistema evalúa de manera conjunta hasta **22 índices y oscilaciones climáticas** del Océano Pacífico, Atlántico, Ártico y la atmósfera global.

---

## 2. Tipología y Tratamiento de Variables de Entrada

Para garantizar la validez física de las comparaciones multivariadas, **AAnalogos** clasifica y audita estrictamente las variables de entrada según su naturaleza matemática y física:

### 2.1 Variable Física Absoluta
Magnitud directa observada en la atmósfera u océano sin remoción del ciclo estacional medio (ej. Temperatura Superficial del Mar $T \in [20, 30]\ ^\circ\text{C}$, Presión Barométrica $P \in [1000, 1025]\ \text{hPa}$).
* **Regla Operacional:** El motor de años análogos **NUNCA** utiliza variables físicas absolutas directamente para evitar que el ciclo estacional dominante introduzca correlaciones espurias de sincronía solar.

### 2.2 Anomalía Climatológica
Desviación de una variable física respecto a su ciclo climatológico medio mensual calculado sobre un período base de 30 años (ej. 1991–2020):
$$x'(t) = x(t) - \bar{x}_{\text{clim}}(m)$$
* **Unidades:** Mantiene las unidades físicas originales (ej. $^{\circ}\text{C}$ para TSM, $10^6\ \text{km}^2$ para extensión oceánica).
* **Ejemplos en el sistema:** `AMO`, `TNA`, `CAR`, `SSTA_12`, `SSTA_3`, `SSTA_4`, `SSTA_34`, `AtlTROP`, `NAtl`, `SAtl`, `WHWP`, `ONIv5`, `ONIv6`.

### 2.3 Índice Climático / Teleconexión
Serie temporal sintética diseñada para monitorear la fase y amplitud de un modo acoplado océano-atmósfera o patrón de ondas planetarias (ej. `MEI`).

### 2.4 Índice Estandarizado (Normalizado)
Anomalía dividida por la desviación estándar interanual del mes correspondiente:
$$z(t) = \frac{x(t) - \bar{x}_{\text{clim}}(m)}{\sigma_{\text{clim}}(m)}$$
* **Unidades:** Adimensional ($z \sim \mathcal{N}(0, 1)$).
* **Ejemplos en el sistema:** `AO`, `NAO`, `PDO`, `PNA`, `SOI`.

### 2.5 Índice Derivado (Anomalía Relativa)
Índice donde se descuenta la señal del calentamiento global de fondo o se aíslan gradientes intercuenca:
$$\text{RONI}(t) = \text{SSTA}_{\text{Niño 3.4}}(t) - \overline{\text{SSTA}}_{\text{Trópicos}}(t)$$
* **Propósito:** Aislar el gradiente baroclínico zonal neto del ENOS libre de la tendencia homogénea planetaria.

---

## 3. Ventanas Temporales: Metodológica Histórica (6 meses) vs Operacional (12 meses)

El sistema distingue formalmente dos longitudes de ventana retrospectiva móvil:

* **Ventana Metodológica Histórica ($N = 6$ meses):** Corresponde a la configuración científica original utilizada para validar la metodología heredada y el benchmark oficial de referencia.
* **Ventana Operacional Retrospectiva ($N = 12$ meses):** Corresponde a una extensión operacional incorporada para evaluar el ciclo anual completo previo al período de pronóstico en la rutina institucional.

### Reglas de Construcción y Cruce Interanual
Sea $Y$ el año de evaluación y $m \in \{1, \dots, 12\}$ el mes objetivo de cierre:

1. **Caso Intra-anual ($m \ge N$):** Los $N$ meses pertenecen íntegramente al mismo año $Y$, extrayendo las columnas desde $(m - N + 1)$ hasta $m$.
2. **Caso Interanual ($m < N$):** La ventana cruza el cambio de año. Se extraen $(N - m)$ meses del año previo $Y - 1$ (columnas desde $13 - N + m$ hasta $12$) y $m$ meses del año actual $Y$ (columnas desde $1$ hasta $m$).
3. **Etiquetado:** El vector resultante de longitud $N$ queda indexado y etiquetado con el **año de cierre $Y$**.

---

## 4. Construcción de Vectores y Exclusión Estricta del Año Objetivo

Para un año y mes objetivo ($Y_{\text{obj}}, m_{\text{obj}}$), se extrae el vector objetivo $\mathbf{y} \in \mathbb{R}^N$.

### Exclusión Estricta del Año Objetivo
El año objetivo **jamás** se incluye dentro del universo de años candidatos:
$$Y_{\text{cand}} \neq Y_{\text{obj}}$$
Incluirlo generaría una correlación trivial $r = 1.0000$ y $\text{MAD} = 0.0000$, distorsionando el ranking estadístico. Esta exclusión aplica idénticamente para $N=6$ y $N=12$.

---

## 5. Métricas Estadísticas de Similitud (Pearson y MAD)

Para cada índice seleccionado $k$ y cada año candidato $Y_{\text{cand}}$, se calculan dos métricas complementarias entre el vector candidato $\mathbf{x}$ y el vector objetivo $\mathbf{y}$:

### 5.1 Coeficiente de Correlación Lineal de Pearson ($r$)
Evalúa la **sincronía, fase y tendencia temporal** de la oscilación durante los $N$ meses:
$$r = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}$$

* $r \in [-1, 1]$.
* Si la varianza de $\mathbf{x}$ o $\mathbf{y}$ es nula, $r = 0$.

### 5.2 Diferencia Absoluta Media (MAD)
Evalúa la **proximidad en magnitud física y amplitud de la anomalía**:
$$\text{MAD} = \frac{1}{N} \sum_{i=1}^{N} |x_i - y_i|$$

* $\text{MAD} \ge 0$.
* Preserva las unidades físicas del índice analizado ($^\circ\text{C}$, desv. est., $10^6\text{ km}^2$).

---

## 6. Criterio Booleano de Coincidencia y Ranking Multivariado

### 6.1 Condición de Coincidencia Univariada
Un año candidato $Y_{\text{cand}}$ es análogo para el índice $k$ si y solo si cumple simultáneamente:
$$C_k(Y_{\text{cand}}) = \begin{cases} 1 & \text{si } (r_k > r_{\text{umbral}, k}) \land (\text{MAD}_k < \text{MAD}_{\text{umbral}, k}) \\ 0 & \text{en caso contrario} \end{cases}$$

### 6.2 Puntaje Consolidado de Coincidencia
$$\text{Total}(Y_{\text{cand}}) = \sum_{k=1}^{K} C_k(Y_{\text{cand}}) \quad \in \{0, 1, \dots, K\}$$

### 6.3 Criterio de Ordenamiento del Ranking
1. **Puntaje total (`Total`):** Orden descendente.
2. **Año (`YEAR`):** Orden descendente (los análogos más recientes tienen prioridad física en caso de empate de coincidencias).

---

## 7. Modos de Análisis: Operacional, Reanálisis Retrospectivo y Backtesting

1. **Modo Operacional:** Evalúa el mes cerrado más reciente ($M-1$) usando todos los años del registro histórico como candidatos.
2. **Reanálisis Retrospectivo Completo:** Evalúa cualquier año histórico ($Y_{\text{obj}}$) comparándolo contra todos los años del catálogo histórico ($Y_{\text{cand}} \neq Y_{\text{obj}}$).
3. **Backtesting Estricto (Sin Look-Ahead):** Restringe los años candidatos a $Y_{\text{cand}} < Y_{\text{obj}}$, emulando exactamente la información disponible en el momento histórico del pronóstico.

---

## 8. Tratamiento de Datos Faltantes y Aislamiento de Sentinelas

* **Detección de Sentinelas:** Valores $\le -50.0$ o $\ge 50.0$ (`-99.99`, `-999.0`) se transforman en `NaN` e invalidan de inmediato el vector correspondiente.
* **Integridad Multivariada (Sin Reducción Silenciosa):** Si un índice seleccionado no dispone de datos válidos para el período evaluado, el motor rechaza el cálculo e informa el índice faltante.

---

## 9. Preservación del Algoritmo y Extensiones Operacionales

Todas las extensiones operacionales (12 meses, nuevas series ENSO, umbrales personalizados) se implementaron como capas incrementales no invasivas, preservando al 100% el comportamiento matemático certificado del motor base.

---

## 10. Limitaciones Metodológicas y Consideraciones Físicas

* Los años análogos identifican analogías estadísticas en el forzamiento climático de gran escala; su interpretación debe combinarse con el conocimiento sinóptico local del pronosticador.
* En escenarios de forzamiento antropogénico acelerado, índices como `RONI` complementan a `ONI` para discernir el gradiente baroclínico tropical respecto al calentamiento global homogéneo.

---

### Navegación

**[← Anterior: Inicio de Documentación](README.md)** · **[Índice de Documentación](README.md)** · **[Siguiente: Manual de Usuario →](manual_usuario.md)**
