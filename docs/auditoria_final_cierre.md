# Informe de Auditoría Final de Cierre (`docs/auditoria_final_cierre.md`)

**Fecha de Emisión:** 2026-08-27  
**Proyecto:** AAnalogos — Sistema Computacional de Selección de Años Análogos Climáticos  
**Institución:** Gerencia de Meteorología, Dirección del Observatorio de Amenazas y Recursos Naturales, Ministerio de Medio Ambiente y Recursos Naturales (MARN), Gobierno de El Salvador  
**Responsable Técnico:** William Abarca (`wabarca@ambiente.gob.sv`)

---

## 1. Resumen Ejecutivo

El presente informe constituye la **auditoría final independiente de consistencia científica, climatológica, metodológica, bibliográfica y operacional** del sistema `aanalogos`. La auditoría fue realizada sobre el estado real, físico y ejecutable del repositorio, evaluando tanto la pureza algorítmica de la implementación computacional como la validez teórica y las limitaciones intrínsecas de la metodología climatológica.

### Principales Conclusiones:
1. **Motor Científico:** La implementación en Python del paquete `aanalogos` es matemáticamente rigurosa, determinista, libre de efectos colaterales (`print`), indexada estrictamente por año calendario (`YEAR`), aislada de sentinelas (`|x| > 50 \to \text{NaN}`) y preserva precisión en `float64` nativo.
2. **Suite de Pruebas y Benchmark:** 9 de 9 pruebas automatizadas pasan satisfactoriamente (`Ran 9 tests in 9.99s, OK`), verificando invarianza ante reordenamiento de filas y paridad matemática del **100.00%** contra el benchmark oficial de 2015 / Octubre / `AMO + PDO + TNA` (72 candidatos, 216 evaluaciones, TOP 7 idéntico con coincidencia `Total = 2`).
3. **Validez Climatológica:** La metodología opera mediante evaluación univariada independiente con acumulación lineal de coincidencias booleanas. No realiza estandarización inter-índice debido a que las métricas ($r$ y MAD) se evalúan de forma desacoplada dentro del espacio métrico de cada oscilación frente a umbrales específicos calibrados empíricamente.
4. **Seguridad y Portabilidad:** Se verificó la ausencia total de credenciales, secretos o rutas locales fijas del desarrollador en el código de producción.
5. **Dictamen Final:** El sistema se dictamina como **APTO CON LIMITACIONES**, detallando con absoluta transparencia las restricciones metodológicas del enfoque de análogos y los aspectos operativos que requieren gestión de red en la infraestructura del MARN.

---

## 2. Estado del Motor Científico y Auditoría Metodológica

A continuación se audita cada componente lógico del motor computacional contrastando la especificación teórica con el código fuente real:

| Componente Metodológico | Estado de Auditoría | Evidencia Concreta en Código | Justificación y Análisis Técnico |
| :--- | :---: | :--- | :--- |
| **Definición de Año Objetivo ($Y_{\text{obj}}$)** | **CORRECTO** | `engine.py:46`, `engine.py:73` | Se recibe como parámetro entero explícito. No se utiliza `.iloc[-1]`. Se busca mediante coincidencia exacta `df["YEAR"] == year_objetivo`. |
| **Definición de Mes Objetivo ($m_{\text{obj}}$)** | **CORRECTO** | `engine.py:47`, `windows.py:27` | Entero $1 \le m \le 12$ que define el mes de cierre de la ventana semestral retrospectiva. |
| **Construcción de Ventana Temporal (6 meses)** | **CORRECTO** | `windows.py:24-60` | Extrae exactamente un vector de 6 meses continuos $[m-5..m]$. |
| **Ventanas Intra-anuales ($m \ge 6$)** | **CORRECTO** | `windows.py:34-39` | Slicing directo de 6 columnas consecutivas dentro de la fila del año $Y$. |
| **Ventanas Interanuales ($m < 6$)** | **CORRECTO** | `windows.py:40-57` | Concatena los últimos $(6-m)$ meses del año $Y-1$ con los primeros $m$ meses del año $Y$. |
| **Etiquetado del Candidato Interanual** | **CORRECTO** | `windows.py:45`, `engine.py:100` | El candidato se etiqueta **estrictamente con el año de cierre $Y$**, coherente con la convención climatológica. |
| **Ventana del Año Objetivo** | **CORRECTO** | `engine.py:73-82` | Se valida que el vector objetivo no contenga `NaN`. Si falta algún dato, se invalida el cálculo. |
| **Ventana de Años Candidatos** | **CORRECTO** | `engine.py:98-105` | Extrae el vector para cada año histórico de la serie; si contiene `NaN`, se descarta como candidato. |
| **Exclusión del Año Objetivo** | **CORRECTO** | `engine.py:114` | Filtro explícito `anios_comunes = [y for y in anios_comunes if y != year_objetivo]`. Evita autocorrelación $r=1.0000$. |
| **Intersección Temporal Común ($\mathcal{H}_{\text{común}}$)** | **CORRECTO** | `engine.py:109-112` | Se calcula como la intersección de conjuntos `set.intersection(*conjuntos_anios)`. Garantiza que todos los índices evalúen exactamente los mismos años. |
| **Tratamiento de Datos Incompletos / NaN** | **CORRECTO** | `quality.py:53-58`, `windows.py:59` | Cualquier celda faltante invalida la ventana de 6 meses; no se realiza imputación artificial. |
| **Aislamiento de Sentinelas (`-99.99`, `99.99`)** | **CORRECTO** | `quality.py:36-37` | Condición vectorizada `df_clean[cols] = df_clean[cols].mask(df_clean[cols].abs() > 50, np.nan)`. |
| **Cálculo de Correlación de Pearson ($r$)** | **CORRECTO** | `metrics.py:28-31` | `scipy.stats.pearsonr` en precisión `float64` nativa. Maneja arrays constantes retornando $r = \text{NaN}$. |
| **Cálculo de Distancia MAD** | **CORRECTO** | `metrics.py:33` | `np.average(np.abs(arr_obj - arr_cand))` (Mean Absolute Difference entre vectores). |
| **Criterio de Coincidencia** | **CORRECTO** | `metrics.py:34` | `(r > r_umbral) and (mad < mad_umbral)`. Booleano estricto (1 o 0). |
| **Cálculo de Coincidencia Total** | **CORRECTO** | `engine.py:136` | Suma aritmética entera de coincidencias univariadas `df_coincidencias["Total"] = df_coincidencias.sum(axis=1)`. |
| **Ordenamiento y Ranking** | **CORRECTO** | `engine.py:137` | `sort_values(by=["Total", "YEAR"], ascending=[False, False])`. Desempata por año más reciente. |
| **Selección del Top-N** | **CORRECTO CON LIMITACIÓN** | `app.py:149`, `aanlogos_v3.py:103` | La visualización presenta el Top 10 o Top N por diseño de interfaz, mientras que el objeto `ResultadoAnalogos` contiene **todos** los candidatos evaluados. |
| **Asimetría Temporal entre Índices** | **CORRECTO CON LIMITACIÓN** | `engine.py:109-115` | Si se combina un índice de 1950 (`AMO`) con uno de 1982 (`SSTA_34`), el universo se acota a 1982–2026. Es matemáticamente correcto pero restringe el período muestral. |

---

## 3. Auditoría de Validez Climatológica

### 3.1 Uso de Pearson ($r$) y Distancia ($\text{MAD}$)
* **Coherencia Física:** La combinación de Pearson y MAD es físicamente sólida:
  * **Pearson ($r$):** Mide la **similitud en la tendencia y fase temporal** del modo climático a lo largo del semestre (e.g. calentamiento progresivo vs enfriamiento relativo).
  * **MAD:** Mide la **cercanía en la amplitud física real** de la anomalía (e.g. diferencia en grados Celsius o unidades estandarizadas).
* **Ausencia de Estandarización Inter-índice:** La metodología **no requiere estandarización previa entre índices** porque las comparaciones nunca cruzan variables diferentes. La evaluación se realiza de forma univariada dentro del dominio físico de cada índice contra sus propios umbrales predefinidos ($r_{\text{umbral}}$ y $\text{MAD}_{\text{umbral}}$).

### 3.2 Combinación Lineal de Coincidencias (`Total`)
* **Naturaleza del Algoritmo:** El método no es un análisis multivariado conjunto (e.g. distancia de Mahalanobis o EOF multivariada), sino una **acumulación discreta de coincidencias univariadas independientes**:
  $$\text{Total}(Y) = \sum_{k=1}^{K} \mathbb{I}\left(r_k(Y) > r_{\text{umbral}, k} \land \text{MAD}_k(Y) < \text{MAD}_{\text{umbral}, k}\right)$$
* **Ventaja Operativa:** Alta interpretabilidad para el meteorólogo de turno; permite saber con exactitud qué forzantes coincidieron y cuáles no.
* **Limitación Climatológica:** Asigna el mismo peso (peso unitario) a todos los índices seleccionados, independientemente de si un forzante específico (e.g. ENOS) ejerce una modulación física dominante sobre la región centroamericana respecto a otro (e.g. AO).

---

## 4. Auditoría de los 19 Índices Climáticos

A continuación se detalla la matriz de auditoría de cada una de las 19 series integradas:

| Código | Nombre Oficial | Variable Física | Unidades | Cobertura | Período Climatológico | Sentinelas | Fuente Operacional | Referencia Científica Primaria | DOI / Enlace | Estado |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **AMO** | Atlantic Multidecadal Oscillation | Anomalía TSM Atlántico Norte ($0^\circ-70^\circ\text{N}$) | $^\circ\text{C}$ | 1950–2023 | 1951–2000 (detrended) | `-99.99` | NOAA PSL | Enfield et al. (2001) | [10.1029/2000GL012745](https://doi.org/10.1029/2000GL012745) | **Auditado OK** |
| **AO** | Arctic Oscillation | Anomalía Altura Geopotencial 1000 hPa ($20^\circ-90^\circ\text{N}$) | Std | 1950–2026 | 1979–2000 | `-999.0` | NOAA CPC | Thompson & Wallace (1998) | [10.1029/98GL00950](https://doi.org/10.1029/98GL00950) | **Auditado OK** |
| **MEI** | Multivariate ENSO Index v2 | Combinación EOF (SLP, SST, Vientos, OLR) | Std | 1950–2026 | 1980–2018 | `-999.0` | NOAA PSL | Wolter & Timlin (2011) / Zhang et al. (2019) | [10.1002/joc.2336](https://doi.org/10.1002/joc.2336) | **Auditado OK** |
| **ONI** | Oceanic Niño Index | Media móvil 3 meses TSM Niño 3.4 (ERSSTv5) | $^\circ\text{C}$ | 1950–2026 | Climatología móvil 30 años | `-99.99` | NOAA CPC | Huang et al. (2017) | [10.1175/JCLI-D-16-0836.1](https://doi.org/10.1175/JCLI-D-16-0836.1) | **Auditado OK** |
| **NAO** | North Atlantic Oscillation | Diferencia de presión SLP / EOF 500 hPa | Std | 1950–2026 | 1950–2000 | `-99.90` | NOAA CPC/PSL | Hurrell (1995) | [10.1126/science.269.5224.676](https://doi.org/10.1126/science.269.5224.676) | **Auditado OK** |
| **PDO** | Pacific Decadal Oscillation | Primera EOF de anomalías TSM Pacífico Norte | Std | 1946–2026 | 1971–2000 | `99.99` | NOAA NCEI | Mantua et al. (1997) | [10.1175/1520-0477(1997)078<1069:APICOW>2.0.CO;2](https://doi.org/10.1175/1520-0477(1997)078<1069:APICOW>2.0.CO;2) | **Auditado OK** |
| **TNA** | Tropical Northern Atlantic | Promedio anomalía TSM ($5.5^\circ-23.5^\circ\text{N}, 15^\circ-57.5^\circ\text{W}$) | $^\circ\text{C}$ | 1950–2026 | 1971–2000 | `-99.99` | NOAA PSL | Enfield & Alfaro (1999) | [10.1175/1520-0442(1999)012<2781:POIRAI>2.0.CO;2](https://doi.org/10.1175/1520-0442(1999)012<2781:POIRAI>2.0.CO;2) | **Auditado OK** |
| **SSTA_12** | Niño 1+2 SST Anomaly | Anomalía TSM OISST.v2 ($0^\circ-10^\circ\text{S}, 90^\circ-80^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **SSTA_3** | Niño 3 SST Anomaly | Anomalía TSM OISST.v2 ($5^\circ\text{N}-5^\circ\text{S}, 150^\circ-90^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **SSTA_4** | Niño 4 SST Anomaly | Anomalía TSM OISST.v2 ($5^\circ\text{N}-5^\circ\text{S}, 160^\circ\text{E}-150^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **SSTA_34** | Niño 3.4 SST Anomaly | Anomalía TSM OISST.v2 ($5^\circ\text{N}-5^\circ\text{S}, 170^\circ-120^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **AtlTROP** | Tropical Atlantic SST | Anomalía TSM ($10^\circ\text{S}-10^\circ\text{N}, 0^\circ-360^\circ$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **SAtl** | South Atlantic SST | Anomalía TSM ($0^\circ-20^\circ\text{S}, 30^\circ\text{E}-60^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **NAtl** | North Atlantic SST | Anomalía TSM ($5^\circ-20^\circ\text{N}, 30^\circ\text{E}-60^\circ\text{W}$) | $^\circ\text{C}$ | 1982–2026 | 1991–2020 | `-99.99` | NOAA CPC | Reynolds et al. (2002) | [10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2](https://doi.org/10.1175/1520-0442(2002)015<1609:AIISAS>2.0.CO;2) | **Auditado OK** |
| **CAR** | Caribbean SST Index | Anomalía TSM Caribe ($10^\circ-20^\circ\text{N}, 85^\circ-60^\circ\text{W}$) | $^\circ\text{C}$ | 1950–2020 | 1981–2010 | `-99.99` | NOAA PSL | Enfield & Alfaro (1999) | [10.1175/1520-0442(1999)012<2781:POIRAI>2.0.CO;2](https://doi.org/10.1175/1520-0442(1999)012<2781:POIRAI>2.0.CO;2) | **Auditado OK (Estático)** |
| **WHWP** | Western Hemisphere Warm Pool | Anomalía de Área TSM $>28.5^\circ\text{C}$ | $10^6\text{ km}^2$ | 1950–2026 | 1971–2000 | `-99.99` | NOAA PSL | Wang & Enfield (2001) | [10.1029/2000GL011763](https://doi.org/10.1029/2000GL011763) | **Auditado OK** |
| **PNA** | Pacific-North American | EOF de Geopotencial 500 hPa | Std | 1950–2026 | 1981–2010 | `-99.90` | NOAA CPC/PSL | Wallace & Gutzler (1981) | [10.1175/1520-0493(1981)109<0784:TITGHF>2.0.CO;2](https://doi.org/10.1175/1520-0493(1981)109<0784:TITGHF>2.0.CO;2) | **Auditado OK** |
| **SOI** | Southern Oscillation Index | Diferencia SLP Tahití - Darwin normalizada | Std | 1953–2021 | 1981–2010 | `-999.0` | NOAA CPC/PSL | Troup (1965) / Trenberth (1984) | [10.1002/qj.49709139009](https://doi.org/10.1002/qj.49709139009) | **Auditado OK (Hasta 2021)** |
| **AMO_CSU** | AMO Colorado State Univ. | Anomalía TSM filtrada polinomialmente | $^\circ\text{C}$ | 1950–2026 | 1982–2010 | `-99.99` | CSU TMP | Klotzbach & Gray (2008) | [10.1175/2008JCLI2162.1](https://doi.org/10.1175/2008JCLI2162.1) | **Auditado OK** |

---

## 5. Auditoría Bibliográfica

Se verificó exhaustivamente el documento [`docs/referencias.md`](referencias.md):
1. **Comprobación de Publicaciones:** Las 19 citas primarias corresponden a publicaciones científicas reales publicadas en revistas indexadas (*Journal of Climate*, *Geophysical Research Letters*, *Science*, *Bulletin of the AMS*, *Monthly Weather Review*, *Tellus A*).
2. **Correspondencia de DOIs:** Todos los enlaces DOI resuelven con exactitud a los artículos correspondientes.
3. **Distinción entre Definición Teórica y Fuente Operacional:** La documentación diferencia formalmente entre los autores que definieron originalmente el índice y la institución actual (e.g. NOAA PSL, NOAA CPC) que calcula y distribuye los datos operativos.

---

## 6. Auditoría de Fuentes de Datos e Ingesta

1. **Correspondencia Inequívoca:**
   * Archivo de configuración: [`config/data_sources.yaml`](../config/data_sources.yaml).
   * Directorio físico: [`data/`](../data).
   * Parsers de datos: [`aanalogos/data.py`](../aanalogos/data.py).
2. **Encabezados Especiales y Footers:**
   * Las funciones `acomodaParaCSV` procesan las líneas de texto omitiendo los encabezados y footers descriptivos de la NOAA (`skiprows`, `skipfooter`).
3. **Series Estáticas / Discontinuadas:**
   * `CAR` (Caribbean SST): La NOAA PSL discontinuó la actualización automática de este archivo en formato tradicional en 2020.
   * `SOI` (formato PSL): La serie local llega hasta 2021.
   * *Diagnóstico:* El motor valida correctamente si el usuario solicita estas series para años posteriores a su cobertura, devolviendo un error explícito de disponibilidad sin alterar los datos históricos válidos.

---

## 7. Certificación del Benchmark Oficial

Se ejecutó la prueba de regresión automatizada sobre el benchmark oficial:
* **Parámetros:** Año objetivo = `2015`, Mes objetivo = `10` (Octubre), Índices = `AMO` + `PDO` + `TNA`.
* **Años Históricos Evaluados ($\mathcal{H}_{\text{común}}$):** Exactamente **72 años** ($1950..2022 \setminus \{2015\}$).
* **Evaluaciones Índice-Año:** Exactamente **216 registros**.
* **TOP 7 Años Análogos Obtenidos (Total = 2):**
  1. `2021` (AMO=1, PDO=1, TNA=0)
  2. `2014` (AMO=1, PDO=1, TNA=0)
  3. `2012` (AMO=1, PDO=1, TNA=0)
  4. `2003` (AMO=1, PDO=1, TNA=0)
  5. `2001` (AMO=1, PDO=1, TNA=0)
  6. `1990` (AMO=1, PDO=1, TNA=0)
  7. `1957` (AMO=1, PDO=1, TNA=0)
* **Paridad Matemática:** **100.00%** idéntica.

---

## 8. Auditoría de Casos Límite y Robustez

Se desarrollaron y evaluaron pruebas automatizadas de casos límite (`scratch/audit_edge_cases_and_env.py`):

1. **Año objetivo al inicio de la serie (1950, M10):** El sistema calcula correctamente con los 72 candidatos posteriores.
2. **Año objetivo al inicio con ventana que cruza año (1950, M2):** Rechazado correctamente (`AMO` no tiene datos en 1949).
3. **Año objetivo reciente con datos faltantes (2024, M10):** Rechazado con mensaje explícito indicando que `AMO` no cuenta con ventana completa para 2024.
4. **Evaluación de un único índice (2015, M10, `AMO`):** Funciona correctamente, retornando candidatos con $\text{Total} \in \{0, 1\}$.
5. **Evaluación de 14 índices simultáneos:** Intersección temporal reduce el universo a 40 años ($1982–2022$), funcionando sin errores numéricos.
6. **Asimetría temporal (1950 vs 1982):** Intersección temporal calculada correctamente en $1982–2022$.
7. **Año objetivo incompatible con la serie (1960 con `SSTA_34`):** Rechazado de forma estricta.
8. **Invarianza ante reordenamiento aleatorio de filas (Shuffle):** 0 discrepancias numéricas ($\Delta = 0$).
9. **Entrada con filas de año duplicadas:** Manejada de forma determinista mediante indexación por `YEAR`.

---

## 9. Auditoría de Reproducibilidad y Entorno Computacional

* **Comando de Verificación:** `python -m unittest discover -s tests -v`
* **Resultado:** **Ran 9 tests in 9.994s — OK (9 passed / 0 failed)**.
* **Entorno Computacional Auditado:**
  * **Sistema Operativo:** Windows 11 / Compatible con Linux (Ubuntu 22.04 LTS+, Debian 11/12).
  * **Python:** `3.13.15` (Soporta `3.10`, `3.11`, `3.12`, `3.13`).
  * **Pandas:** `3.0.4`
  * **NumPy:** `2.5.0`
  * **SciPy:** `1.18.0`
  * **Streamlit:** `1.62.0`
  * **Matplotlib:** `3.11.0`

---

## 10. Auditoría de Despliegue Linux y Red Institucional (LAN)

1. **Configuración de Servicio:**
   * Archivo: [`deploy/aanalogos.service`](../deploy/aanalogos.service).
   * Usuario de ejecución: `clima` (sin privilegios de superusuario / root).
   * Directorio de trabajo: `/opt/aanalogos`.
   * Reinicio automático: `Restart=on-failure`, `RestartSec=5s`.
   * Logs centralizados en `journalctl -u aanalogos`.
2. **Acceso Web en Red Local (LAN):**
   * Script: [`deploy/run_server.sh`](../deploy/run_server.sh).
   * Enlace de red: `0.0.0.0:8501` (permite conexión directa desde cualquier PC conectada a la red del MARN).
3. **Limitación Operativa Identificada:**
   * Streamlit en modo básico no incluye autenticación de usuarios integrada. Para acceso institucional seguro, el servidor debe estar protegido dentro de la LAN institucional o detrás de un proxy inverso con autenticación.

---

## 11. Auditoría de Seguridad Operacional

1. **Credenciales y Secretos:** Inspección regex confirma **cero contraseñas, tokens o llaves API** en el repositorio.
2. **Permisos de Archivos:** El servicio no requiere privilegios elevados y opera en modo de solo lectura sobre el directorio `data/` durante las consultas interactivas.
3. **Concurrencia:** Streamlit gestiona sesiones concurrentes independientes por cada usuario conectado a través de la LAN institucional.

---

## 12. Atribución y Metadata

1. **Código Fuente (`.py`):** Completamente limpio de encabezados, banners, docstrings de autoría heredada o referencias directas que atribuyan la autoría actual al IMN o al autor original.
2. **Documentación Institucional:** Registra de forma transparente la distinción entre el antecedente original (Anthony Segura García, UCR/IMN) y la presente versión reestructurada, rediseñada y validada para el MARN por **William Abarca** (`wabarca@ambiente.gob.sv`).

---

## 13. Limitaciones Metodológicas y Operacionales Conocidas

1. **Naturaleza Diagnóstica (No Determinista):** Los años análogos identifican escenarios históricos con forzantes oceánicos y atmosféricos similares; **no constituyen por sí mismos un pronóstico determinista** de precipitación o temperatura futura.
2. **Ponderación Igualitaria de Índices:** El cálculo del puntaje `Total` suma coincidencias univariadas con pesos iguales, sin ponderar la influencia estacional diferenciada de cada forzante en Centroamérica.
3. **Series Discontinuadas por la Fuente:** `CAR` (hasta 2020) y `SOI` (hasta 2021) no se actualizan automáticamente en el formato tradicional de texto plano de la NOAA PSL.

---

## 14. Recomendaciones para la Operación Institucional (MARN)

1. **Configuración de Firewall:** Permitir el puerto `8501/tcp` únicamente a las IPs pertenecientes a la red interna del MARN (`192.168.x.x` o subred institucional correspondiente).
2. **Actualización Periódica de Datos:** Ejecutar mensualmente `python scripts/download_data.py` seguido de `python scripts/audit_sources.py` para mantener actualizadas las series de la NOAA.
3. **Capacitación al Personal Operativo:** Socializar el [`docs/manual_usuario.md`](manual_usuario.md) y [`docs/metodologia.md`](metodologia.md) con el equipo de meteorólogos y climatólogos de turno.

---

## 15. Dictamen Final

Con base en la auditoría exhaustiva e independiente del código, las pruebas formales, la validación bibliográfica y las especificaciones de despliegue, el proyecto **AAnalogos** se dictamina formalmente como:

# **APTO CON LIMITACIONES**

### Justificación del Dictamen:
* **APTO:** El software es computacionalmente correcto, determinista, seguro, portable, completamente documentado y reproduce el 100% de la paridad matemática del benchmark certificado.
* **CON LIMITACIONES:** Debido a que la metodología climatológica de años análogos es de naturaleza empírico-estadística no determinista, utiliza ponderación discreta lineal de índices, y la aplicación web Streamlit debe ser operada exclusivamente dentro de una red institucional protegida (LAN) al carecer de módulo de autenticación propio.
