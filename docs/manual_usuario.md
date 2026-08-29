# Manual de Usuario del Sistema AAnalogos

## Contenido

1. [Acceso e Interfaz General](#1-acceso-e-interfaz-general)
2. [Sección 1: Análisis de Años Análogos (Operacional y Reanálisis)](#2-sección-1-análisis-de-años-análogos-operacional-y-reanálisis)
3. [Sección 2: Explorador de Índices Climáticos](#3-sección-2-explorador-de-índices-climáticos)
4. [Sección 3: Metodología de Cálculo](#4-sección-3-metodología-de-cálculo)
5. [Sección 4: Estado y Actualización de Datos](#5-sección-4-estado-y-actualización-de-datos)
6. [Sección 5: Configuración y Calibración de Umbrales](#6-sección-5-configuración-y-calibración-de-umbrales)
7. [Interpretación de Resultados y Exportación](#7-interpretación-de-resultados-y-exportación)

---

## 1. Acceso e Interfaz General

Inicie la aplicación mediante el comando estándar:
```bash
streamlit run app.py
```
O acceda desde cualquier estación de la red institucional a través de: `http://<IP_SERVIDOR>:8501`.

La barra lateral izquierda permite alternar entre las 5 secciones principales del sistema.

---

## 2. Sección 1: Análisis de Años Análogos (Operacional y Reanálisis)

### Modo Operacional
* **Detección Automática:** El sistema identifica la fecha del sistema y el último mes operacional utilizable respetando la regla de publicación ($M+1$).
* **Ventana Predeterminada:** Aplica automáticamente la ventana operacional de 12 meses.
* **Uso:** Seleccione la combinación de oscilaciones deseadas en el panel lateral y presione **🚀 Calcular Años Análogos**.

### Modo Reanálisis Histórico
* **Año y Mes Personalizado:** Permite seleccionar cualquier año ($1950 \le Y_{\text{obj}} \le \text{actual}$) y mes ($1 \le m \le 12$).
* **Longitud de Ventana:** Permite elegir entre 12 meses (operacional) o 6 meses (metodológica histórica).
* **Alcance del Reanálisis:**
  * **Retrospectivo Completo:** Evalúa el año objetivo frente a todos los años del registro histórico ($Y_{\text{cand}} \neq Y_{\text{obj}}$).
  * **Backtesting / Simulación en Tiempo Real:** Aplica corte estricto ($Y_{\text{cand}} \le Y_{\text{obj}}$), evaluando únicamente los datos que habrían estado disponibles al momento del evento.

---

## 3. Sección 2: Explorador de Índices Climáticos

Permite seleccionar cualquiera de las 19 oscilaciones para inspeccionar:
* **Ficha Técnica:** Nombre completo, institución responsable, región, variable física, unidades y DOI.
* **Evolución Temporal:** Gráfico interactivo mensual con filtros rápidos (*Todo el registro*, *Últimos 10 años*, *Últimos 5 años*, *Rango personalizado*).

---

## 4. Sección 3: Metodología de Cálculo

Sección didáctica integrada que explica a los especialistas meteorológicos los fundamentos matemáticos:
* Ventana histórica (6 meses) vs operacional (12 meses).
* Correlación de Pearson ($r$) y Distancia Absoluta Media (MAD).
* Criterio booleano $C_k$ y algoritmo de ranking multivariado.

---

## 5. Sección 4: Estado y Actualización de Datos

* **Panel de Cobertura:** Indicador global de salud (ej. `19 / 19 series disponibles`).
* **Tabla de Diagnóstico:** Primer año, último año, último mes publicado y estado de cada serie.
* **Botón 🔄 Actualizar Índices Climáticos:** Descarga atómica de las fuentes de NOAA/CPC/PSL/CSU sin riesgo de corromper series existentes si falla la conexión.

---

## 6. Sección 5: Configuración y Calibración de Umbrales

* Permite ajustar individualmente $r_{\text{umbral}}$ y $\text{MAD}_{\text{umbral}}$ para cada oscilación.
* Muestra indicadores visuales de estado: 🟢 *Valor oficial* / 🟠 *Modificado por usuario*.
* **Botón 🔄 Restaurar Valores Metodológicos Predeterminados:** Restablece instantáneamente los umbrales oficiales validados.

---

## 7. Interpretación de Resultados y Exportación

* **Tabla de Ranking:** Ordena los años históricos por el puntaje `Total`.
* **Gráficos:** Histograma de análogos y comparación temporal de trayectorias.
* **Trazabilidad:** Valores exactos de $r$, MAD y umbrales aplicados.
* **Botones de Descarga:** Exportación directa a formato CSV estructurado.

---

### Navegación

**[← Anterior](metodologia.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](validacion_climatologica.md)**
