# Manual de Usuario: Sistema de Selección de Años Análogos Climáticos



## Contenido

1. [Introducción](#introducción)
2. [Acceso e Inicio de la Aplicación](#acceso-e-inicio-de-la-aplicación)
3. [Guía Paso a Paso de Uso](#guía-paso-a-paso-de-uso)
4. [Alertas y Mensajes de Advertencia](#alertas-y-mensajes-de-advertencia)

---
## 1. Introducción
**AAnalogos** es una aplicación interactiva desarrollada en Python y Streamlit para asistir a meteorólogos, climatólogos y analistas en la identificación rigurosa y automatizada de años históricos con patrones de variabilidad climática similares a un período objetivo.

---

## 2. Acceso e Inicio de la Aplicación

### En Entorno Local
Abra una terminal en el directorio del proyecto y ejecute:
```bash
streamlit run app.py
```

### En Red Institucional (LAN)
Abra su navegador web favorito (Chrome, Firefox, Edge) e ingrese la dirección del servidor institucional:
`http://<IP_DEL_SERVIDOR>:8501`

---

## 3. Guía Paso a Paso de Uso

### Paso 1: Configuración de Parámetros (Panel Lateral)
En el panel lateral izquierdo (`⚙️ Configuración del Análisis`):
1. **Año Objetivo ($Y_{\text{obj}}$):** Ingrese el año que desea evaluar (e.g. `2015`, `2024`, `2026`).
2. **Mes Objetivo (Cierre de Ventana):** Seleccione el mes en el que finaliza el período semestral (e.g. `10 — OCT`).
3. **Selección de Índices:** Elija una o más de las 19 oscilaciones disponibles en la lista desplegable.

### Paso 2: Ejecución del Cálculo
* Presione el botón **`🚀 Calcular Años Análogos`**.
* El motor ejecutará el filtrado de ventanas, la intersección temporal y las métricas univariadas en menos de un segundo.

### Paso 3: Diagnóstico y Cobertura de Series
* Despliegue el apartado **`📊 Diagnóstico y Cobertura de Series Temporales Seleccionadas`** para verificar los años cubiertos por cada índice y si el vector objetivo se encuentra completo.

### Paso 4: Interpretación del Ranking de Resultados
* **Tarjetas KPI:** Muestran el total de años candidatos evaluados en el período común ($\mathcal{H}_{\text{común}}$) y la máxima coincidencia alcanzada.
* **Tabla de Ranking:** Lista los años históricos ordenados descendentemente.
  * **Columna Ranking:** Posición relativa (1..N).
  * **Año Análogo:** Año histórico coincidente.
  * **Total Coincidencias:** Cantidad de oscilaciones que cumplieron los umbrales ($r > r_{\text{umbral}} \land \text{MAD} < \text{MAD}_{\text{umbral}}$).
  * **Índices Coincidentes:** Lista explícita de oscilaciones que coincidieron.

### Paso 5: Inspección Detallada por Año Análogo
* En la sección **`🔍 Detalle Estadístico y Trazabilidad por Año Análogo`**, elija un año del selector:
  * **Tabla de Métricas:** Muestra el $r$ y MAD exacto frente a sus umbrales.
  * **Trazabilidad Mensual:** Compara los valores numéricos mes a mes de la ventana de 6 meses (Objetivo vs Análogo) y su diferencia absoluta.

### Paso 6: Visualizaciones Climatológicas
* **Pestaña 1 (Comparación Temporal):** Gráficos de líneas con las trayectorias de los 6 meses de cada oscilación ($Y_{\text{obj}}$ en azul vs $Y_{\text{análogo}}$ en rojo).
* **Pestaña 2 (Distribución de Coincidencias):** Histograma de frecuencias de coincidencias históricas.

### Paso 7: Exportación de Resultados
En la sección **`📥 Exportación de Resultados`**:
* **📄 Descargar Ranking (CSV):** Descarga la tabla consolidada en formato CSV.
* **📊 Descargar Trazabilidad Completa (CSV):** Descarga los $N \times K$ registros con $r$ y MAD en precisión `float64`.
* **📝 Descargar Informe Completo (TXT):** Descarga un informe técnico estructurado listo para imprimir o adjuntar a reportes.

---

## 4. Alertas y Mensajes de Advertencia

* **❌ Error de Validación Científica (Índices Incompletos):**  
  Aparece si seleccionó un índice que no dispone de los 6 meses completos para el año/mes objetivo (e.g. seleccionar `CAR` o `SOI` para el año 2024).  
  *Acción requerida:* Deseleccione los índices sin cobertura o elija un año/mes con datos observados completos.
* **⚠️ Sin Intersección Temporal Común:**  
  Ocurre si la combinación de índices elegida no comparte ningún año histórico con ventanas completas.

---

### Navegación

**[← Anterior](arquitectura.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](instalacion_linux.md)**
