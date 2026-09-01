# Manual de Usuario del Sistema AAnalogos

## Contenido

1. [Acceso e Interfaz General](#1-acceso-e-interfaz-general)
2. [Sección 1: Estado de Datos Disponibles](#2-sección-1-estado-de-datos-disponibles)
3. [Sección 2: Configuración de Umbrales](#3-sección-2-configuración-de-umbrales)
4. [Sección 3: Análisis de Años Análogos (Operacional y Reanálisis)](#4-sección-3-análisis-de-años-análogos-operacional-y-reanálisis)
5. [Sección 4: Explorador de Índices](#5-sección-4-explorador-de-índices)
6. [Sección 5: Metodología](#6-sección-5-metodología)
7. [Sección: Documentación y Créditos](#7-sección-documentación-y-créditos)
8. [Configuración Institucional (`config/institution.yaml`)](#8-configuración-institucional-configinstitutionyaml)

---

## 1. Acceso e Interfaz General

Inicie la aplicación mediante el comando estándar:
```bash
streamlit run app.py
```
O acceda desde cualquier estación de la red institucional a través de: `http://<IP_SERVIDOR>:8501`.

La barra lateral izquierda contiene el logotipo institucional, nombre de la entidad y permite alternar entre las secciones principales del sistema.

---

## 2. Sección 1: Estado de Datos Disponibles

* **Panel de Cobertura:** Indicadores de salud global (ej. `21 / 21 series disponibles`, cobertura promedio en años y último año con registros).
* **Inventario Detallado:** Tabla completa con código, nombre legible, primer año, último año, último mes publicado, tipo de variable, variable exacta en motor y estado de disponibilidad (`✓ Disponible`, `✗ No disponible`, `⚠ Error`).
* **Botón ↻ Actualizar índices:** Descarga atómica y no destructiva desde las fuentes oficiales de NOAA/CPC/PSL/CSU sin riesgo de corromper series locales.

---

## 3. Sección 2: Configuración de Umbrales

* Permite calibrar individualmente $r_{\text{umbral}}$ (correlación lineal de Pearson) y $\text{MAD}_{\text{umbral}}$ (distancia absoluta media) para cada una de las 21 oscilaciones climáticas.
* Muestra indicadores visuales de estado: 🟢 *Valor oficial* / 🟠 *Modificado por usuario*.
* **Botón 🔄 Restaurar Valores Metodológicos Predeterminados:** Restablece instantáneamente los umbrales oficiales validados.

---

## 4. Sección 3: Análisis de Años Análogos (Operacional y Reanálisis)

### Modo Operacional
* **Detección Automática:** El sistema identifica la fecha del sistema y el último mes operacional utilizable respetando la regla de publicación ($M+1$).
* **Ventana Predeterminada:** Aplica automáticamente la ventana operacional de 12 meses.
* **Uso:** Seleccione la combinación de oscilaciones deseadas en el panel lateral (por defecto `RONI`, `TNA`, `ONIv6`) y presione **🚀 Calcular Años Análogos**.

### Modo Reanálisis Histórico
* **Año y Mes Personalizado:** Permite seleccionar cualquier año ($1950 \le Y_{\text{obj}} \le \text{actual}$) y mes ($1 \le m \le 12$).
* **Longitud de Ventana:** Permite elegir entre 12 meses (operacional) o 6 meses (metodológica histórica).
* **Alcance del Reanálisis:**
  * **Retrospectivo Completo:** Evalúa el año objetivo frente a todos los años del registro histórico ($Y_{\text{cand}} \neq Y_{\text{obj}}$).
  * **Backtesting / Simulación en Tiempo Real:** Aplica corte estricto ($Y_{\text{cand}} \le Y_{\text{obj}}$), evaluando únicamente los datos que habrían estado disponibles al momento del evento.

### Interpretación de Resultados
* **Resumen de KPIs:** Año objetivo, mes de cierre, ventana, candidatos evaluados y coincidencias encontradas.
* **Pestaña Ranking:** Tabla de años análogos ordenados por coincidencia multivariada `Total` descendente y año más reciente.
* **Pestaña Gráficos Comparativos:** Histograma de análogos y comparación temporal de curvas donde el Año Objetivo se resalta en azul institucional.
* **Pestaña Trazabilidad Detallada:** Tabla diagnóstica completa con valores individuales de $r$, MAD y banderas de coincidencia $C_k$.
* **Botones de Descarga:** Exportación directa a archivos CSV.

---

## 5. Sección 4: Explorador de Índices

Permite seleccionar cualquiera de las 21 oscilaciones climáticas para inspeccionar:
* **Ficha Técnica y Auditoría:** Nombre completo, institución responsable, región, variable física, tipo de variable, variable exacta utilizada en el cálculo de años análogos, columna fuente, unidades y DOI.
* **Evolución Temporal:** Gráfico interactivo mensual con filtros temporales (*Todo el registro*, *Últimos 10 años*, *Últimos 5 años*, *Rango personalizado*).
* **Tabla de Datos Históricos Interactiva:**
  * Visualización completa de los registros anuales y mensuales.
  * Resaltado explícito de la variable utilizada en el motor.
  * Pestañas para alternar entre matriz mensual y series compuestas originales.
  * Botón de exportación: **💾 Descargar CSV**.

---

## 6. Sección 5: Metodología

Sección didáctica integrada que explica a los especialistas meteorológicos los fundamentos matemáticos:
* Tipología de variables (variables absolutas, anomalías, índices normalizados, índices derivados).
* Ventana histórica (6 meses) vs operacional (12 meses).
* Exclusión estricta del año objetivo ($Y_{\text{cand}} \neq Y_{\text{obj}}$).
* Correlación de Pearson ($r$) y Diferencia Absoluta Media (MAD).
* Criterio booleano $C_k$ y algoritmo de ranking multivariado.

---

## 7. Sección: Documentación y Créditos

* **Pestaña Documentación del Sistema:** Enlaces directos y descripciones a los manuales, metodologías, fichas de índices, guías de instalación y arquitectura en `docs/`.
* **Pestaña Créditos y Atribución:** Información de versión, propósito científico, personalización institucional activa y atribución a centros climáticos internacionales (NOAA CPC, PSL, NCEI, CSU).

---

## 8. Configuración Institucional (`config/institution.yaml`)

El sistema permite adaptar institucionalmente el nombre, la división y el logotipo PNG sin modificar el código fuente:

```yaml
institution:
  name: "Nombre de su Institución"
  division: "Nombre de la División o Departamento"
  logo: "docs/img/su_logo.png"
```

---

### Navegación

**[← Anterior](metodologia.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](validacion_climatologica.md)**
