# Informe Consolidado de Auditorías Científicas (Fases 1 y 2)

Este documento resume los hallazgos técnicos, climatológicos y las pruebas de certificación matemática realizadas sobre **AAnalogos**.

---

## 1. Resumen de Hallazgos y Correcciones Críticas

1. **Desfase Temporal en PDO:**  
   * *Diagnóstico:* En versiones preliminares, la lectura de PDO asumía una correspondencia posicional (`iloc`), generando un desfase temporal de 4 años ($1946$ vs $1950$).  
   * *Corrección:* Todas las operaciones entre series se indexaron estrictamente por la columna temporal `YEAR`.
2. **Aislamiento de Valores Sentinela:**  
   * *Diagnóstico:* Códigos como `-99.99` o `99.99` entraban a los cálculos de Pearson y MAD como si fuesen valores físicos reales de temperatura.  
   * *Corrección:* Sanitización estricta convirtiendo valores $|x| > 50$ a `NaN` e invalidando la ventana de cálculo.
3. **Exclusión del Año Objetivo:**  
   * *Diagnóstico:* El año objetivo era evaluado contra sí mismo, generando siempre un análogo trivial con $r=1.000$ y $\text{MAD}=0.000$.  
   * *Corrección:* Exclusión estricta de $Y_{\text{obj}}$ de la lista de candidatos.
4. **Ventanas Interanuales que Cruzan Año ($m < 6$):**  
   * *Diagnóstico:* Los meses de enero a mayo utilizaban ventanas con desplazamientos manuales erróneos.  
   * *Corrección:* Construcción continua de 6 meses ($(Y-1)$ a $Y$) etiquetada en el año de cierre $Y$.
5. **Cero Reducción Silenciosa de Índices:**  
   * *Diagnóstico:* Índices sin datos para el objetivo eran eliminados en silencio.  
   * *Corrección:* Validación estricta que exige cobertura del 100% de los índices solicitados.

---

## 2. Certificación de Invarianza y Precisión

* **Invarianza ante Shuffle:** Demostrada reordenando aleatoriamente las filas de todas las series históricas ($\Delta = 0$).
* **Precisión Flotante:** Preservada en `float64` nativo para $r$ y MAD en toda la cadena de cómputo.
