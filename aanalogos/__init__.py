"""
Paquete climatológico para cálculo y selección automatizada de años análogos.
"""

from .engine import calcular_analogos
from .results import ResultadoAnalogos, MetricaDetallada
from .data import cargar_todas_oscilaciones
from .windows import extraer_ventana, obtener_descripcion_ventana
from .metrics import calcular_metricas_vector
from .quality import limpiar_datos_indice, validar_vector_ventana
from .config import UMBRALES_OSCILACIONES, NOMBRES_MESES, FUENTES_DATOS

__version__ = "3.1.0"

__all__ = [
    "calcular_analogos",
    "ResultadoAnalogos",
    "MetricaDetallada",
    "cargar_todas_oscilaciones",
    "extraer_ventana",
    "obtener_descripcion_ventana",
    "calcular_metricas_vector",
    "limpiar_datos_indice",
    "validar_vector_ventana",
    "UMBRALES_OSCILACIONES",
    "NOMBRES_MESES",
    "FUENTES_DATOS",
]
