"""
Orquestador principal del motor climatológico de selección de años análogos.
"""

from typing import List, Optional, Dict, Tuple
import pandas as pd
import numpy as np

from .config import (
    LONGITUD_VENTANA_METODOLOGICA,
    LONGITUD_VENTANA_OPERACIONAL,
    UMBRALES_OSCILACIONES,
    obtener_umbrales_metodologicos,
)
from .data import cargar_todas_oscilaciones
from .windows import extraer_ventana, obtener_descripcion_ventana
from .metrics import calcular_metricas_vector
from .results import ResultadoAnalogos, MetricaDetallada


def calcular_analogos(
    year_objetivo: int,
    mes_objetivo: int,
    indices: List[str],
    longitud_ventana: int = LONGITUD_VENTANA_METODOLOGICA,
    umbrales_personalizados: Optional[Dict[str, Tuple[float, float]]] = None,
    max_year_corte: Optional[int] = None,
    modo_analisis: str = "Metodológico",
    data_dir: str = ".",
    oscilaciones_cargadas: Optional[Dict[str, pd.DataFrame]] = None
) -> ResultadoAnalogos:
    """
    Función principal de la API del motor.
    Calcula los años análogos climáticos para un conjunto de índices, mes y año objetivo.
    
    Parámetros:
    - year_objetivo: Año objetivo a evaluar (ej. 2015, 2026).
    - mes_objetivo: Mes de cierre de la ventana temporal (1 a 12).
    - indices: Lista de nombres de oscilaciones a combinar (ej. ['AMO', 'PDO', 'TNA']).
    - longitud_ventana: Longitud de la ventana móvil retrospectiva en meses (6 = metodológica, 12 = operacional).
    - umbrales_personalizados: Diccionario opcional {indice: (r_min, mad_max)} para calibración.
    - max_year_corte: Año máximo permitido en el análisis (control estricto de look-ahead bias).
    - modo_analisis: Etiqueta descriptiva del modo ("Operacional", "Reanálisis Histórico", "Metodológico").
    - data_dir: Directorio donde se ubican los archivos de datos CSV.
    - oscilaciones_cargadas: Diccionario preexistente de DataFrames (opcional).
    
    Retorna:
    - ResultadoAnalogos: Objeto estructurado con todos los parámetros, métricas, rankings y trazabilidad.
    """
    year_objetivo = int(year_objetivo)
    mes_objetivo = int(mes_objetivo)
    longitud_ventana = int(longitud_ventana)

    if not (1 <= mes_objetivo <= 12):
        raise ValueError(f"mes_objetivo debe estar entre 1 y 12. Recibido: {mes_objetivo}")
    if not (1 <= longitud_ventana <= 12):
        raise ValueError(f"longitud_ventana debe estar entre 1 y 12. Recibido: {longitud_ventana}")

    # Determinar diccionario de umbrales a utilizar
    umbrales_efectivos = obtener_umbrales_metodologicos()
    if umbrales_personalizados:
        for k, v in umbrales_personalizados.items():
            if isinstance(v, (list, tuple)) and len(v) == 2:
                umbrales_efectivos[k] = (float(v[0]), float(v[1]))

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
        
        df_osc = oscilaciones_cargadas[osc]
        # Si se especifica max_year_corte, validar que el objetivo no supere el corte
        if max_year_corte is not None and year_objetivo > int(max_year_corte):
            indices_no_disponibles.append(osc)
            continue

        v_obj = extraer_ventana(df_osc, year_objetivo, mes_objetivo, longitud_ventana=longitud_ventana)
        if v_obj is not None:
            osc_validas.append(osc)
            vectores_objetivo[osc] = v_obj
        else:
            indices_no_disponibles.append(osc)

    # Si uno o más índices solicitados no están disponibles, NO reducir silenciosamente el conjunto
    if indices_no_disponibles:
        msg_err = (
            f"Los siguientes {len(indices_no_disponibles)} índice(s) seleccionados no disponen de una "
            f"ventana retrospectiva de {longitud_ventana} meses completa para el Año {year_objetivo} (Mes {mes_objetivo}): "
            f"{', '.join(indices_no_disponibles)}. La metodología requiere cobertura completa de todos los índices solicitados."
        )
        return ResultadoAnalogos(
            year_objetivo=year_objetivo,
            mes_objetivo=mes_objetivo,
            indices_solicitados=indices,
            indices_evaluados=[],
            indices_no_disponibles=indices_no_disponibles,
            longitud_ventana=longitud_ventana,
            umbrales_utilizados=umbrales_efectivos,
            modo_analisis=modo_analisis,
            es_valido=False,
            mensaje_error=msg_err,
            ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo, longitud_ventana=longitud_ventana),
            anios_candidatos=[],
            tabla_coincidencias=pd.DataFrame(),
            tabla_trazabilidad=pd.DataFrame()
        )

    # 2. Construir intersección estricta de años candidatos comunes (excluyendo el año objetivo)
    anios_comunes = None
    for osc in osc_validas:
        df = oscilaciones_cargadas[osc]
        if max_year_corte is not None:
            df = df[df["YEAR"] <= int(max_year_corte)]

        anios_con_ventana = set()
        for y in df["YEAR"].unique():
            y_int = int(y)
            if y_int != year_objetivo and extraer_ventana(df, y_int, mes_objetivo, longitud_ventana=longitud_ventana) is not None:
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
            longitud_ventana=longitud_ventana,
            umbrales_utilizados=umbrales_efectivos,
            modo_analisis=modo_analisis,
            es_valido=False,
            mensaje_error="No se encontraron años históricos comunes con ventanas completas para la combinación seleccionada.",
            ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo, longitud_ventana=longitud_ventana),
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
        r_th, mad_th = umbrales_efectivos.get(osc, (0.6, 0.6))

        for y_cand in anios_candidatos:
            v_cand = extraer_ventana(df, y_cand, mes_objetivo, longitud_ventana=longitud_ventana)
            if v_cand is None:
                continue

            r_val, mad_val, coincide = calcular_metricas_vector(v_cand, v_obj, r_th, mad_th)
            matriz_coincidencias[osc][y_cand] = 1 if coincide else 0

            filas_trazabilidad.append({
                "YEAR": y_cand,
                "Indice": osc,
                "Pearson": float(r_val),
                "MAD": float(mad_val),
                "Umbral_r": float(r_th),
                "Umbral_MAD": float(mad_th),
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
        longitud_ventana=longitud_ventana,
        umbrales_utilizados=umbrales_efectivos,
        modo_analisis=modo_analisis,
        es_valido=True,
        mensaje_error=None,
        ventana_temporal=obtener_descripcion_ventana(year_objetivo, mes_objetivo, longitud_ventana=longitud_ventana),
        anios_candidatos=anios_candidatos,
        tabla_coincidencias=df_consolidado,
        tabla_trazabilidad=df_trazabilidad
    )
