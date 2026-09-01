# AAnalogos — Sistema de Selección de Años Análogos Climáticos

**Ministerio de Medio Ambiente y Recursos Naturales (MARN)**  
**Dirección del Observatorio de Amenazas y Recursos Naturales — Gerencia de Meteorología**  
*San Salvador, El Salvador*

---

## Descripción General

**AAnalogos** es un sistema computacional interactivo y modular para la **identificación y análisis multivariado de años análogos climáticos**, diseñado como herramienta de diagnóstico y apoyo para la **predicción climática estacional y el seguimiento del ENOS en Centroamérica**.

La formulación matemática fundamental de similitud, incluyendo la correlación de Pearson, la distancia absoluta media (MAD), el tratamiento de valores faltantes, la exclusión del año objetivo y los criterios históricos de coincidencia, se preserva respecto al benchmark validado. La aplicación incorpora extensiones operacionales explícitas, particularmente una ventana retrospectiva de doce meses y mecanismos de actualización y determinación automática del período disponible.

La aplicación evalúa de forma simultánea hasta **21 índices oceánicos y atmosféricos** (Pacífico, Atlántico, Ártico y atmósfera global), comparando la trayectoria reciente frente al registro histórico mediante **correlación de Pearson ($r$)** y **diferencia absoluta media (MAD)** con estricta validación de anomalías térmicas y barométricas.

---

## Características Principales

* 🌦️ **Operación Automática:** Detección dinámica del año actual y del último mes operacional disponible respetando la regla de publicación ($M+1$) con ventana de 12 meses predeterminada.
* 🕰️ **Reanálisis y Backtesting:** Soporte para reanálisis retrospectivo completo frente a todo el registro histórico y backtesting estricto con corte temporal ($Y_{\text{cand}} \le Y_{\text{obj}}$).
* 📐 **Ventana Paramétrica (12 vs 6 Meses):** Soporte operacional para ciclo anual completo (12 meses) y ventana metodológica histórica (6 meses).
* 📊 **Explorador de Índices y Tablas:** Fichas técnicas, metadatos, fuentes oficiales, DOIs, series temporales interactivas y tablas de datos históricos con descarga en CSV para las 21 oscilaciones.
* 📚 **Metodología Integrada:** Documentación científica interactiva con fórmulas KaTeX y explicación física de cada métrica y tipología de variable.
* 🔄 **Actualización Atómica:** Descarga y validación no destructiva de las fuentes remotas oficiales (NOAA/CPC/PSL/CSU).
* ⚙️ **Umbrales Configurables:** Personalización de criterios de coincidencia por índice con trazabilidad y botón de restauración oficial.
* 🏛️ **Desacoplamiento Institucional:** Personalización sencilla del nombre, división y logotipo en `config/institution.yaml` para despliegue regional en cualquier servicio meteorológico.
* 🛡️ **Rigor Científico Certificado:** Precisión `float64` nativa, aislamiento de valores sentinela (`-99.99`), exclusión del año objetivo ($Y_{\text{cand}} \neq Y_{\text{obj}}$), verificación de anomalías térmicas y suite automatizada de más de 90 pruebas unitarias.

---

## 21 Índices Climáticos Integrados

| Pacífico & ENOS | Atlántico & Caribe | Atmósfera & Hemisferio Norte |
| :--- | :--- | :--- |
| **ONIv5** (ONI basado en ERSSTv5) | **AMO** (Kaplan SST) | **AO** (Arctic Oscillation) |
| **ONIv6** (ONI basado en ERSSTv6) | **AMO_CSU** (Colorado State Univ.) | **NAO** (North Atlantic Oscillation) |
| **RONI** (Relative Oceanic Niño Index) | **TNA** (Tropical Northern Atlantic) | **PNA** (Pacific-North American) |
| **MEI** (Multivariate ENSO v2) | **CAR** (Caribbean SST Index) | |
| **SOI** (Southern Oscillation Index) | **AtlTROP** (Tropical Atlantic) | |
| **SSTA_12** (Niño 1+2) | **NAtl** (North Atlantic) | |
| **SSTA_3** (Niño 3) | **SAtl** (South Atlantic) | |
| **SSTA_4** (Niño 4) | **WHWP** (Western Hemisphere Warm Pool) | |
| **SSTA_34** (Niño 3.4) | | |

---

## Instalación y Ejecución Rápida

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/wabarca/aanalogos.git
cd aanalogos
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Personalización Institucional (Opcional)
Edite `config/institution.yaml` con el nombre, división y logotipo de su institución.

### 3. Ejecutar Suite de Pruebas Automatizadas
```bash
python -m unittest discover -s tests -v
```

### 4. Iniciar la Aplicación Web
```bash
streamlit run app.py
```

---

## Estructura de Documentación

* [📚 Índice General de Documentación](docs/README.md)
* [🔬 Metodología Científica](docs/metodologia.md)
* [📊 Validación Climatológica](docs/validacion_climatologica.md)
* [📖 Manual de Usuario](docs/manual_usuario.md)
* [📈 Catálogo de Índices Climáticos](docs/indices.md)
* [📑 Referencias Bibliográficas y DOIs](docs/referencias.md)
* [🏗️ Arquitectura Técnica](docs/arquitectura.md)
* [🔁 Reproducibilidad y Benchmarks](docs/reproducibilidad.md)
* [🐧 Instalación en Linux](docs/instalacion_linux.md)
* [🪟 Instalación en Windows](docs/instalacion_windows.md)
* [🏛️ Despliegue Institucional](docs/despliegue_institucional.md)
* [🛠️ Manual de Mantenimiento](docs/mantenimiento.md)

---

## Licencia y Créditos Institucionales

* **Desarrollo y mantenimiento:**  
  **William Abarca**  
  Gerencia de Meteorología — Observatorio de Amenazas y Recursos Naturales  
  Ministerio de Medio Ambiente y Recursos Naturales
* **Licencia:** Código abierto para servicios meteorológicos e instituciones de investigación.
* **Fuentes Operacionales:** NOAA CPC, NOAA PSL, NOAA NCEI, Colorado State University (CSU).
* **Antecedente Histórico:** Metodología conceptual basada en los trabajos de Anthony Segura García (UCR / IMN Costa Rica).
