"""
Módulo para el cálculo y extracción de ventanas móviles retrospectivas de 6 meses.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from .config import LONGITUD_VENTANA_METODOLOGICA, NOMBRES_MESES
from .quality import validar_vector_ventana


def extraer_ventana(
    df: pd.DataFrame,
    year: int,
    mes: int,
    longitud_ventana: int = LONGITUD_VENTANA_METODOLOGICA
) -> Optional[List[float]]:
    """
    Extrae la ventana continua de `longitud_ventana` meses que culmina en el mes `mes` del año `year`.
    
    Reglas metodológicas y operacionales:
    - Si mes >= longitud_ventana: N meses continuos del año `year` (columnas mes - N + 1 hasta mes).
    - Si mes < longitud_ventana: (N - mes) meses del año previo `year - 1` (columnas 13 - N + mes hasta 12)
      + mes meses del año actual `year` (columnas 1 hasta mes).
      Etiqueta del candidato: año de cierre `year`.
    
    Retorna:
    - list[float] de longitud `longitud_ventana` si los datos son válidos y completos.
    - None si faltan registros o si alguno contiene NaN/sentinela.
    """
    if df is None or len(df) == 0:
        return None

    N = int(longitud_ventana)
    if not (1 <= N <= 12):
        raise ValueError(f"longitud_ventana debe estar entre 1 y 12. Recibido: {N}")

    df_year = df[df["YEAR"] == int(year)]
    if len(df_year) == 0:
        return None
    row_year = df_year.iloc[0]

    if mes >= N:
        # Columnas mensuales (1 a 12)
        col_indices = list(range(mes - N + 1, mes + 1))
        vals = [row_year.iloc[c] for c in col_indices]
        if not validar_vector_ventana(vals, longitud_esperada=N):
            return None
        return [float(v) for v in vals]
    else:
        df_prev = df[df["YEAR"] == int(year) - 1]
        if len(df_prev) == 0:
            return None
        row_prev = df_prev.iloc[0]

        # Meses del año previo: (13 - N + mes) a 12
        col_prev = list(range(13 - N + mes, 13))
        # Meses del año actual: 1 a mes
        col_curr = list(range(1, mes + 1))

        vals_prev = [row_prev.iloc[c] for c in col_prev]
        vals_curr = [row_year.iloc[c] for c in col_curr]
        vals_total = vals_prev + vals_curr

        if not validar_vector_ventana(vals_total, longitud_esperada=N):
            return None
        return [float(v) for v in vals_total]


def obtener_descripcion_ventana(
    year: int,
    mes: int,
    longitud_ventana: int = LONGITUD_VENTANA_METODOLOGICA
) -> List[str]:
    """
    Genera la lista de nombres y años de los N meses de la ventana (ej. ['AGO(2014)', ..., 'ENE(2015)']).
    """
    N = int(longitud_ventana)
    if mes >= N:
        return [f"{NOMBRES_MESES[c - 1]}({year})" for c in range(mes - N + 1, mes + 1)]
    else:
        prev_m = [f"{NOMBRES_MESES[c - 1]}({year - 1})" for c in range(13 - N + mes, 13)]
        curr_m = [f"{NOMBRES_MESES[c - 1]}({year})" for c in range(1, mes + 1)]
        return prev_m + curr_m
