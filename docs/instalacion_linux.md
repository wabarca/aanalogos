# Guía de Instalación y Despliegue en Servidor Linux (Ubuntu / Debian)

Esta guía describe el procedimiento para desplegar **AAnalogos** en un servidor o PC institucional con sistema operativo Linux (Ubuntu 22.04 / 24.04 LTS o Debian 11 / 12) para servicio en red local (LAN).

---

## 1. Requisitos Previos del Sistema

Actualice los repositorios e instale Python 3, `venv`, `pip` y `git`:
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
```

---

## 2. Clonación del Repositorio e Instalación

1. Clone el repositorio en la ruta institucional (e.g. `/opt/aanalogos` o directorio de usuario):
```bash
sudo git clone https://github.com/wabarca/aanalogos.git /opt/aanalogos
cd /opt/aanalogos
```

2. Cree y active un entorno virtual aislado:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale las dependencias de producción:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Verifique la instalación ejecutando la suite de pruebas:
```bash
python -m unittest discover -s tests
```
*(Debe reportar 9 pruebas con estado `OK`).*

---

## 3. Configuración para Acceso en Red Institucional (LAN)

Para permitir que otros equipos de la red accedan mediante navegador web:

### Configurar Firewall (UFW)
Habilite el puerto 8501 en el firewall del servidor:
```bash
sudo ufw allow 8501/tcp
sudo ufw reload
```

### Prueba de Ejecución Manual
```bash
./deploy/run_server.sh
```
Abra el navegador en cualquier computadora de la red: `http://<IP_DEL_SERVIDOR>:8501`.

---

## 4. Configuración como Servicio Continuo con `systemd`

Para que la aplicación se inicie automáticamente con el sistema y se reinicie ante caídas:

1. Cree un usuario de sistema dedicado sin privilegios de root:
```bash
sudo useradd -r -s /bin/false -d /opt/aanalogos clima
sudo chown -R clima:clima /opt/aanalogos
```

2. Copie la unidad de servicio `systemd`:
```bash
sudo cp deploy/aanalogos.service /etc/systemd/system/
sudo systemctl daemon-reload
```

3. Habilite e inicie el servicio:
```bash
sudo systemctl enable aanalogos
sudo systemctl start aanalogos
```

4. Verifique el estado del servicio:
```bash
sudo systemctl status aanalogos
```

5. Para consultar los logs en tiempo real:
```bash
journalctl -u aanalogos -f
```
