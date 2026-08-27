"""
Módulo de cálculo de correlación de Pearson, Mean Absolute Difference (MAD) y evaluación de coincidencia.
"""

from typing import Tuple
import numpy as np
from scipy.stats import pearsonr


def calcular_metricas_vector(
    v_candidato: list | np.ndarray,
    v_objetivo: list | np.ndarray,
    r_umbral: float,
    mad_umbral: float
) -> Tuple[float, float, bool]:
    """
    Calcula la correlación de Pearson y la distancia MAD entre un vector candidato y el vector objetivo.
    
    Criterio de coincidencia:
        Coincide = (r > r_umbral) and (MAD < mad_umbral)
        
    Retorna:
    - (pearson_r, mad, coincide)
    """
    arr_cand = np.array(v_candidato, dtype=float)
    arr_obj = np.array(v_objetivo, dtype=float)

    try:
        r_val = float(pearsonr(arr_cand, arr_obj)[0])
    except Exception:
        r_val = np.nan

    mad_val = float(np.average(np.abs(arr_obj - arr_cand)))
    coincide = bool((r_val > r_umbral) and (mad_val < mad_umbral))
    return r_val, mad_val, coincide
