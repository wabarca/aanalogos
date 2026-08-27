# Guía de Instalación y Despliegue en Servidor Linux (Ubuntu / Debian)

## Contenido

1. [Requisitos Previos del Sistema](#1-requisitos-previos-del-sistema)
2. [Método Rápido: Instalación Automatizada con Script](#2-método-rápido-instalación-automatizada-con-script)
3. [Método Manual: Instalación en Ruta Estándar `/opt/aanalogos`](#3-método-manual-instalación-en-ruta-estándar-optaanalogos)
4. [Método Manual: Instalación en Directorio Personal o de Desarrollo](#4-método-manual-instalación-en-directorio-personal-o-de-desarrollo)
5. [Configuración de Red y Firewall (UFW)](#5-configuración-de-red-y-firewall-ufw)
6. [Control y Monitoreo del Servicio](#6-control-y-monitoreo-del-servicio)

---

Esta guía describe el procedimiento para desplegar **AAnalogos** en servidores o estaciones de trabajo institucionales con sistema operativo Linux (Ubuntu 22.04 LTS / 24.04 LTS o Debian 11 / 12), garantizando portabilidad e integración con `systemd`.

---

## 1. Requisitos Previos del Sistema

Actualice el sistema e instale los paquetes base de Python 3 y Git:
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

---

## 2. Método Rápido: Instalación Automatizada con Script

El repositorio incluye el instalador automatizado [`deploy/install_service.sh`](../deploy/install_service.sh), el cual detecta el entorno, configura el `.venv`, ajusta permisos y genera la unidad `systemd` correspondiente.

### A. Para Despliegue Estándar de Producción (en `/opt/aanalogos` con usuario `clima`)
```bash
# 1. Clonar el repositorio en cualquier ubicación temporal o de descarga
git clone https://github.com/wabarca/aanalogos.git
cd aanalogos

# 2. Ejecutar el instalador en modo institucional
sudo bash deploy/install_service.sh --opt
```
*El script creará el usuario del sistema `clima`, copiará los archivos a `/opt/aanalogos`, creará el entorno `.venv`, instalará `requirements.txt`, registrará la unidad en `/etc/systemd/system/aanalogos.service` y activará el servicio.*

### B. Para Despliegue In-Place (en el directorio actual donde se clonó el repositorio)
```bash
cd /ruta/donde/esta/el/repositorio/aanalogos
sudo bash deploy/install_service.sh --inplace
```
*El instalador configurará el servicio `systemd` para que se ejecute directamente desde la ruta actual utilizando el usuario propietario del directorio.*

---

## 3. Método Manual: Instalación en Ruta Estándar `/opt/aanalogos`

Si prefiere realizar la instalación paso a paso de forma manual:

1. **Crear usuario del sistema dedicado:**
   ```bash
   sudo useradd -r -s /usr/sbin/nologin -d /opt/aanalogos clima
   ```

2. **Clonar el proyecto y asignar permisos:**
   ```bash
   sudo git clone https://github.com/wabarca/aanalogos.git /opt/aanalogos
   sudo chown -R clima:clima /opt/aanalogos
   ```

3. **Crear el entorno virtual e instalar dependencias:**
   ```bash
   cd /opt/aanalogos
   sudo -u clima python3 -m venv .venv
   sudo -u clima .venv/bin/pip install --upgrade pip
   sudo -u clima .venv/bin/pip install -r requirements.txt
   ```

4. **Verificar la suite de pruebas:**
   ```bash
   sudo -u clima .venv/bin/python -m unittest discover -s tests -v
   ```
   *(Debe reportar `9 passed / 0 failed`).*

5. **Instalar y activar el servicio `systemd`:**
   ```bash
   sudo cp deploy/aanalogos.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now aanalogos.service
   ```

---

## 4. Método Manual: Instalación en Directorio Personal o de Desarrollo

Si el repositorio está clonado en un directorio personal (por ejemplo, `/home/usuario/workspace/aanalogos`):

1. **Crear y activar el entorno virtual local:**
   ```bash
   cd /home/usuario/workspace/aanalogos
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Ejecución Directa mediante Script de Red:**
   ```bash
   chmod +x deploy/run_server.sh
   ./deploy/run_server.sh
   ```

3. **O Registrar Servicio `systemd` Personalizado:**
   Cree `/etc/systemd/system/aanalogos.service` con la ruta real:
   ```ini
   [Unit]
   Description=Servicio Web de Años Análogos Climáticos (AAnalogos Streamlit)
   After=network.target

   [Service]
   Type=simple
   User=usuario
   WorkingDirectory=/home/usuario/workspace/aanalogos
   Environment="PATH=/home/usuario/workspace/aanalogos/.venv/bin:/usr/local/bin:/usr/bin:/bin"
   ExecStart=/home/usuario/workspace/aanalogos/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
   Restart=on-failure
   RestartSec=5s
   SyslogIdentifier=aanalogos

   [Install]
   WantedBy=multi-user.target
   ```
   Y active con:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now aanalogos.service
   ```

---

## 5. Configuración de Red y Firewall (UFW)

Para permitir el acceso a la aplicación web desde las estaciones de trabajo de la red institucional:

```bash
# Permitir tráfico entrante en el puerto 8501 (o restringido a subred interna)
sudo ufw allow 8501/tcp
sudo ufw reload
```

La aplicación quedará disponible en:
```text
http://<IP_DEL_SERVIDOR>:8501
```

---

## 6. Control y Monitoreo del Servicio

* **Consultar estado en vivo:** `sudo systemctl status aanalogos`
* **Verificar puerto de escucha:** `ss -ltnp | grep 8501`
* **Ver logs en tiempo real:** `journalctl -u aanalogos -f`
* **Reiniciar servicio:** `sudo systemctl restart aanalogos`
* **Detener servicio:** `sudo systemctl stop aanalogos`

---

### Navegación

**[← Anterior](manual_usuario.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](instalacion_windows.md)**
