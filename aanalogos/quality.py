"""
Módulo de control de calidad y normalización de datos climatológicos.
"""

import pandas as pd
import numpy as np
from .config import UMBRAL_SENTINELA_MIN, UMBRAL_SENTINELA_MAX


def limpiar_datos_indice(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza y sanea un DataFrame mensual de índice climático:
    - Asegura que la columna de año se llame 'YEAR' y sea de tipo entero.
    - Convierte valores mensuales a float.
    - Enmascara valores sentinela (< -50 o > 50) como np.nan.
    - Elimina duplicados de año y ordena cronológicamente.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()

    df = df.copy()
    col_year = [c for c in df.columns if "YEAR" in str(c).upper() or "AÑO" in str(c).upper()]
    if not col_year:
        raise ValueError("El DataFrame no contiene una columna identificable como 'YEAR'.")
    
    if col_year[0] != "YEAR":
        df = df.rename(columns={col_year[0]: "YEAR"})

    # Eliminar columnas accesorias como 'Unnamed: 0'
    df = df[[c for c in df.columns if not str(c).startswith("Unnamed")]]

    # Limpiar y convertir columna YEAR
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")
    df = df.dropna(subset=["YEAR"])
    df["YEAR"] = df["YEAR"].astype(int)

    # Limpiar y convertir columnas mensuales
    for col in df.columns:
        if col != "YEAR":
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df.loc[(df[col] < UMBRAL_SENTINELA_MIN) | (df[col] > UMBRAL_SENTINELA_MAX), col] = np.nan

    # Deduplicación y orden cronológico
    df = df.drop_duplicates(subset=["YEAR"]).sort_values(by="YEAR").reset_index(drop=True)
    return df


def validar_vector_ventana(vector: list | np.ndarray | None) -> bool:
    """
    Verifica si un vector de 6 meses es numéricamente válido (sin NaNs ni infinitos).
    """
    if vector is None:
        return False
    if len(vector) != 6:
        return False
    arr = np.array(vector, dtype=float)
    if np.isnan(arr).any() or np.isinf(arr).any():
        return False
    return True
