"""
Paquete climatológico para cálculo y selección automatizada de años análogos.
"""

from .engine import calcular_analogos
from .results import ResultadoAnalogos, MetricaDetallada
from .data import cargar_todas_oscilaciones, verificar_y_descargar_datos
from .windows import extraer_ventana, obtener_descripcion_ventana
from .metrics import calcular_metricas_vector
from .quality import limpiar_datos_indice, validar_vector_ventana
from .config import (
    UMBRALES_OSCILACIONES,
    NOMBRES_MESES,
    FUENTES_DATOS,
    LONGITUD_VENTANA_METODOLOGICA,
    LONGITUD_VENTANA_OPERACIONAL,
    obtener_umbrales_metodologicos,
)
from .catalog import (
    cargar_catalogo_indices,
    determinar_ultimo_mes_disponible,
    obtener_periodo_evaluacion_operacional,
    obtener_estado_fuentes,
    cargar_configuracion_institucional,
)
from .charts import generar_grafico_individual_indice

__version__ = "3.2.0"

__all__ = [
    "calcular_analogos",
    "ResultadoAnalogos",
    "MetricaDetallada",
    "cargar_todas_oscilaciones",
    "verificar_y_descargar_datos",
    "extraer_ventana",
    "obtener_descripcion_ventana",
    "calcular_metricas_vector",
    "limpiar_datos_indice",
    "validar_vector_ventana",
    "UMBRALES_OSCILACIONES",
    "NOMBRES_MESES",
    "FUENTES_DATOS",
    "LONGITUD_VENTANA_METODOLOGICA",
    "LONGITUD_VENTANA_OPERACIONAL",
    "obtener_umbrales_metodologicos",
    "cargar_catalogo_indices",
    "determinar_ultimo_mes_disponible",
    "obtener_periodo_evaluacion_operacional",
    "obtener_estado_fuentes",
    "cargar_configuracion_institucional",
    "generar_grafico_individual_indice",
]
