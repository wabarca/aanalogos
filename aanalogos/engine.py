"""
Orquestador principal del motor climatológico de selección de años análogos.
"""

from typing import List, Optional, Dict
import pandas as pd
import numpy as np

from .config import UMBRALES_OSCILACIONES
from .data import cargar_todas_oscilaciones
from .windows import extraer_ventana, obtener_descripcion_ventana
from .metrics import calcular_metricas_vector
from .results import ResultadoAnalogos, MetricaDetallada


def calcular_analogos(
    year_objetivo: int,
    mes_objetivo: int,
    indices: List[str],
    data_dir: str = ".",
    oscilaciones_cargadas: Optional[Dict[str, pd.DataFrame]] = None
) -> ResultadoAnalogos:
    """
    Función principal de la API del motor.
    Calcula los años análogos climáticos para un conjunto de índices, mes y año objetivo.
    
    Parámetros:
    - year_objetivo: Año objetivo a evaluar (ej. 2015, 2026).
    - mes_objetivo: Mes de cierre de la ventana semestral (1 a 12).
    - indices: Lista de nombres de oscilaciones a combinar (ej. ['AMO', 'PDO', 'TNA']).
    - data_dir: Directorio donde se ubican los archivos de datos CSV.
    - oscilaciones_cargadas: Diccionario preexistente de DataFrames (opcional).
    
    Retorna:
    - ResultadoAnalogos: Objeto estructurado con todos los parámetros, métricas, rankings y trazabilidad.
    """
    year_objetivo = int(year_objetivo)
    mes_objetivo = int(mes_objetivo)

    if not (1 <= mes_objetivo <= 12):
        raise ValueError(f"mes_objetivo debe estar entre 1 y 12. Recibido: {mes_objetivo}")

    # Cargar datos si no fueron provistos
    if oscilaciones_cargadas is None:
        oscilaciones_cargadas = cargar_todas_oscilaciones(data_dir)

    # 1. Validar que TODAS las oscilaciones solicitadas existan y tengan vector objetivo completo
    osc_validas = []
    indices_no_disponibles = []
    vectores_objetivo = {}

    for osc in indices:
        if osc not in oscilaciones_cargadas:
            indices_no_disponibles.append(osc)
            continue
        v_obj = extraer_ventana(oscilaciones_cargadas[osc], year_objetivo, mes_objetivo)
        if v_obj is not None:
            osc_validas.append(osc)
            vectores_objetivo[osc] = v_obj
        else:
            indices_no_disponibles.append(osc)

    # Si uno o más índices solicitados no están disponibles, NO reducir silenciosamente el conjunto
    if indices_no_disponibles:
        msg_err = (
            f"Los siguientes {len(indices_no_disponibles)} índice(s) seleccionados no disponen de una "
            f"ventana retrospectiva de 6 meses completa para el Año {year_objetivo} (Mes {mes_objetivo}): "
            f"{', '.join(indices_no_disponibles)}. La metodología requiere cobertura completa de todos los índices solicitados."
        )
        return ResultadoAnalogos(
            year_objetivo=year_objetivo,
            mes_objetivo=mes_objetivo,
            indices_solicitados=indices,
            indices_evaluados=[],
            indices_no_disponibles=indices_no_disponibles,
            es_valido=False,
            mensaje_error=msg_err,
            ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo),
            anios_candidatos=[],
            tabla_coincidencias=pd.DataFrame(),
            tabla_trazabilidad=pd.DataFrame()
        )

    # 2. Construir intersección estricta de años candidatos comunes (excluyendo el año objetivo)
    anios_comunes = None
    for osc in osc_validas:
        df = oscilaciones_cargadas[osc]
        anios_con_ventana = set()
        for y in df["YEAR"].unique():
            y_int = int(y)
            if y_int != year_objetivo and extraer_ventana(df, y_int, mes_objetivo) is not None:
                anios_con_ventana.add(y_int)

        if anios_comunes is None:
            anios_comunes = anios_con_ventana
        else:
            anios_comunes = anios_comunes.intersection(anios_con_ventana)

    if not anios_comunes:
        return ResultadoAnalogos(
            year_objetivo=year_objetivo,
            mes_objetivo=mes_objetivo,
            indices_solicitados=indices,
            indices_evaluados=osc_validas,
            indices_no_disponibles=[],
            es_valido=False,
            mensaje_error="No se encontraron años históricos comunes con ventanas completas para la combinación seleccionada.",
            ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo),
            anios_candidatos=[],
            tabla_coincidencias=pd.DataFrame(),
            tabla_trazabilidad=pd.DataFrame()
        )

    anios_candidatos = sorted(list(anios_comunes))

    # 3. Calcular métricas por oscilación y generar trazabilidad con precisión flotante completa
    filas_trazabilidad = []
    matriz_coincidencias = {osc: {} for osc in osc_validas}

    for osc in osc_validas:
        df = oscilaciones_cargadas[osc]
        v_obj = vectores_objetivo[osc]
        r_th, mad_th = UMBRALES_OSCILACIONES.get(osc, (0.6, 0.6))

        for y_cand in anios_candidatos:
            v_cand = extraer_ventana(df, y_cand, mes_objetivo)
            if v_cand is None:
                continue

            r_val, mad_val, coincide = calcular_metricas_vector(v_cand, v_obj, r_th, mad_th)
            matriz_coincidencias[osc][y_cand] = 1 if coincide else 0

            filas_trazabilidad.append({
                "YEAR": y_cand,
                "Indice": osc,
                "Pearson": float(r_val),
                "MAD": float(mad_val),
                "Coincidencia": 1 if coincide else 0
            })

    df_trazabilidad = pd.DataFrame(filas_trazabilidad)

    # 4. Consolidar tabla de resultados indexada por YEAR
    df_consolidado = pd.DataFrame(index=anios_candidatos)
    df_consolidado.index.name = "YEAR"

    for osc in osc_validas:
        df_consolidado[f"Coincidencias {osc}"] = [matriz_coincidencias[osc].get(y, 0) for y in anios_candidatos]

    df_consolidado["Total"] = df_consolidado.sum(axis=1)
    df_consolidado = df_consolidado.sort_values(by=["Total", "YEAR"], ascending=[False, False])

    return ResultadoAnalogos(
        year_objetivo=year_objetivo,
        mes_objetivo=mes_objetivo,
        indices_solicitados=indices,
        indices_evaluados=osc_validas,
        indices_no_disponibles=[],
        es_valido=True,
        mensaje_error=None,
        ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo),
        anios_candidatos=anios_candidatos,
        tabla_coincidencias=df_consolidado,
        tabla_trazabilidad=df_trazabilidad
    )
