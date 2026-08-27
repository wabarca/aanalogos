#!/usr/bin/env bash
# ==============================================================================
# Script de Arranque para AAnalogos en Red Institucional
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "======================================================================"
echo "Iniciando AAnalogos en Red Local (LAN)..."
echo "Directorio de trabajo: $SCRIPT_DIR"
echo "Puerto: 8501 (accesible desde otros equipos en la misma red)"
echo "======================================================================"

streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
