# Guía de Despliegue Institucional en Servidores Linux

**Documento:** `docs/despliegue_institucional.md`  
**Destinatarios:** Administradores de Sistemas, Gerencia de Informática y Gerencia de Meteorología, MARN El Salvador



## Contenido

1. [Arquitectura de Despliegue en Red Local (LAN)](#arquitectura-de-despliegue-en-red-local-lan)
2. [Procedimiento de Instalación Paso a Paso](#procedimiento-de-instalación-paso-a-paso)
3. [Configuración del Servicio `systemd`](#configuración-del-servicio-systemd)
4. [Configuración de Red y Seguridad](#configuración-de-red-y-seguridad)
5. [Buenas Prácticas de Seguridad](#buenas-prácticas-de-seguridad)

---
---

## 1. Arquitectura de Despliegue en Red Local (LAN)

```
[ Usuario en Red Institucional ]
             │
             │ HTTP (Puerto 8501)
             ▼
[ Servidor Linux (Ubuntu 22.04 LTS / Debian 12) ]
┌─────────────────────────────────────────────────────────────┐
│ Firewall (UFW): Permitir 8501/tcp desde 192.168.x.x         │
│                                                             │
│ Servicio systemd: aanalogos.service                         │
│ └── Usuario de sistema: clima (sin privilegios root)        │
│ └── Entorno Python: /opt/aanalogos/.venv                    │
│ └── Streamlit Web Server (0.0.0.0:8501)                     │
│                                                             │
│ Capas del Software:                                         │
│ └── app.py                                                  │
│ └── aanalogos/ (Motor Climatológico Modular)                │
│ └── data/ (Series Históricas)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Procedimiento de Instalación Paso a Paso

### 2.1 Preparación del Servidor
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

### 2.2 Clonación y Permisos
```bash
sudo git clone https://github.com/wabarca/aanalogos.git /opt/aanalogos
sudo useradd -r -s /bin/false -d /opt/aanalogos clima
sudo chown -R clima:clima /opt/aanalogos
```

### 2.3 Creación del Entorno Virtual e Instalación de Dependencias
```bash
cd /opt/aanalogos
sudo -u clima python3 -m venv .venv
sudo -u clima .venv/bin/pip install --upgrade pip
sudo -u clima .venv/bin/pip install -r requirements.txt
```

### 2.4 Verificación de Integridad y Pruebas
```bash
sudo -u clima .venv/bin/python -m unittest discover -s tests -v
```
*(Debe reportar 9 pruebas OK con 100% de paridad).*

---

## 3. Configuración del Servicio `systemd`

Copie el archivo de servicio y active el arranque automático:
```bash
sudo cp /opt/aanalogos/deploy/aanalogos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aanalogos
sudo systemctl start aanalogos
```

### Comandos de Control Operativo
* **Consultar estado:** `sudo systemctl status aanalogos`
* **Reiniciar servicio:** `sudo systemctl restart aanalogos`
* **Ver logs en tiempo real:** `journalctl -u aanalogos -f`

---

## 4. Configuración de Red y Seguridad

### 4.1 Reglas de Firewall (UFW)
Para restringir el acceso exclusivamente a la subred de la institución:
```bash
sudo ufw allow from 192.168.0.0/16 to any port 8501 proto tcp
sudo ufw reload
```

### 4.2 Acceso desde las Estaciones de Trabajo
Los analistas y meteorólogos pueden acceder mediante navegador web ingresando:
```text
http://<IP_DEL_SERVIDOR_LINUX>:8501
```

---

## 5. Buenas Prácticas de Seguridad
* **No exponer directamente a Internet:** La aplicación está diseñada para uso institucional interno. Si se requiere acceso externo, debe realizarse mediante VPN institucional o Reverse Proxy HTTPS (Nginx/Caddy) con autenticación centralizada.
* **Aislamiento de Privilegios:** El servicio se ejecuta bajo el usuario dedicado `clima` sin privilegios de administración.

---

### Navegación

**[← Anterior](instalacion_windows.md)** · **[Índice de documentación](README.md)** · **[Siguiente →](mantenimiento.md)**
