"""
Dataclasses y estructuras de resultados del motor de Años Análogos.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class MetricaDetallada:
    year: int
    indice: str
    pearson: float
    mad: float
    coincidencia: int


@dataclass
class ResultadoAnalogos:
    year_objetivo: int
    mes_objetivo: int
    indices_solicitados: List[str]
    indices_evaluados: List[str]
    ventana_temporal: List[str]
    anios_candidatos: List[int]
    tabla_coincidencias: pd.DataFrame
    tabla_trazabilidad: pd.DataFrame
    longitud_ventana: int = 6
    umbrales_utilizados: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    modo_analisis: str = "Metodológico"
    ranking: List[Tuple[int, int]] = field(default_factory=list)
    indices_no_disponibles: List[str] = field(default_factory=list)
    es_valido: bool = True
    mensaje_error: Optional[str] = None

    def __post_init__(self):
        if not self.ranking and len(self.tabla_coincidencias) > 0:
            self.ranking = [
                (int(idx), int(row["Total"]))
                for idx, row in self.tabla_coincidencias.iterrows()
            ]

    def guardar_txt(self, ruta_archivo: str = "Años_Análogos.txt") -> None:
        """Exporta la tabla consolidada al formato de texto estándar."""
        self.tabla_coincidencias.to_csv(ruta_archivo, sep=" ", mode="w")

    def guardar_trazabilidad(self, ruta_archivo: str = "Trazabilidad_Detallada.txt") -> None:
        """Exporta la tabla de trazabilidad estadística detallada."""
        self.tabla_trazabilidad.to_csv(ruta_archivo, sep=" ", index=False)

    def guardar_grafico(self, ruta_archivo: str = "Años_Análogos.png") -> None:
        """Genera y guarda el gráfico de barras de coincidencias."""
        if len(self.tabla_coincidencias) == 0:
            return
        plt.figure(figsize=(15, 6))
        self.tabla_coincidencias["Total"].plot(kind="bar", color="red", legend=True)
        max_total = int(self.tabla_coincidencias["Total"].max()) if len(self.tabla_coincidencias) > 0 else 1
        plt.yticks(np.arange(0, max_total + 2, 1))
        plt.xticks(rotation=70)
        plt.title(f"Años Análogos (Año Objetivo: {self.year_objetivo}, Mes: {self.mes_objetivo})")
        plt.ylabel("Cantidad de Indicadores")
        plt.xlabel("Años")
        plt.tight_layout()
        plt.savefig(ruta_archivo)
        plt.close()
