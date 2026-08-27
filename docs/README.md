# Índice General de Documentación — Sistema `aanalogos`

Bienvenido a la documentación técnica, científica y operacional del sistema **AAnalogos**, desarrollado y adaptado para la **Gerencia de Meteorología** del **Ministerio de Medio Ambiente y Recursos Naturales (MARN)** de El Salvador.

La documentación está organizada de forma modular y secuencial para facilitar su consulta y lectura integral.

---

## Estructura de la Documentación

### 1. Fundamento Científico y Climatológico
* [**Metodología de Años Análogos**](metodologia.md): Formulación matemática, ventanas móviles de 6 meses (intra e interanuales), métricas de correlación de Pearson ($r$), distancia absoluta media (MAD), criterios de coincidencia y ordenamiento por ranking.
* [**Validación Climatológica**](validacion_climatologica.md): Justificación física de la exclusión del año objetivo, requerimiento de ventanas completas, aislamiento de valores sentinela, tratamiento de cobertura temporal asimétrica y certificación del caso benchmark.
* [**Fichas Técnicas de Índices Climáticos**](indices.md): Catálogo detallado de las 19 oscilaciones climáticas (definición física, cobertura histórica, dominios geográficos, períodos base climatológicos y fuentes oficiales).
* [**Referencias Bibliográficas y Atribución**](referencias.md): 19 publicaciones científicas primarias con DOIs verificados, fuentes operacionales de datos y sección oficial de antecedentes y autoría.

### 2. Arquitectura y Uso del Sistema
* [**Arquitectura de Software**](arquitectura.md): Estructura del paquete modular `aanalogos/`, flujo de datos por capas desacopladas, API pública e interfaz web en Streamlit.
* [**Manual de Usuario**](manual_usuario.md): Guía interactiva paso a paso para meteorólogos y climatólogos (configuración de parámetros, interpretación de KPIs, matriz de trazabilidad y exportación).
* [**Protocolo de Reproducibilidad**](reproducibilidad.md): Instrucciones para verificar de manera independiente el benchmark de referencia y la suite formal de pruebas.

### 3. Instalación, Despliegue y Mantenimiento
* [**Guía de Instalación en Linux**](instalacion_linux.md): Despliegue en servidores Ubuntu 22.04 LTS+ / Debian, entornos virtuales y configuración de red.
* [**Guía de Instalación en Windows**](instalacion_windows.md): Instalación y ejecución local en estaciones de trabajo Windows 10/11.
* [**Despliegue Institucional y Red Local (LAN)**](despliegue_institucional.md): Arquitectura de servicio continuo mediante `systemd` y acceso en red institucional (`0.0.0.0:8501`).
* [**Manual de Mantenimiento y Operaciones**](mantenimiento.md): Procedimientos para la actualización periódica de series, control de calidad, inspección de logs y respaldo.

### 4. Informes de Auditoría y Certificación
* [**Auditoría Histórica de Fases 1 y 2**](auditoria.md): Registro de las auditorías previas de refactorización y validación.
* [**Auditoría Final de Cierre**](auditoria_final_cierre.md): Evaluación independiente de consistencia metodológica, bibliográfica, de seguridad y dictamen institucional.
* [**Auditoría Estructural del Repositorio**](auditoria_repositorio.md): Informe de saneamiento, organización de directorios y control de exclusiones Git.
* [**Informe de Preparación Institucional**](informe_preparacion_institucional.md): Informe formal de cierre para la Dirección del Observatorio de Amenazas y Recursos Naturales.

---

### Navegación

**[← Volver al README Principal](../README.md)** · **[Comenzar Lectura: Metodología →](metodologia.md)**
