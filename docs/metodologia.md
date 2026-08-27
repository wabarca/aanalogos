# Metodología Climatológica de Selección de Años Análogos

## 1. Concepto y Fundamento Climatológico de los Años Análogos

El método de **Años Análogos** es una técnica empírico-estadística ampliamente utilizada en la climatología aplicada y los servicios meteorológicos operativos (como el Instituto Meteorológico Nacional de Costa Rica, IMN) para el apoyo a la **predicción climática estacional y subsustancial**.

### 1.1 Fundamento Físico
El sistema climático global exhibe variabilidad en múltiples escalas temporales (intraestacional, interanual y multidecadal), gobernada en gran medida por la interacción océano-atmósfera y los modos acoplados de gran escala (como el evento El Niño-Oscilación del Sur - ENOS, la Oscilación Decadal del Pacífico - PDO, y la Oscilación Multidecadal del Atlántico - AMO).

La hipótesis central del método establece que **si el estado y la trayectoria reciente de los principales forzantes oceánicos y atmosféricos de gran escala en un año objetivo son similares a los observados en un año histórico determinado, la evolución climática regional subsiguiente (e.g. régimen de precipitación, temperatura y eventos extremos) tenderá a comportarse de forma análoga a la de dicho año histórico**.

### 1.2 Utilidad Operativa y Alcance
* **Apoyo a la toma de decisiones:** Permite a los meteorólogos y tomadores de decisión disponer de escenarios históricos concretos de impacto (e.g. sequías, temporadas de huracanes activas, inundaciones) asociados a patrones oceánicos similares.
* **Complemento a los modelos numéricos:** Sirve como herramienta diagnóstica independiente frente a los pronósticos dinámicos globales (modelos globales de circulación general, GCMs).

### 1.3 Limitaciones Científicas Críticas
1. **No determinismo:** Un año análogo **no constituye por sí mismo un pronóstico determinista**. La no-linealidad intrínseca de la atmósfera y el calentamiento global antropogénico pueden modular la respuesta regional aun cuando los índices oceánicos muestren alta coincidencia.
2. **Dependencia de la longitud de registro:** La base empírica está acotada a las décadas con observaciones instrumentales homogéneas (usualmente desde 1950 o 1982).
3. **Sensibilidad a la selección de índices y sobreajuste:** Seleccionar un número excesivo de índices puede reducir artificialmente el universo de años análogos a cero, o seleccionar candidatos por azar. La selección debe responder a un criterio físico justificado para la región de interés.

---

## 2. Definición y Construcción de la Ventana Temporal

La metodología evalúa la evolución temporal del sistema mediante una **ventana retrospectiva móvil de seis meses consecutivos**, culminando en el **mes objetivo ($m_{\text{obj}}$)** del **año objetivo ($Y_{\text{obj}}$)**.

### 2.1 Ventanas Intra-anuales ($m_{\text{obj}} \ge 6$)
Cuando el mes objetivo es igual o posterior a junio, la ventana semestral se encuentra contenida en su totalidad dentro del mismo año calendario:
$$\mathbf{x}(Y) = \left[ x(Y, m_{\text{obj}}-5), \, x(Y, m_{\text{obj}}-4), \, x(Y, m_{\text{obj}}-3), \, x(Y, m_{\text{obj}}-2), \, x(Y, m_{\text{obj}}-1), \, x(Y, m_{\text{obj}}) \right]$$

* **Ejemplo ($Y_{\text{obj}} = 2015, m_{\text{obj}} = 10$ - Octubre):**
  $$\mathbf{x}_{\text{target}} = [\text{MAY}(2015), \text{JUN}(2015), \text{JUL}(2015), \text{AGO}(2015), \text{SET}(2015), \text{OCT}(2015)]$$

### 2.2 Ventanas Interanuales que Cruzan Año ($m_{\text{obj}} < 6$)
Cuando el mes objetivo es anterior a junio (enero a mayo), los seis meses retrospectivos cruzan la frontera de diciembre/enero, abarcando los últimos meses del año precedente ($Y-1$) y los primeros meses del año de cierre ($Y$).
**Regla Metodológica Invariante:** El candidato se etiqueta **estrictamente con el año de cierre $Y$**:
$$\mathbf{x}(Y) = \left[ x(Y-1, m_{\text{obj}}+7), \, \dots, \, x(Y-1, 12), \, x(Y, 1), \, \dots, \, x(Y, m_{\text{obj}}) \right]$$

* **Ejemplo ($Y_{\text{obj}} = 2015, m_{\text{obj}} = 2$ - Febrero):**
  $$\mathbf{x}_{\text{target}} = [\text{SET}(2014), \text{OCT}(2014), \text{NOV}(2014), \text{DIC}(2014), \text{ENE}(2015), \text{FEB}(2015)]$$

---

## 3. Universo de Candidatos e Intersección Temporal

El conjunto de años históricos evaluados por el motor ($\mathcal{H}_{\text{candidatos}}$) se obtiene mediante un filtrado estricto:

```
Años Totales Disponibles en Archivos
                ↓
Filtrado de Ventana Completa (6 meses continuos observados, sin NaNs ni sentinelas)
                ↓
Intersección Temporal Común (H_común = ⋂ de ventanas válidas de todos los índices seleccionados)
                ↓
Exclusión del Año Objetivo (Y_cand ≠ Y_obj)
                ↓
Universo Final de Años Candidatos (H_candidatos)
```

### 3.1 Exclusión del Año Objetivo
El año objetivo **jamás** se incluye como candidato de sí mismo ($Y_{\text{cand}} \neq Y_{\text{obj}}$). Incluirlo generaría una correlación trivial $r = 1.0000$ y $\text{MAD} = 0.0000$, distorsionando el ranking.

---

## 4. Métricas Estadísticas de Similitud

Para cada índice seleccionado $k$ y cada año candidato $Y_{\text{cand}} \in \mathcal{H}_{\text{candidatos}}$, se calculan dos métricas complementarias entre el vector candidato $\mathbf{x}$ y el vector objetivo $\mathbf{y}$:

### 4.1 Coeficiente de Correlación Lineal de Pearson ($r$)
Evalúa la **similitud en la tendencia, forma y sincronía temporal** de la oscilación durante los seis meses:
$$r = \frac{\sum_{i=1}^{6} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{6} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{6} (y_i - \bar{y})^2}}$$

* $r \in [-1, 1]$.
* $r > 0$ indica que ambas trayectorias evolucionaron en la misma dirección temporal (calentamiento/enfriamiento relativo sincronizado).

### 4.2 Distancia Absoluta Media (MAD)
En esta implementación climatológica, **MAD representa la diferencia absoluta media (Mean Absolute Difference) entre los valores de ambos vectores**, evaluando la **cercanía en magnitud y amplitud física de la anomalía**:
$$\text{MAD} = \frac{1}{6} \sum_{i=1}^{6} |x_i - y_i|$$

* $\text{MAD} \ge 0$.
* Valores pequeños de MAD aseguran que no solo coincida la tendencia, sino que las anomalías térmicas o báricas posean intensidades comparables en magnitud absoluta.

---

## 5. Criterio de Coincidencia y Ranking Multivariado

### 5.1 Criterio Booleano de Coincidencia Univariada
Un año histórico $Y_{\text{cand}}$ se declara **coincidente** para el índice $k$ si y solo si cumple simultáneamente ambas condiciones umbral:
$$C_k(Y_{\text{cand}}) = \begin{cases} 1 & \text{si } r_k > r_{\text{umbral}, k} \quad \land \quad \text{MAD}_k < \text{MAD}_{\text{umbral}, k} \\ 0 & \text{en caso contrario} \end{cases}$$

### 5.2 Conteo Total y Ranking Final
Para una combinación de $K$ índices seleccionados, el puntaje total de coincidencia del año candidato es:
$$\text{Total}(Y_{\text{cand}}) = \sum_{k=1}^{K} C_k(Y_{\text{cand}}) \quad \in \{0, 1, \dots, K\}$$

Los años análogos se ordenan en forma **descendente por la columna `Total`**, desempatando por el año más reciente.

---

## 6. Tratamiento de Datos Faltantes y Valores Sentinela

1. **Sentinelas de Fuentes Oficiales:** Códigos como `-99.99`, `-99.90`, `99.99`, `-999.0` representan ausencia de medición y son convertidos inmediatamente a `NaN`.
2. **Aislamiento Estricto:** Si alguno de los 6 meses de la ventana de un año candidato contiene `NaN`, la ventana se considera incompleta y el año queda **excluido de la evaluación estadística**.
3. **Cero Imputación Arbitraria:** La metodología prohíbe rellenar datos faltantes con ceros o medias artificiales para preservar la estricta pureza observacional.
