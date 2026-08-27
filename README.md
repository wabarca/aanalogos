# AAnalogos: Sistema de Selección de Años Análogos Climáticos

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Tests](https://img.shields.io/badge/tests-9%20passed%20%7C%20100%25-brightgreen.svg)]()

**AAnalogos** es un sistema computacional y climatológico desarrollado para la identificación, evaluación y selección automatizada de **años análogos climáticos** mediante la comparación estadística multivariada de las principales oscilaciones e índices océano-atmosféricos globales y regionales.

---

## 1. Metodología Climatológica

La metodología compara una **ventana retrospectiva móvil de seis meses** del año objetivo ($Y_{\text{obj}}$) contra el registro histórico ($1950–2026$) a través de **19 índices climáticos**:

* **Métricas de Similitud:**
  * **Correlación de Pearson ($r$):** Evalúa la sincronía y forma de la trayectoria temporal.
  * **Distancia Absoluta Media (MAD):** Evalúa la cercanía en la magnitud y amplitud física de la anomalía.
* **Criterio de Coincidencia:** Un año histórico se declara análogo para un índice si cumple simultáneamente:
  $$r > r_{\text{umbral}} \quad \land \quad \text{MAD} < \text{MAD}_{\text{umbral}}$$
* **Ranking:** Los años candidatos se ordenan en forma descendente según el número total de índices coincidentes.

> ⚠️ **Aviso Climatológico:** El método de años análogos es una herramienta de diagnóstico y apoyo a la predicción climática estacional. **No constituye por sí mismo un pronóstico determinista del clima futuro.**

---

## 2. Índices Climáticos Contemplados (19 Series)

`AMO`, `AO`, `MEI`, `ONI`, `NAO`, `PDO`, `TNA`, `SSTA_12`, `SSTA_3`, `SSTA_4`, `SSTA_34`, `AtlTROP`, `SAtl`, `NAtl`, `CAR`, `WHWP`, `PNA`, `SOI`, `AMO_CSU`.

---

## 3. Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/wabarca/aanalogos.git
cd aanalogos

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar suite de pruebas
python -m unittest discover -s tests
```

---

## 4. Ejecución

### Interfaz Web Interactiva (Streamlit)
```bash
streamlit run app.py
```
Abra su navegador en `http://localhost:8501`.

### Despliegue en Red Local (LAN Institucional)
```bash
./deploy/run_server.sh
```
Accesible desde otros equipos de la red en `http://<IP_SERVIDOR>:8501`.

---

## 5. Estructura del Repositorio

```text
aanalogos/
├── app.py                  # Aplicación interactiva Streamlit
├── requirements.txt        # Dependencias fijadas
├── pyproject.toml          # Metadatos del paquete
├── CHANGELOG.md            # Historial de versiones
│
├── aanalogos/              # Motor climatológico modular (Python package)
│   ├── engine.py           # Orquestador (cero prints, validación estricta)
│   ├── metrics.py          # Cálculo de Pearson r y MAD en float64
│   ├── windows.py          # Construcción de ventanas semestrales
│   ├── quality.py          # Limpieza y control de sentinelas
│   └── data.py             # Ingesta y normalización
│
├── config/                 # Manifiesto YAML de fuentes de datos
├── data/                   # Series históricas de las 19 oscilaciones
├── docs/                   # Documentación científica y técnica completa (11 guías)
├── deploy/                 # Servicio systemd y scripts de arranque en red
├── scripts/                # Actualización y auditoría automatizada
└── tests/                  # Suite formal de pruebas automatizadas y regresión
```

---

## 6. Documentación Detallada

* **[Metodología Científica](docs/metodologia.md)**
* **[Fichas de los 19 Índices](docs/indices.md)**
* **[Referencias Bibliográficas (DOIs)](docs/referencias.md)**
* **[Manual de Usuario](docs/manual_usuario.md)**
* **[Arquitectura de Software](docs/arquitectura.md)**
* **[Instalación en Linux](docs/instalacion_linux.md)**
* **[Mantenimiento y Actualización](docs/mantenimiento.md)**
* **[Protocolo de Reproducibilidad](docs/reproducibilidad.md)**
* **[Auditoría Consolidada](docs/auditoria.md)**

---

## Antecedentes y Atribución

Este proyecto tiene como antecedente un código de cálculo de años análogos desarrollado originalmente por el meteorólogo **Anthony Segura García**, asociado a la **Universidad de Costa Rica** y al **Instituto Meteorológico Nacional de Costa Rica**. El código original sirvió como referencia para el desarrollo inicial de esta herramienta.

La versión actualmente contenida en este repositorio ha sido **completamente modificada, reestructurada, rediseñada, modularizada, auditada y validada** para su utilización en el contexto de la **Gerencia de Meteorología del Ministerio de Medio Ambiente y Recursos Naturales (MARN) de El Salvador**.

* **Desarrollo y rediseño de la versión actual:**  
  **William Abarca**  
  *Ministerio de Medio Ambiente y Recursos Naturales (MARN), El Salvador*  
  Contacto: [wabarca@ambiente.gob.sv](mailto:wabarca@ambiente.gob.sv)
