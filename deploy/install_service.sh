#!/usr/bin/env bash
# ==============================================================================
# Instalador Automatizado del Servicio systemd para AAnalogos
# Ministerio de Medio Ambiente y Recursos Naturales (MARN), El Salvador
# ==============================================================================
set -euo pipefail

# 1. Comprobar privilegios de superusuario (root)
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: Este script debe ejecutarse con privilegios de superusuario (root o sudo)." >&2
    echo "Uso: sudo bash deploy/install_service.sh [--inplace | --opt | --dir <ruta> --user <usuario>]" >&2
    exit 1
fi

# Directorio donde se encuentra este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="aanalogos"
SYSTEMD_DIR="/etc/systemd/system"
PORT="8501"

# Modo de instalación
MODE="auto"
CUSTOM_DIR=""
CUSTOM_USER=""

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        --inplace)
            MODE="inplace"
            shift
            ;;
        --opt)
            MODE="opt"
            shift
            ;;
        --dir)
            CUSTOM_DIR="$2"
            shift 2
            ;;
        --user)
            CUSTOM_USER="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Uso: sudo bash deploy/install_service.sh [OPCIONES]"
            echo ""
            echo "Opciones:"
            echo "  --inplace        Instala el servicio en el directorio actual ($SCRIPT_DIR)"
            echo "  --opt            Instala el servicio en la ruta estándar /opt/aanalogos"
            echo "  --dir <ruta>     Especifica una ruta de instalación personalizada"
            echo "  --user <usuario>  Especifica el usuario del sistema que ejecutará el servicio"
            echo "  --port <puerto>   Puerto de escucha de Streamlit (por defecto: 8501)"
            exit 0
            ;;
        *)
            echo "Opción desconocida: $1" >&2
            exit 1
            ;;
    esac
done

if [ "$MODE" = "auto" ]; then
    if [ "$SCRIPT_DIR" = "/opt/aanalogos" ]; then
        MODE="opt"
    else
        MODE="inplace"
    fi
fi

# Definir variables según el modo
if [ "$MODE" = "opt" ]; then
    TARGET_DIR="/opt/aanalogos"
    TARGET_USER="${CUSTOM_USER:-clima}"
    TARGET_GROUP="$TARGET_USER"

    echo "======================================================================"
    echo "Instalación en Ruta Estándar Institucional: $TARGET_DIR"
    echo "Usuario del Servicio: $TARGET_USER"
    echo "======================================================================"

    # Crear usuario del sistema si no existe
    if ! id -u "$TARGET_USER" >/dev/null 2>&1; then
        echo "Creando usuario del sistema dedicado: $TARGET_USER..."
        useradd -r -s /usr/sbin/nologin -d "$TARGET_DIR" "$TARGET_USER"
    fi

    # Copiar/sincronizar archivos si venimos de otro directorio
    if [ "$SCRIPT_DIR" != "$TARGET_DIR" ]; then
        echo "Copiando archivos del proyecto hacia $TARGET_DIR..."
        mkdir -p "$TARGET_DIR"
        cp -ru "$SCRIPT_DIR"/* "$TARGET_DIR"/
    fi

else
    # Modo In-Place (directorio actual o personalizado)
    TARGET_DIR="${CUSTOM_DIR:-$SCRIPT_DIR}"
    
    # Determinar usuario: si no se especifica, usar el dueño del directorio o SUDO_USER
    if [ -n "$CUSTOM_USER" ]; then
        TARGET_USER="$CUSTOM_USER"
    elif [ -n "${SUDO_USER:-}" ]; then
        TARGET_USER="$SUDO_USER"
    else
        TARGET_USER="$(stat -c '%U' "$TARGET_DIR")"
    fi
    TARGET_GROUP="$(id -gn "$TARGET_USER")"

    echo "======================================================================"
    echo "Instalación en Directorio Actual (In-Place): $TARGET_DIR"
    echo "Usuario del Servicio: $TARGET_USER (Grupo: $TARGET_GROUP)"
    echo "======================================================================"
fi

# Verificar o crear entorno virtual
VENV_DIR="$TARGET_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando entorno virtual Python en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip
    if [ -f "$TARGET_DIR/requirements.txt" ]; then
        echo "Instalando dependencias desde requirements.txt..."
        "$VENV_DIR/bin/pip" install -r "$TARGET_DIR/requirements.txt"
    fi
fi

# Verificar ejecutable de streamlit
STREAMLIT_BIN="$VENV_DIR/bin/streamlit"
if [ ! -f "$STREAMLIT_BIN" ]; then
    echo "Instalando Streamlit en el entorno virtual..."
    "$VENV_DIR/bin/pip" install streamlit
fi

# Ajustar permisos
echo "Configurando permisos de archivos..."
chmod +x "$TARGET_DIR/deploy/run_server.sh" || true
chmod +x "$TARGET_DIR/deploy/install_service.sh" || true
chown -R "$TARGET_USER:$TARGET_GROUP" "$TARGET_DIR"

# Generar archivo de servicio systemd
SERVICE_FILE="$SYSTEMD_DIR/${SERVICE_NAME}.service"
echo "Generando unidad systemd en $SERVICE_FILE..."

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Servicio Web de Años Análogos Climáticos (AAnalogos Streamlit)
After=network.target

[Service]
Type=simple
User=$TARGET_USER
Group=$TARGET_GROUP
WorkingDirectory=$TARGET_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$STREAMLIT_BIN run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd y activar servicio
echo "Recargando demonio systemd..."
systemctl daemon-reload

echo "Habilitando e iniciando servicio ${SERVICE_NAME}..."
systemctl enable --now "${SERVICE_NAME}.service"

echo "======================================================================"
echo "¡SERVICIO INSTALADO Y ACTIVADO CON ÉXITO!"
echo "======================================================================"
echo "Estado del servicio:"
systemctl status "${SERVICE_NAME}.service" --no-pager || true
echo "======================================================================"
echo "Acceso web local:        http://localhost:$PORT"
echo "Acceso en Red LAN (MARN): http://$(hostname -I | awk '{print $1}'):$PORT"
echo "Para ver logs en vivo:   journalctl -u $SERVICE_NAME -f"
echo "Para reiniciar:          sudo systemctl restart $SERVICE_NAME"
echo "Para detener:            sudo systemctl stop $SERVICE_NAME"
echo "======================================================================"
