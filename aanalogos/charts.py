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
import matplotlib.patheffects as path_effects

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
    ruta_salida: Optional[str] = None,
    orden: str = "cronologico"
) -> plt.Figure:
    """
    Genera una figura científica individual para el índice especificado, reproduciendo
    fielmente la composición de referencia: doble eje (Pearson r y MAD), líneas de umbral,
    rectángulos verticales de años análogos con etiqueta superior a 90°, y tarjetas de parámetros/resumen.
    
    Parámetros:
    - resultado: Objeto ResultadoAnalogos devuelto por el motor.
    - codigo_indice: Código del índice a graficar (ej. 'AMO', 'TNA', 'RONI').
    - catalogo: Catálogo de metadatos de índices (opcional).
    - ruta_salida: Ruta de archivo opcional para guardar el PNG.
    - orden: Modo de ordenamiento del eje X ('cronologico' o 'pearson_desc').
    
    Retorna:
    - matplotlib.figure.Figure lista para renderizar en Streamlit o guardar en disco.
    """
    if catalogo is None:
        catalogo = cargar_catalogo_indices()

    meta = catalogo.get(codigo_indice, {})
    nombre_indice = meta.get("name", codigo_indice)
    institucion_fuente = meta.get("source_inst", meta.get("source", "NOAA PSL / CPC"))

    # Extraer trazabilidad calculada para el índice
    df_traz = resultado.tabla_trazabilidad
    if df_traz is None or df_traz.empty:
        raise ValueError("El resultado no contiene tabla de trazabilidad estadística.")

    df_idx = df_traz[df_traz["Indice"] == codigo_indice].copy()
    if df_idx.empty:
        raise ValueError(f"No se encontraron datos de trazabilidad para el índice '{codigo_indice}'.")

    # Filtrar registros que tengan valores finitos de Pearson o MAD
    df_validos = df_idx.dropna(subset=["Pearson", "MAD"]).copy()
    if df_validos.empty:
        raise ValueError(f"El índice '{codigo_indice}' no cuenta con datos numéricos suficientes en el período.")

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

    # Ordenamiento de datos y configuración del eje X
    if orden == "pearson_desc":
        df_plot = df_validos.sort_values("Pearson", ascending=False).reset_index(drop=True)
        n_cand = len(df_plot)
        x_vals = np.arange(n_cand)
        x_margin = 0.8
        x_min_lim = -x_margin
        x_max_lim = n_cand - 1 + x_margin
        x_label_title = "Año (ordenado por correlación, mayor a menor)"
        subtitulo_texto = f"Correlación y MAD – Años ordenados por correlación (mayor a menor) – Ventana: {ventana_desc}"
    else:
        df_plot = df_validos.sort_values("YEAR").reset_index(drop=True)
        x_vals = df_plot["YEAR"].values
        n_cand = len(df_plot)
        min_year = int(min(x_vals))
        max_year = int(max(x_vals))
        x_margin = max(2.5, float(np.round((max_year - min_year) * 0.035)))
        x_min_lim = min_year - x_margin
        x_max_lim = max_year + x_margin
        x_label_title = "Año"
        subtitulo_texto = f"Correlación y MAD – Ventana: {ventana_desc}"

    # Escala dinámica de MAD para 7 ticks (6 intervalos) que adapta la altura real de cada índice
    mad_vals_all = df_plot["MAD"].values
    max_mad = float(np.nanmax(mad_vals_all)) if len(mad_vals_all) > 0 else 1.0
    criterio_max = max(max_mad, mad_th) * 1.15

    posibles_pasos = [0.05, 0.10, 0.15, 0.20, 0.25, 0.50, 1.00, 1.50, 2.00, 2.50, 5.00]
    step = posibles_pasos[-1]
    for s in posibles_pasos:
        if s * 6 >= criterio_max:
            step = s
            break
    else:
        step = float(np.ceil(criterio_max / 6.0))

    mad_max_axis = step * 6

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
        subtitulo_texto,
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

    ax1.set_xlim(x_min_lim, x_max_lim)
    ax2.set_xlim(x_min_lim, x_max_lim)

    if orden == "pearson_desc":
        step_tick = 5 if n_cand >= 20 else 2
        xticks = [0] + list(range(step_tick, n_cand, step_tick))
        if (n_cand - 1) not in xticks and ((n_cand - 1) - xticks[-1] >= 2):
            xticks.append(n_cand - 1)
        xticklabels = [str(int(df_plot.loc[i, "YEAR"])) for i in xticks]
        ax1.set_xticks(xticks)
        ax1.set_xticklabels(xticklabels, rotation=35, ha="right", fontsize=10, color="#334155")
    else:
        tick_start = int(np.floor(min_year / 5) * 5)
        if min_year % 5 != 0:
            xticks = [min_year] + list(range(tick_start + 5, max_year + 1, 5))
        else:
            xticks = list(range(tick_start, max_year + 1, 5))
        if max_year not in xticks and (max_year - xticks[-1] >= 2):
            xticks.append(max_year)
        ax1.set_xticks(xticks)
        ax1.set_xticklabels([str(y) for y in xticks], rotation=35, ha="right", fontsize=10, color="#334155")

    ax1.set_xlabel(x_label_title, fontsize=12, fontweight="bold", color="#1E293B", labelpad=5)

    # Configuración Eje Y1 (Correlación r: -1.50 a +1.50)
    ax1.set_ylim(-1.50, 1.50)
    r_ticks = np.linspace(-1.50, 1.50, 7)
    ax1.set_yticks(r_ticks)
    ax1.set_yticklabels([f"{val:+.2f}" if val != 0 else "0.00" for val in r_ticks], color="#1565C0", fontsize=10)
    ax1.set_ylabel("Coeficiente de correlación (r)", fontsize=12, fontweight="bold", color="#1565C0", labelpad=10)

    # Configuración Eje Y2 (MAD: 0.00 a mad_max_axis con 7 ticks coincidentes)
    ax2.set_ylim(0.0, mad_max_axis)
    mad_ticks = np.linspace(0.0, mad_max_axis, 7)
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

    # 4. Resaltado de Años Análogos (Rectángulos verticales de -1.10 a +1.00)
    h_bottom = -1.10
    h_top = 1.00
    rect_height = h_top - h_bottom
    band_width = 0.9 if orden == "pearson_desc" else 1.5

    for i, row in df_plot.iterrows():
        if row["Coincidencia"] == 1:
            x_pos = i if orden == "pearson_desc" else row["YEAR"]
            rect_patch = mpatches.FancyBboxPatch(
                (x_pos - (band_width / 2.0), h_bottom), band_width, rect_height,
                boxstyle="round,pad=0.02,rounding_size=0.15",
                facecolor="#E8F5E9",
                edgecolor="#2E7D32",
                linewidth=1.2,
                alpha=0.55,
                zorder=2
            )
            ax1.add_patch(rect_patch)

            # Etiqueta en la parte superior fuera de la banda (y = 1.06) con orientación vertical (90°)
            ax1.text(
                x_pos, 1.06, str(int(row["YEAR"])),
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
    x_lbl_r = (-x_margin * 0.5) if orden == "pearson_desc" else (min_year - (x_margin * 0.7))
    txt_r = ax1.text(
        x_lbl_r, r_th + 0.05,
        f"Umbral r = {r_th:.2f}",
        color="#1565C0", fontsize=10.5, fontweight="bold",
        va="bottom", zorder=5
    )
    txt_r.set_path_effects([path_effects.withStroke(linewidth=3.5, foreground="white")])

    # Umbral MAD
    ax2.axhline(mad_th, color="#D32F2F", linestyle="--", dashes=(6, 3), linewidth=1.5, zorder=3)
    x_lbl_mad = (n_cand - 1 + (x_margin * 0.5)) if orden == "pearson_desc" else (max_year + (x_margin * 0.7))
    txt_mad = ax2.text(
        x_lbl_mad, mad_th + (0.015 * mad_max_axis),
        f"Umbral MAD = {mad_th:.2f}",
        color="#D32F2F", fontsize=10.5, fontweight="bold",
        ha="right", va="bottom", zorder=5
    )
    txt_mad.set_path_effects([path_effects.withStroke(linewidth=3.5, foreground="white")])

    # 6. Series de datos
    # Pearson r
    ax1.plot(
        x_vals, df_plot["Pearson"].values,
        color="#1976D2", linestyle="--", dashes=(4, 3), linewidth=1.2,
        marker="o", markersize=5, markerfacecolor="#1976D2", markeredgecolor="#0D47A1", markeredgewidth=0.8,
        zorder=4
    )

    # MAD
    ax2.plot(
        x_vals, df_plot["MAD"].values,
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
        0.045, 0.185,
        "Parámetros de umbral (definidos por el usuario)",
        fontsize=13, fontweight="bold", color="#0F2942"
    )
    l_r = Line2D(
        [0.050, 0.075], [0.145, 0.145],
        transform=fig.transFigure,
        color="#1565C0", linestyle="--", dashes=(6, 3), linewidth=2.0
    )
    fig.add_artist(l_r)
    fig.text(0.085, 0.145, f"Umbral de correlación (r) mínimo: {r_th:.2f}", fontsize=12, color="#1E293B", va="center")

    l_mad = Line2D(
        [0.050, 0.075], [0.095, 0.095],
        transform=fig.transFigure,
        color="#D32F2F", linestyle="--", dashes=(6, 3), linewidth=2.0
    )
    fig.add_artist(l_mad)
    fig.text(0.085, 0.095, f"Umbral de MAD máximo: {mad_th:.2f}", fontsize=12, color="#1E293B", va="center")

    # Panel Derecho: Resumen
    min_cand_y = int(df_validos["YEAR"].min())
    max_cand_y = int(df_validos["YEAR"].max())
    total_eval = len(df_validos)
    total_matches = len(anios_analogos)

    card_right = mpatches.FancyBboxPatch(
        (0.515, 0.052), 0.46, 0.165,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=fig.transFigure,
        facecolor="#FFFDF5",
        edgecolor="#FFE082",
        linewidth=1.2,
        zorder=2
    )
    fig.add_artist(card_right)

    fig.text(
        0.535, 0.185,
        "Resumen",
        fontsize=13, fontweight="bold", color="#6A4B00"
    )
    fig.text(0.540, 0.145, "•", fontsize=16, color="#B45309", va="center")
    fig.text(0.555, 0.145, f"Total de años evaluados: {total_eval} ({min_cand_y}–{max_cand_y})", fontsize=12, color="#1E293B", va="center")
    fig.text(0.540, 0.095, "•", fontsize=16, color="#B45309", va="center")
    fig.text(0.555, 0.095, f"Años análogos encontrados: {total_matches}", fontsize=12, color="#1E293B", va="center")

    # 9. Pie de página (Footer)
    fig.text(
        0.025, 0.018,
        f"Fuente: {institucion_fuente} | Cálculos: Aanalogos | Ventana: {resultado.longitud_ventana} meses",
        fontsize=9.5, color="#64748B"
    )

    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        fig.savefig(ruta_salida, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')

    return fig
