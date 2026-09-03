"""
Módulo de visualización gráfica científica individual por índice para Aanalogos.
Genera la representación gráfica de alta calidad con doble eje (Pearson r y MAD),
líneas de umbral, resaltado de años análogos y paneles de parámetros y resumen.
"""

import os
import re
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from .results import ResultadoAnalogos
from .catalog import cargar_catalogo_indices

MESES_MAP = {
    "ENE": "Ene", "FEB": "Feb", "MAR": "Mar", "ABR": "Abr",
    "MAY": "May", "JUN": "Jun", "JUL": "Jul", "AGO": "Ago",
    "SET": "Sep", "SEP": "Sep", "OCT": "Oct", "NOV": "Nov", "DIC": "Dic"
}


def formatear_mes_anio(item_str: str) -> str:
    """
    Convierte cadenas como 'ABR(2025)' o 'ABR 2025' a formato estandarizado 'Abr 2025'.
    """
    m = re.match(r"([A-Za-z]+)\s*\(?(\d{4})\)?", str(item_str).strip())
    if m:
        mes_raw = m.group(1).upper()
        anio_raw = m.group(2)
        mes_fmt = MESES_MAP.get(mes_raw, mes_raw.capitalize())
        return f"{mes_fmt} {anio_raw}"
    return str(item_str)


def generar_grafico_individual_indice(
    resultado: ResultadoAnalogos,
    codigo_indice: str,
    catalogo: Optional[Dict[str, Any]] = None,
    ruta_salida: Optional[str] = None
) -> plt.Figure:
    """
    Genera una figura científica individual para el índice especificado, reproduciendo
    fielmente la composición de referencia: doble eje (Pearson r y MAD), líneas de umbral,
    rectángulos verticales de años análogos con etiqueta inferior, y tarjetas de parámetros/resumen.
    
    Parámetros:
    - resultado: Objeto ResultadoAnalogos devuelto por el motor.
    - codigo_indice: Código del índice a graficar (ej. 'AMO', 'TNA', 'RONI').
    - catalogo: Catálogo de metadatos de índices (opcional).
    - ruta_salida: Ruta de archivo opcional para guardar el PNG.
    
    Retorna:
    - matplotlib.figure.Figure lista para renderizar en Streamlit o guardar en disco.
    """
    if catalogo is None:
        catalogo = cargar_catalogo_indices()

    meta = catalogo.get(codigo_indice, {})
    nombre_indice = meta.get("name", codigo_indice)
    institucion_fuente = meta.get("source_inst", "NOAA PSL / CPC")

    # Extraer trazabilidad calculada para el índice
    df_traz = resultado.tabla_trazabilidad
    if df_traz is None or df_traz.empty:
        raise ValueError("El resultado no contiene tabla de trazabilidad estadística.")

    df_idx = df_traz[df_traz["Indice"] == codigo_indice].sort_values("YEAR").copy()
    if df_idx.empty:
        raise ValueError(f"No se encontraron datos de trazabilidad para el índice '{codigo_indice}'.")

    # Filtrar registros que tengan valores finitos de Pearson o MAD
    df_validos = df_idx.dropna(subset=["Pearson", "MAD"])
    if df_validos.empty:
        raise ValueError(f"El índice '{codigo_indice}' no cuenta con datos numéricos suficientes en el período.")

    years = df_validos["YEAR"].values
    r_vals = df_validos["Pearson"].values
    mad_vals = df_validos["MAD"].values

    # Obtener umbrales utilizados por el motor
    if "Umbral_r" in df_validos.columns and "Umbral_MAD" in df_validos.columns:
        r_th = float(df_validos["Umbral_r"].iloc[0])
        mad_th = float(df_validos["Umbral_MAD"].iloc[0])
    elif codigo_indice in resultado.umbrales_utilizados:
        r_th, mad_th = resultado.umbrales_utilizados[codigo_indice]
    else:
        r_th, mad_th = 0.50, 0.60

    # Años análogos identificados directamente por la condición del motor (Coincidencia == 1)
    anios_analogos = df_validos[df_validos["Coincidencia"] == 1]["YEAR"].tolist()

    # Formateo de descripción de la ventana
    v_seq = resultado.ventana_temporal
    if v_seq and len(v_seq) >= 2:
        v_inicio = formatear_mes_anio(v_seq[0])
        v_fin = formatear_mes_anio(v_seq[-1])
        ventana_desc = f"{v_inicio} a {v_fin} ({resultado.longitud_ventana} meses)"
    elif v_seq and len(v_seq) == 1:
        ventana_desc = f"{formatear_mes_anio(v_seq[0])} ({resultado.longitud_ventana} meses)"
    else:
        ventana_desc = f"Últimos {resultado.longitud_ventana} meses"

    # Escala de MAD para alinear con los 9 ticks de r (-1.00 a 1.00, 8 intervalos)
    max_mad = float(np.nanmax(mad_vals)) if len(mad_vals) > 0 else 1.0
    criterio_max = max(max_mad, mad_th)
    if criterio_max <= 1.8:
        mad_max = 2.00
    elif criterio_max <= 3.6:
        mad_max = 4.00
    elif criterio_max <= 7.2:
        mad_max = 8.00
    elif criterio_max <= 15.0:
        mad_max = 16.00
    else:
        mad_max = float(np.ceil(criterio_max * 1.25 / 8.0) * 8.0)

    # Crear figura 16:9 de alta definición
    fig = plt.figure(figsize=(16, 9), dpi=150, facecolor='#FFFFFF')

    # Borde exterior redondeado de la tarjeta
    outer_rect = mpatches.FancyBboxPatch(
        (0.005, 0.005), 0.99, 0.99,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=fig.transFigure,
        facecolor="none",
        edgecolor="#D0E2F0",
        linewidth=1.2,
        zorder=0
    )
    fig.add_artist(outer_rect)

    # 1. Título y Subtítulo
    fig.text(
        0.5, 0.962,
        f"{codigo_indice} ({nombre_indice})",
        ha="center", va="center",
        fontsize=20, fontweight="bold",
        color="#0F2942"
    )
    fig.text(
        0.5, 0.930,
        f"Correlación y MAD – Ventana: {ventana_desc}",
        ha="center", va="center",
        fontsize=13, color="#475569"
    )

    # 2. Badges / Pills de Leyenda superiores
    # Pill Izquierda: Correlación
    pill_corr = mpatches.FancyBboxPatch(
        (0.08, 0.880), 0.20, 0.032,
        boxstyle="round,pad=0.005,rounding_size=0.01",
        transform=fig.transFigure,
        facecolor="#FFFFFF",
        edgecolor="#CFD8DC",
        linewidth=1.0,
        zorder=2
    )
    fig.add_artist(pill_corr)
    line_corr_sample = Line2D(
        [0.092, 0.118], [0.896, 0.896],
        transform=fig.transFigure,
        color="#1565C0", linestyle="--", dashes=(4, 3), linewidth=1.2,
        marker="o", markersize=5, markerfacecolor="#1976D2", markeredgecolor="#0D47A1",
        zorder=3
    )
    fig.add_artist(line_corr_sample)
    fig.text(0.126, 0.896, "Correlación (Pearson r)", ha="left", va="center", color="#1E293B", fontsize=11)

    # Pill Derecha: MAD
    pill_mad = mpatches.FancyBboxPatch(
        (0.66, 0.880), 0.26, 0.032,
        boxstyle="round,pad=0.005,rounding_size=0.01",
        transform=fig.transFigure,
        facecolor="#FFFFFF",
        edgecolor="#CFD8DC",
        linewidth=1.0,
        zorder=2
    )
    fig.add_artist(pill_mad)
    line_mad_sample = Line2D(
        [0.675, 0.701], [0.896, 0.896],
        transform=fig.transFigure,
        color="#D32F2F", linestyle="--", dashes=(4, 3), linewidth=1.2,
        marker="o", markersize=5, markerfacecolor="#D32F2F", markeredgecolor="#B71C1C",
        zorder=3
    )
    fig.add_artist(line_mad_sample)
    fig.text(0.709, 0.896, "MAD (Desviación Absoluta Media)", ha="left", va="center", color="#1E293B", fontsize=11)

    # 3. Ejes Principales
    ax1 = fig.add_axes([0.08, 0.33, 0.84, 0.47])
    ax2 = ax1.twinx()

    min_year = int(min(years))
    max_year = int(max(years))
    ax1.set_xlim(min_year - 1.5, max_year + 1.5)
    ax2.set_xlim(min_year - 1.5, max_year + 1.5)

    # Configuración de ticks en X: cada 5 años
    tick_start = int(np.floor(min_year / 5) * 5)
    if min_year % 5 != 0:
        xticks = [min_year] + list(range(tick_start + 5, max_year + 1, 5))
    else:
        xticks = list(range(tick_start, max_year + 1, 5))
    if max_year not in xticks and (max_year - xticks[-1] >= 2):
        xticks.append(max_year)

    ax1.set_xticks(xticks)
    ax1.set_xticklabels([str(y) for y in xticks], rotation=35, ha="right", fontsize=10, color="#334155")
    ax1.set_xlabel("Año", fontsize=12, fontweight="bold", color="#1E293B", labelpad=5)

    # Configuración Eje Y1 (Correlación r)
    ax1.set_ylim(-1.05, 1.05)
    r_ticks = np.linspace(-1.0, 1.0, 9)
    ax1.set_yticks(r_ticks)
    ax1.set_yticklabels([f"{val:.2f}" for val in r_ticks], color="#1565C0", fontsize=10)
    ax1.set_ylabel("Coeficiente de correlación (r)", fontsize=12, fontweight="bold", color="#1565C0", labelpad=10)

    # Configuración Eje Y2 (MAD)
    ax2.set_ylim(0.0, mad_max * 1.025)
    mad_ticks = np.linspace(0.0, mad_max, 9)
    ax2.set_yticks(mad_ticks)
    ax2.set_yticklabels([f"{val:.2f}" for val in mad_ticks], color="#D32F2F", fontsize=10)
    ax2.set_ylabel("MAD", fontsize=12, fontweight="bold", color="#D32F2F", labelpad=10)

    # Rejilla horizontal sutil
    ax1.grid(axis="y", linestyle="--", alpha=0.5, color="#CFD8DC", linewidth=0.8, zorder=1)

    # Estilo de espinas
    ax1.spines["left"].set_color("#1565C0")
    ax1.spines["left"].set_linewidth(1.2)
    ax1.spines["bottom"].set_color("#94A3B8")
    ax1.spines["top"].set_color("#E2E8F0")
    ax1.spines["right"].set_visible(False)

    ax2.spines["right"].set_color("#D32F2F")
    ax2.spines["right"].set_linewidth(1.2)
    ax2.spines["bottom"].set_color("#94A3B8")
    ax2.spines["top"].set_color("#E2E8F0")
    ax2.spines["left"].set_visible(False)

    # 4. Resaltado de Años Análogos (Rectángulos verticales de altura completa con etiqueta superior vertical a 90°)
    h_bottom = -1.02
    h_top = 1.02
    rect_height = h_top - h_bottom

    for y_match in anios_analogos:
        rect_patch = mpatches.FancyBboxPatch(
            (y_match - 0.75, h_bottom), 1.5, rect_height,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor="#E8F5E9",
            edgecolor="#2E7D32",
            linewidth=1.2,
            alpha=0.55,
            zorder=2
        )
        ax1.add_patch(rect_patch)

        # Etiqueta en la parte superior del rectángulo con orientación vertical (90°) y centrada en la banda
        y_label_pos = 1.03
        ax1.text(
            y_match, y_label_pos, str(y_match),
            ha="center", va="bottom",
            rotation=90,
            fontsize=9.5, fontweight="bold",
            color="#1B5E20",
            clip_on=False,
            zorder=6
        )

    # 5. Líneas de Umbral Horizontales
    # Umbral r
    ax1.axhline(r_th, color="#1565C0", linestyle="--", dashes=(6, 3), linewidth=1.5, zorder=3)
    ax1.text(
        min_year - 0.8, r_th + 0.03,
        f"Umbral r = {r_th:.2f}",
        color="#1565C0", fontsize=10.5, fontweight="bold",
        va="bottom", zorder=5
    )

    # Umbral MAD
    ax2.axhline(mad_th, color="#D32F2F", linestyle="--", dashes=(6, 3), linewidth=1.5, zorder=3)
    ax2.text(
        max_year + 0.8, mad_th - (0.04 * mad_max),
        f"Umbral MAD = {mad_th:.2f}",
        color="#D32F2F", fontsize=10.5, fontweight="bold",
        ha="right", va="top", zorder=5,
        bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none", alpha=0.85)
    )

    # 6. Series de datos
    # Pearson r
    ax1.plot(
        years, r_vals,
        color="#1976D2", linestyle="--", dashes=(4, 3), linewidth=1.2,
        marker="o", markersize=5, markerfacecolor="#1976D2", markeredgecolor="#0D47A1", markeredgewidth=0.8,
        zorder=4
    )

    # MAD
    ax2.plot(
        years, mad_vals,
        color="#D32F2F", linestyle="--", dashes=(4, 3), linewidth=1.2,
        marker="o", markersize=5, markerfacecolor="#D32F2F", markeredgecolor="#B71C1C", markeredgewidth=0.8,
        zorder=4
    )

    # 7. Leyenda inferior de Años Análogos (debajo del eje X con holgura)
    pill_match = mpatches.FancyBboxPatch(
        (0.35, 0.235), 0.038, 0.024,
        boxstyle="round,pad=0.003,rounding_size=0.008",
        transform=fig.transFigure,
        facecolor="#E8F5E9",
        edgecolor="#2E7D32",
        linewidth=1.2,
        zorder=2
    )
    fig.add_artist(pill_match)
    fig.text(
        0.398, 0.247,
        "Años análogos (cumplen ambos umbrales)",
        ha="left", va="center",
        fontsize=11.5, fontweight="bold",
        color="#1E293B"
    )

    # 8. Paneles inferiores (Tarjetas lado a lado)
    # Panel Izquierdo: Parámetros de umbral
    card_left = mpatches.FancyBboxPatch(
        (0.025, 0.052), 0.46, 0.165,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=fig.transFigure,
        facecolor="#F4F8FB",
        edgecolor="#90CAF9",
        linewidth=1.2,
        zorder=2
    )
    fig.add_artist(card_left)

    fig.text(
        0.04, 0.18,
        "Parámetros de umbral (definidos por el usuario)",
        fontsize=12, fontweight="bold", color="#1565C0"
    )
    line_th_r = Line2D(
        [0.045, 0.065], [0.142, 0.142],
        transform=fig.transFigure,
        color="#1565C0", linestyle="--", dashes=(4, 2), linewidth=2.0,
        zorder=3
    )
    fig.add_artist(line_th_r)
    fig.text(0.075, 0.142, f"Umbral de correlación (r) mínimo: {r_th:.2f}", color="#1E293B", fontsize=11, va="center")

    line_th_mad = Line2D(
        [0.045, 0.065], [0.100, 0.100],
        transform=fig.transFigure,
        color="#D32F2F", linestyle="--", dashes=(4, 2), linewidth=2.0,
        zorder=3
    )
    fig.add_artist(line_th_mad)
    fig.text(0.075, 0.100, f"Umbral de MAD máximo: {mad_th:.2f}", color="#1E293B", fontsize=11, va="center")

    # Panel Derecho: Resumen
    card_right = mpatches.FancyBboxPatch(
        (0.505, 0.052), 0.47, 0.165,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=fig.transFigure,
        facecolor="#FFFDF5",
        edgecolor="#FFE082",
        linewidth=1.2,
        zorder=2
    )
    fig.add_artist(card_right)

    fig.text(
        0.52, 0.18,
        "Resumen",
        fontsize=12, fontweight="bold", color="#8D6E63"
    )
    fig.text(0.525, 0.142, "•", color="#8D6E63", fontsize=14, va="center")
    fig.text(0.542, 0.142, f"Total de años evaluados: {len(years)} ({min_year}–{max_year})", color="#1E293B", fontsize=11, va="center")
    fig.text(0.525, 0.100, "•", color="#8D6E63", fontsize=14, va="center")
    fig.text(0.542, 0.100, f"Años análogos encontrados: {len(anios_analogos)}", color="#1E293B", fontsize=11, va="center")

    # 9. Pie de página (Footer)
    fig.text(
        0.025, 0.02,
        f"Fuente: {institucion_fuente} | Cálculos: Aanalogos v3.2.0 | Ventana de comparación: {ventana_desc}",
        fontsize=9, color="#94A3B8"
    )

    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        fig.savefig(ruta_salida, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')

    return fig
