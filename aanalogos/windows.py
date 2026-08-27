"""
Módulo para el cálculo y extracción de ventanas móviles retrospectivas de 6 meses.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from .config import LONGITUD_VENTANA, NOMBRES_MESES
from .quality import validar_vector_ventana


def extraer_ventana(df: pd.DataFrame, year: int, mes: int) -> Optional[List[float]]:
    """
    Extrae la ventana continua de 6 meses que culmina en el mes `mes` del año `year`.
    
    Reglas metodológicas :
    - Para mes >= 6: 6 meses continuos del mismo año (mes - 5 hasta mes).
    - Para mes < 6: (6 - mes) meses del año previo (year - 1) + mes meses del año actual (year).
      Etiqueta del análogo: año de cierre `year`.
    
    Retorna:
    - list[float] de longitud 6 si los datos son válidos y completos.
    - None si faltan registros o si alguno contiene NaN/sentinela.
    """
    if df is None or len(df) == 0:
        return None

    df_year = df[df["YEAR"] == int(year)]
    if len(df_year) == 0:
        return None
    row_year = df_year.iloc[0]

    if mes >= 6:
        # Columnas mensuales 1 a 12
        col_indices = list(range(mes - 5, mes + 1))
        vals = [row_year.iloc[c] for c in col_indices]
        if not validar_vector_ventana(vals):
            return None
        return [float(v) for v in vals]
    else:
        df_prev = df[df["YEAR"] == int(year) - 1]
        if len(df_prev) == 0:
            return None
        row_prev = df_prev.iloc[0]

        # Meses del año previo: (7 + mes) a 12 (ej. mes=1 -> 8:13 -> AGO..DIC)
        col_prev = list(range(7 + mes, 13))
        # Meses del año actual: 1 a mes (ej. mes=1 -> 1:2 -> ENE)
        col_curr = list(range(1, mes + 1))

        vals_prev = [row_prev.iloc[c] for c in col_prev]
        vals_curr = [row_year.iloc[c] for c in col_curr]
        vals_total = vals_prev + vals_curr

        if not validar_vector_ventana(vals_total):
            return None
        return [float(v) for v in vals_total]


def obtener_descripcion_ventana(year: int, mes: int) -> List[str]:
    """
    Genera la lista de nombres y años de los 6 meses de la ventana (ej. ['AGO(2014)', ..., 'ENE(2015)']).
    """
    if mes >= 6:
        return [f"{NOMBRES_MESES[c - 1]}({year})" for c in range(mes - 5, mes + 1)]
    else:
        prev_m = [f"{NOMBRES_MESES[c - 1]}({year - 1})" for c in range(7 + mes, 13)]
        curr_m = [f"{NOMBRES_MESES[c - 1]}({year})" for c in range(1, mes + 1)]
        return prev_m + curr_m
