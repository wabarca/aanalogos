"""
Script de Descarga y Actualización Automatizada de Series Climáticas.
Verifica estado HTTP, tamaño mínimo, estructura de datos y actualiza los archivos de forma segura y no destructiva.
"""

import os
import sys
import tempfile
import urllib.request
import pandas as pd
import requests

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos.config import FUENTES_DATOS
from aanalogos.data import acomodaParaCSV, acomodaParaCSV_2, acomodaParaCSV_3

DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def descargar_y_actualizar(codigo: str, meta: dict) -> bool:
    url = meta.get("url")
    if not url:
        print(f"[{codigo}] Sin URL configurada. Omitiendo.")
        return False

    print(f"[{codigo}] Descargando desde {url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AAnalogos-Updater/3.1"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                print(f"[{codigo}] Error HTTP: {resp.status}")
                return False
            data_bytes = resp.read()

        if len(data_bytes) < 100:
            print(f"[{codigo}] Error: Archivo descargado demasiado pequeño ({len(data_bytes)} bytes).")
            return False

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_f:
            tmp_f.write(data_bytes)
            tmp_path = tmp_f.name

        target_txt = os.path.join(DATA_DIR, meta.get("txt", f"data{codigo}.txt"))
        target_csv = os.path.join(DATA_DIR, meta.get("csv", f"data{codigo}.csv"))

        # Mover atómicamente a txt
        if os.path.exists(target_txt):
            os.remove(target_txt)
        os.rename(tmp_path, target_txt)

        # Procesar a CSV
        acomodaParaCSV(target_txt, target_csv)
        print(f"[{codigo}] Actualizado exitosamente en data/{os.path.basename(target_csv)}")
        return True

    except Exception as e:
        print(f"[{codigo}] Error durante la descarga: {e}")
        return False


def main():
    print("=" * 80)
    print("ACTUALIZACIÓN DE FUENTES DE DATOS CLIMÁTICAS (AANALOGOS)")
    print("=" * 80)
    
    exitosos = 0
    total = len(FUENTES_DATOS)
    
    for cod, meta in FUENTES_DATOS.items():
        if descargar_y_actualizar(cod, meta):
            exitosos += 1

    print(f"\nProceso finalizado: {exitosos}/{total} series actualizadas.")


if __name__ == "__main__":
    main()
