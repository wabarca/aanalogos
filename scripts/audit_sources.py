"""
Script de Auditoría Automatizada de Calidad y Cobertura de Datos (AAnalogos).
Produce un reporte integral sobre completitud, sentinelas, NaNs y rangos de ventanas válidas.
"""

import os
import sys
import pandas as pd
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from aanalogos.config import FUENTES_DATOS, NOMBRES_MESES
from aanalogos.data import cargar_todas_oscilaciones
from aanalogos.windows import extraer_ventana


def ejecutar_auditoria():
    data_dir = os.path.join(PROJECT_DIR, "data")
    if not os.path.exists(data_dir):
        data_dir = PROJECT_DIR

    oscilaciones = cargar_todas_oscilaciones(data_dir)

    print("=" * 110)
    print("INFORME DE AUDITORÍA AUTOMATIZADA DE SERIES CLIMÁTICAS (AANALOGOS)")
    print("=" * 110)

    reporte = []

    for cod, df in oscilaciones.items():
        anios = sorted(df["YEAR"].tolist())
        y_min, y_max = min(anios), max(anios)
        n_anios = len(anios)

        cols_m = [c for c in df.columns if c != "YEAR"]
        exact_12 = (len(cols_m) == 12) and (cols_m == NOMBRES_MESES)

        # NaNs y sentinelas
        vals = df[cols_m].values
        n_nans = int(np.isnan(vals).sum())

        # Primera y última ventana de 6 meses válida
        primer_w, ultima_w = None, None
        for y in anios:
            for m in range(1, 13):
                v = extraer_ventana(df, y, m)
                if v is not None:
                    if primer_w is None:
                        primer_w = f"{y}-M{m:02d}"
                    ultima_w = f"{y}-M{m:02d}"

        # Diagnóstico de problemas
        dups = df["YEAR"].duplicated().sum()
        huecos = set(range(y_min, y_max + 1)) - set(anios)

        estado = "ÓPTIMO"
        obs = []
        if dups > 0:
            estado = "ADVERTENCIA"
            obs.append(f"{dups} años duplicados")
        if huecos:
            estado = "ADVERTENCIA"
            obs.append(f"Huecos: {sorted(list(huecos))}")
        if not exact_12:
            obs.append("Estructura trimestral/no mensual")
        if n_nans > 0:
            obs.append(f"{n_nans} celdas NaN")

        obs_str = "; ".join(obs) if obs else "Serie continua y homogénea"

        reporte.append({
            "Índice": cod,
            "Inicio": y_min,
            "Fin": y_max,
            "Total Años": n_anios,
            "12 Meses": "SÍ" if exact_12 else "NO",
            "Primera Ventana Válida": primer_w or "Ninguna",
            "Última Ventana Válida": ultima_w or "Ninguna",
            "Celdas NaN": n_nans,
            "Estado": estado,
            "Observaciones": obs_str
        })

    df_rep = pd.DataFrame(reporte)
    print(df_rep.to_string(index=False))
    print("=" * 110)
    return df_rep


if __name__ == "__main__":
    ejecutar_auditoria()
