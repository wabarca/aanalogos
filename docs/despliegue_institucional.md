# Guía de Despliegue Institucional en Servidores Linux

**Documento:** `docs/despliegue_institucional.md`  
**Destinatarios:** Administradores de Sistemas, Gerencia de Informática y Gerencia de Meteorología, MARN El Salvador

## Contenido

1. [Arquitectura de Despliegue en Red Local (LAN)](#1-arquitectura-de-despliegue-en-red-local-lan)
2. [Ruta Estándar y Usuario de Producción](#2-ruta-estándar-y-usuario-de-producción)
3. [Procedimiento Automatizado de Despliegue](#3-procedimiento-automatizado-de-despliegue)
4. [Configuración y Estructura de la Unidad `systemd`](#4-configuración-y-estructura-de-la-unidad-systemd)
5. [Seguridad y Restricción de Firewall](#5-seguridad-y-restricción-de-firewall)
6. [Auditoría Operativa y Verificación del Servicio](#6-auditoría-operativa-y-verificación-del-servicio)

---

## 1. Arquitectura de Despliegue en Red Local (LAN)

```text
[ Estaciones de Trabajo / Meteorólogos (LAN MARN) ]
                       │
                       │ HTTP (Puerto 8501)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Servidor Institucional Linux (Ubuntu 22.04+ / Debian 12)    │
│                                                             │
│ Firewall (UFW): Permitir 8501/tcp desde 192.168.0.0/16      │
│                                                             │
│ Servicio systemd: aanalogos.service                         │
│ ├── Usuario del sistema: clima (sin acceso a shell)         │
│ ├── Directorio raíz: /opt/aanalogos                         │
│ ├── Entorno Python aislado: /opt/aanalogos/.venv            │
│ └── Servidor Web: Streamlit (0.0.0.0:8501, headless)        │
│                                                             │
│ Componentes del Sistema:                                    │
│ ├── app.py (Interfaz Web)                                   │
│ ├── aanalogos/ (Motor Climatológico Modular)                │
│ └── data/ (Matrices Históricas de 19 Índices)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Ruta Estándar y Usuario de Producción

Para garantizar aislamiento, mantenibilidad y cumplimiento de las políticas de infraestructura del MARN:

* **Ruta Estándar de Producción:** `/opt/aanalogos`
* **Usuario de Servicio Dedicado:** `clima` (creado como usuario del sistema con `/usr/sbin/nologin`).
* **Permisos del Directorio:** `750` (`rwxr-x---`) con propiedad `clima:clima`.

---

## 3. Procedimiento Automatizado de Despliegue

Para instalar o actualizar el servicio de forma determinista y reproducible:

```bash
# 1. Clonar el repositorio
git clone https://github.com/wabarca/aanalogos.git
cd aanalogos

# 2. Ejecutar el instalador institucional
sudo bash deploy/install_service.sh --opt
```

El script ejecuta automáticamente:
1. Creación del usuario `clima` (si no existe).
2. Instalación de archivos en `/opt/aanalogos`.
3. Creación y aprovisionamiento del entorno virtual `.venv`.
4. Asignación de permisos de ejecución a los scripts.
5. Generación de `/etc/systemd/system/aanalogos.service`.
6. Recarga del demonio (`systemctl daemon-reload`) y arranque inmediato (`enable --now`).

---

## 4. Configuración y Estructura de la Unidad `systemd`

La unidad `/etc/systemd/system/aanalogos.service` queda configurada de la siguiente forma:

```ini
[Unit]
Description=Servicio Web de Años Análogos Climáticos (AAnalogos Streamlit)
After=network.target

[Service]
Type=simple
User=clima
Group=clima
WorkingDirectory=/opt/aanalogos
Environment="PATH=/opt/aanalogos/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/aanalogos/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aanalogos

[Install]
WantedBy=multi-user.target
```

---

## 5. Seguridad y Restricción de Firewall

Al tratarse de una herramienta institucional que no implementa autenticación nativa en Streamlit, el acceso debe ser restringido a la red local del MARN:

```bash
# Permitir únicamente conexiones desde la subred institucional
sudo ufw allow from 192.168.0.0/16 to any port 8501 proto tcp
sudo ufw reload
```

---

## 6. Auditoría Operativa y Verificación del Servicio

Tras la instalación, valide que el servicio se encuentre activo y escuchando en el puerto configurado:

```bash
# 1. Verificar estado en systemd
sudo systemctl status aanalogos.service

# 2. Verificar puerto de escucha en 0.0.0.0:8501
ss -ltnp | grep 8501

# 3. Monitorear logs de ejecución
journalctl -u aanalogos.service -f
```

---

### Navegación

**[← Anterior](instalacion_windows.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](mantenimiento.md)**
