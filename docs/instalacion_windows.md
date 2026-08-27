# Guía de Instalación y Uso en Windows

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
