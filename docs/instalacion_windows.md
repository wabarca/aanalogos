# Guía de Instalación y Uso en Windows



## Contenido

1. [Requisitos](#1-requisitos)
2. [Instalación Paso a Paso](#2-instalación-paso-a-paso)
3. [Ejecución de la Aplicación](#3-ejecución-de-la-aplicación)
4. [Configuración Institucional (`config/institution.yaml`)](#4-configuración-institucional-configinstitutionyaml)

---
Instrucciones para instalar y ejecutar **AAnalogos** en estaciones de trabajo con Windows 10 u 11.

---

## 1. Requisitos
* Python 3.10, 3.11, 3.12 o 3.13 (o distribución Conda / Miniforge).
* Git para Windows (opcional).

---

## 2. Instalación Paso a Paso

1. Abra PowerShell o Windows Terminal en la carpeta del proyecto.
2. Cree un entorno virtual:
```powershell
python -m venv .venv
```
3. Active el entorno virtual:
```powershell
.venv\Scripts\Activate.ps1
```
*(Si PowerShell bloquea la ejecución de scripts, ejecute previamente: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`).*

4. Instale las dependencias:
```powershell
pip install -r requirements.txt
```

5. Ejecute la verificación de pruebas:
```powershell
python -m unittest discover -s tests
```

---

## 3. Ejecución de la Aplicación

### Modo Interfaz Web (Streamlit)
```powershell
streamlit run app.py
```
La aplicación se abrirá automáticamente en su navegador en `http://localhost:8501`.

### Modo Terminal / CLI (Compatibilidad)
```powershell
python aanlogos_v3.py
```

---

## 4. Configuración Institucional (`config/institution.yaml`)

Para adaptar el nombre institucional, división y logotipo en Windows:

1. Abra y edite el archivo `config\institution.yaml` con el Bloc de Notas o su editor preferido:
```yaml
institution:
  name: "Nombre Oficial de su Institución"
  division: "Nombre de la División o Departamento"
  logo: "docs/img/su_logo.png"  # Archivo PNG (opcional)
```
2. Guarde su imagen en formato `.png` dentro de `docs/img/` o en una ruta accesible. Si se omite, la interfaz se mostrará en formato neutro.
3. Al reiniciar `streamlit run app.py`, los cambios se reflejarán de inmediato.

---

### Navegación

**[← Anterior](instalacion_linux.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](despliegue_institucional.md)**
