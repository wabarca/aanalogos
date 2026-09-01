"""
Módulo de catálogo estructurado, metadatos y diagnóstico operacional de fuentes climáticas.
"""

import os
import yaml
import datetime
from typing import Dict, Optional, Tuple, Any, List
import pandas as pd
import numpy as np

from .config import NOMBRES_MESES, UMBRAL_SENTINELA_MIN, UMBRAL_SENTINELA_MAX


def resolver_ruta_config(nombre_archivo: str = "data_sources.yaml") -> str:
    """Busca el archivo de configuración en posibles rutas relativas."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidatos = [
        os.path.join(base_dir, "config", nombre_archivo),
        os.path.join(base_dir, nombre_archivo),
        os.path.join(os.getcwd(), "config", nombre_archivo),
        os.path.join(os.getcwd(), nombre_archivo),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return os.path.join(base_dir, "config", nombre_archivo)


def cargar_catalogo_indices(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga el catálogo estructurado de los 19 índices climáticos desde data_sources.yaml.
    """
    if config_path is None:
        config_path = resolver_ruta_config("data_sources.yaml")
    
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        catalogo = yaml.safe_load(f)
    return catalogo if catalogo else {}


def cargar_configuracion_institucional(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga la personalización institucional (nombre, división, logo PNG) desde config/institution.yaml.
    Si el archivo no existe o contiene campos vacíos, retorna valores institucionales por defecto.
    """
    defaults = {
        "name": "Servicio Meteorológico Nacional",
        "division": "Dirección de Meteorología y Climatología",
        "logo": None,
    }
    
    if config_path is None:
        config_path = resolver_ruta_config("institution.yaml")
    
    if not os.path.exists(config_path):
        return defaults
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if not cfg or not isinstance(cfg, dict):
            return defaults
        
        inst_data = cfg.get("institution", cfg)
        if not isinstance(inst_data, dict):
            return defaults
        
        nombre = inst_data.get("name", defaults["name"]) or defaults["name"]
        division = inst_data.get("division", defaults["division"]) or defaults["division"]
        logo_raw = inst_data.get("logo")
        
        logo_resuelto = None
        if logo_raw:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cands = [
                str(logo_raw),
                os.path.join(base_dir, str(logo_raw)),
                os.path.join(os.getcwd(), str(logo_raw)),
            ]
            for c in cands:
                if os.path.isfile(c) and c.lower().endswith(".png"):
                    logo_resuelto = os.path.abspath(c)
                    break
        
        return {
            "name": str(nombre).strip(),
            "division": str(division).strip(),
            "logo": logo_resuelto,
        }
    except Exception:
        return defaults


def obtener_periodo_evaluacion_operacional(fecha_referencia: Optional[datetime.date] = None) -> Tuple[int, int]:
    """
    Calcula el año y mes de evaluación operacional a partir de una fecha de referencia
    (por defecto, la fecha actual del sistema).
    
    Regla fundamental de temporalidad:
    El mes de evaluación corresponde siempre al mes calendario inmediatamente anterior
    al mes en curso:
      mes_evaluacion = mes_actual - 1
    Con manejo estricto del cambio de año:
      enero Y -> diciembre Y-1
      febrero Y -> enero Y
      ...
      agosto Y -> julio Y
      diciembre Y -> noviembre Y
    """
    if fecha_referencia is None:
        fecha_referencia = datetime.date.today()
    
    año_actual = fecha_referencia.year
    mes_actual = fecha_referencia.month
    
    if mes_actual == 1:
        return (año_actual - 1, 12)
    else:
        return (año_actual, mes_actual - 1)


def determinar_ultimo_mes_disponible(
    oscilaciones: Dict[str, pd.DataFrame],
    year: Optional[int] = None,
    indices: Optional[List[str]] = None,
    fecha_referencia: Optional[datetime.date] = None
) -> Tuple[int, int]:
    """
    Determina de manera robusta y explícita el último año y mes disponible operacionalmente
    en el conjunto de series cargadas (o en el subconjunto `indices` especificado).
    
    Regla Operacional Institucional:
    - Los datos correspondientes al mes M solamente pueden utilizarse para el cálculo
      operacional a partir del mes M+1.
    - Por tanto, para el año calendario actual (now.year), el mes máximo operacional permitido
      es estricto: `mes_maximo = now.month - 1`.
    - Si `mes_maximo == 0` (ej. enero del año actual), el período de evaluación por defecto
      es diciembre del año anterior: `(now.year - 1, 12)`.
    - Para años anteriores (año objetivo < año actual), esta restricción de publicación no aplica,
      permitiendo utilizar hasta el último mes con datos válidos no-sentinela del año.
    """
    ref_date = fecha_referencia if fecha_referencia is not None else datetime.date.today()
    año_ref = ref_date.year
    mes_ref = ref_date.month

    target_year = int(year) if year is not None else (año_ref if mes_ref > 1 else año_ref - 1)

    if not oscilaciones:
        return obtener_periodo_evaluacion_operacional(ref_date)

    series_a_evaluar = {k: v for k, v in oscilaciones.items() if (indices is None or k in indices)}
    if not series_a_evaluar:
        series_a_evaluar = oscilaciones

    def _meses_validos_para_año(y: int) -> List[int]:
        # Para el año calendario actual, limitar estrictamente a mes_actual - 1
        if y == año_ref:
            max_m_posible = mes_ref - 1
        else:
            max_m_posible = 12

        if max_m_posible <= 0:
            return []

        meses_ok = []
        for m in range(1, max_m_posible + 1):
            con_dato = 0
            total_eval = 0
            for osc_name, df in series_a_evaluar.items():
                if df is None or len(df) == 0:
                    continue
                df_y = df[df["YEAR"] == y]
                if len(df_y) == 0:
                    continue
                val = df_y.iloc[0, m]
                total_eval += 1
                if pd.notna(val) and UMBRAL_SENTINELA_MIN <= float(val) <= UMBRAL_SENTINELA_MAX:
                    con_dato += 1
            if total_eval > 0 and con_dato == total_eval:
                meses_ok.append(m)
        return meses_ok

    # Probar año solicitado
    meses_año = _meses_validos_para_año(target_year)
    if meses_año:
        return (target_year, max(meses_año))

    # Si no hay datos en el año solicitado y no se especificó un año fijo, retroceder año por año
    if year is None:
        for y_back in range(target_year - 1, target_year - 6, -1):
            meses_prev = _meses_validos_para_año(y_back)
            if meses_prev:
                return (y_back, max(meses_prev))

    # Fallback determinista
    return obtener_periodo_evaluacion_operacional(ref_date)


def obtener_estado_fuentes(
    oscilaciones: Dict[str, pd.DataFrame],
    catalogo: Optional[Dict[str, Any]] = None,
    data_dir: str = "."
) -> pd.DataFrame:
    """
    Genera una tabla de diagnóstico con el estado de salud, cobertura temporal
    y disponibilidad de las 19 series climáticas.
    """
    if catalogo is None:
        catalogo = cargar_catalogo_indices()

    filas = []
    lista_indices = list(catalogo.keys()) if catalogo else list(oscilaciones.keys())

    for codigo in lista_indices:
        meta = catalogo.get(codigo, {})
        nombre = meta.get("name", codigo)
        institucion = meta.get("institution", "Desconocida")
        region = meta.get("region", "No especificada")
        variable = meta.get("variable", "Anomalía")
        unidad = meta.get("units", "Adimensional")
        frecuencia = meta.get("update_frequency", "Mensual")
        doi = meta.get("doi", "")
        url = meta.get("url", "")

        if codigo in oscilaciones and oscilaciones[codigo] is not None and len(oscilaciones[codigo]) > 0:
            df = oscilaciones[codigo]
            y_min = int(df["YEAR"].min())
            y_max = int(df["YEAR"].max())
            total_anios = len(df)

            # Buscar el último mes con dato válido en el último año
            df_last = df[df["YEAR"] == y_max]
            ultimo_mes_num = 0
            if len(df_last) > 0:
                for m in range(12, 0, -1):
                    val = df_last.iloc[0, m]
                    if pd.notna(val) and UMBRAL_SENTINELA_MIN <= float(val) <= UMBRAL_SENTINELA_MAX:
                        ultimo_mes_num = m
                        break

            if ultimo_mes_num == 0:
                for y_back in range(y_max - 1, y_min - 1, -1):
                    df_prev = df[df["YEAR"] == y_back]
                    if len(df_prev) > 0:
                        for m in range(12, 0, -1):
                            val = df_prev.iloc[0, m]
                            if pd.notna(val) and UMBRAL_SENTINELA_MIN <= float(val) <= UMBRAL_SENTINELA_MAX:
                                ultimo_mes_num = m
                                y_max = y_back
                                break
                    if ultimo_mes_num > 0:
                        break

            ultimo_mes_str = f"{NOMBRES_MESES[ultimo_mes_num - 1]} ({y_max})" if ultimo_mes_num > 0 else f"Sin datos ({y_max})"
            estado = "✓ Disponible" if total_anios >= 30 else "✓ Cobertura Parcial"
        else:
            y_min = pd.NA
            y_max = pd.NA
            ultimo_mes_str = "Sin datos"
            total_anios = 0

            # Determinar si existe el archivo en disco pero no pudo ser cargado (Error) o si no existe (No descargado)
            csv_name = meta.get("filename_csv", f"data{codigo}.csv")
            txt_name = meta.get("filename_txt", f"data{codigo}.txt")
            if data_dir and data_dir != ".":
                candidatos_dir = [data_dir, os.path.join(data_dir, "data")]
            else:
                candidatos_dir = [
                    "data",
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "."
                ]
            archivo_existe = False
            for d in candidatos_dir:
                if (csv_name and os.path.exists(os.path.join(d, csv_name))) or (txt_name and os.path.exists(os.path.join(d, txt_name))):
                    archivo_existe = True
                    break

            estado = "⚠ Error" if archivo_existe else "✗ No disponible"

        variable_type = meta.get("variable_type", "anomalía")
        col_usada = meta.get("variable_column", "ENE..DIC")
        exact_var = meta.get("exact_variable_used", variable)

        filas.append({
            "Código": codigo,
            "Nombre": nombre,
            "Estado": estado,
            "Primer Año": y_min,
            "Último Año": y_max,
            "Último Mes": ultimo_mes_str,
            "Años Registrados": total_anios,
            "Institución": institucion,
            "Región": region,
            "Variable Física": variable,
            "Tipo de Variable": variable_type,
            "Columna Fuente": col_usada,
            "Variable en Motor": exact_var,
            "Unidad": unidad,
            "Frecuencia": frecuencia,
            "URL": url,
            "DOI": doi,
        })

    df_salud = pd.DataFrame(filas)
    if not df_salud.empty:
        df_salud["Primer Año"] = pd.to_numeric(df_salud["Primer Año"], errors="coerce").astype("Int64")
        df_salud["Último Año"] = pd.to_numeric(df_salud["Último Año"], errors="coerce").astype("Int64")
        df_salud["Años Registrados"] = pd.to_numeric(df_salud["Años Registrados"], errors="coerce").fillna(0).astype("int64")

        columnas_texto = [
            "Código", "Nombre", "Estado", "Último Mes", "Institución", "Región",
            "Variable Física", "Tipo de Variable", "Columna Fuente", "Variable en Motor",
            "Unidad", "Frecuencia", "URL", "DOI"
        ]
        for col_t in columnas_texto:
            if col_t in df_salud.columns:
                df_salud[col_t] = df_salud[col_t].fillna("").astype(str)

    return df_salud
