"""
Sistema Interactivo de Selección de Años Análogos Climáticos
Metodología Original: Anthony Segura García (UCR / IMN)
Framework: Streamlit
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Agregar directorio del proyecto para importar aanalogos
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from aanalogos import (
    calcular_analogos,
    cargar_todas_oscilaciones,
    extraer_ventana,
    obtener_descripcion_ventana,
    UMBRALES_OSCILACIONES,
    NOMBRES_MESES,
)

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Años Análogos Climáticos | IMN - UCR",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diccionario de nombres legibles para los 19 índices
NOMBRES_LEGIBLES = {
    "AMO": "AMO — Oscilación Multidecadal del Atlántico",
    "AO": "AO — Oscilación del Ártico",
    "MEI": "MEI — Índice Multivariado del ENOS (v2)",
    "ONI": "ONI — Índice Oceánico de El Niño",
    "NAO": "NAO — Oscilación del Atlántico Norte",
    "PDO": "PDO — Oscilación Decadal del Pacífico",
    "TNA": "TNA — Atlántico Norte Tropical",
    "SSTA_12": "SSTA 1+2 — Anomalía TSM Niño 1+2",
    "SSTA_3": "SSTA 3 — Anomalía TSM Niño 3",
    "SSTA_4": "SSTA 4 — Anomalía TSM Niño 4",
    "SSTA_34": "SSTA 3.4 — Anomalía TSM Niño 3.4",
    "AtlTROP": "AtlTROP — Anomalía Atlántico Tropical",
    "SAtl": "SAtl — Anomalía Atlántico Sur",
    "NAtl": "NAtl — Anomalía Atlántico Norte",
    "CAR": "CAR — Anomalía Mar Caribe",
    "WHWP": "WHWP — Piscina Cálida del Hemisferio Occidental",
    "PNA": "PNA — Patrón Pacífico-Norteamericano",
    "SOI": "SOI — Índice de Oscilación del Sur",
    "AMO_CSU": "AMO (CSU) — AMO Colorado State University",
}

MAPA_ETIQUETA_A_CODIGO = {v: k for k, v in NOMBRES_LEGIBLES.items()}

# Cache de carga de oscilaciones para rendimiento óptimo
@st.cache_resource(show_spinner="Cargando series históricas de oscilaciones...")
def obtener_datos_oscilaciones():
    return cargar_todas_oscilaciones(DIRECTORIO_ACTUAL)

oscilaciones_disponibles = obtener_datos_oscilaciones()

# ==============================================================================
# ENCABEZADO INSTITUCIONAL
# ==============================================================================
st.title("🌦️ Sistema de Selección de Años Análogos Climáticos")
st.markdown(
    """
    **Gerencia de Meteorología — Observatorio de Amenazas y Recursos Naturales**  
    *Ministerio de Medio Ambiente y Recursos Naturales (MARN), El Salvador*  
    *Herramienta computacional para análisis de análogos climáticos y apoyo al pronóstico estacional.*
    """
)
st.divider()

# ==============================================================================
# A. PANEL LATERAL DE CONFIGURACIÓN
# ==============================================================================
st.sidebar.header("⚙️ Configuración del Análisis")

year_objetivo = st.sidebar.number_input(
    "Año Objetivo ($Y_{\\text{obj}}$):",
    min_value=1950,
    max_value=2030,
    value=2015,
    step=1,
    help="Año climátológico que se desea comparar contra el registro histórico."
)

opciones_meses = [f"{i} — {NOMBRES_MESES[i-1]}" for i in range(1, 13)]
mes_seleccionado_str = st.sidebar.selectbox(
    "Mes Objetivo (Cierre de Ventana):",
    options=opciones_meses,
    index=9,  # Octubre por defecto (índice 9)
    help="Mes en el cual culmina la ventana retrospectiva móvil de 6 meses."
)
mes_objetivo = int(mes_seleccionado_str.split(" — ")[0])

# Preselección por defecto: AMO, PDO, TNA
default_indices = [
    NOMBRES_LEGIBLES["AMO"],
    NOMBRES_LEGIBLES["PDO"],
    NOMBRES_LEGIBLES["TNA"]
]

indices_seleccionados_str = st.sidebar.multiselect(
    "Selección de Índices / Oscilaciones:",
    options=list(NOMBRES_LEGIBLES.values()),
    default=default_indices,
    help="Seleccione una o más oscilaciones climáticas para el análisis multivariado."
)

indices_codigos = [MAPA_ETIQUETA_A_CODIGO[item] for item in indices_seleccionados_str]

boton_calcular = st.sidebar.button("🚀 Calcular Años Análogos", type="primary", use_container_width=True)

# Guardar estado de ejecución en session_state
if "resultado" not in st.session_state or boton_calcular:
    if indices_codigos:
        with st.spinner("Procesando análisis multivariado..."):
            st.session_state["resultado"] = calcular_analogos(
                year_objetivo=year_objetivo,
                mes_objetivo=mes_objetivo,
                indices=indices_codigos,
                oscilaciones_cargadas=oscilaciones_disponibles
            )
    else:
        st.session_state["resultado"] = None

resultado = st.session_state.get("resultado")

# ==============================================================================
# B. INFORMACIÓN Y DIAGNÓSTICO DE DATOS
# ==============================================================================
with st.expander("📊 Diagnóstico y Cobertura de Series Temporales Seleccionadas", expanded=False):
    if not indices_codigos:
        st.warning("Seleccione al menos un índice para ver la información de cobertura.")
    else:
        info_filas = []
        for cod in indices_codigos:
            if cod in oscilaciones_disponibles:
                df_osc = oscilaciones_disponibles[cod]
                y_min = int(df_osc["YEAR"].min())
                y_max = int(df_osc["YEAR"].max())
                
                # Encontrar último mes con datos válidos en el último año
                row_last = df_osc[df_osc["YEAR"] == y_max].iloc[0]
                meses_validos = [m for m in NOMBRES_MESES if not pd.isna(row_last[m])]
                ultimo_mes_str = meses_validos[-1] if meses_validos else "Sin datos"
                
                # Verificar vector objetivo
                v_obj = extraer_ventana(df_osc, year_objetivo, mes_objetivo)
                estado_obj = "✅ Completo" if v_obj is not None else "⚠️ Incompleto / No disp."
                
                r_th, mad_th = UMBRALES_OSCILACIONES.get(cod, (0.6, 0.6))
                
                info_filas.append({
                    "Código": cod,
                    "Nombre": NOMBRES_LEGIBLES[cod],
                    "Primer Año": y_min,
                    "Último Año": y_max,
                    "Último Mes Registrado": f"{ultimo_mes_str} ({y_max})",
                    "Vector Año Objetivo": estado_obj,
                    "Umbral Pearson (r >)": r_th,
                    "Umbral MAD (<)": mad_th
                })
        
        st.dataframe(pd.DataFrame(info_filas), use_container_width=True, hide_index=True)

if resultado is None or not indices_codigos:
    st.info("👈 Seleccione los parámetros en el panel lateral y presione **Calcular Años Análogos**.")
    st.stop()

if not resultado.es_valido:
    if resultado.indices_no_disponibles:
        st.error(f"❌ **Error de Validación Científica:** {resultado.mensaje_error}")
        st.info("💡 **Acción recomendada:** Deseleccione los índices sin cobertura para este año/mes objetivo o elija un año/mes con registro completo para todas las series solicitadas.")
    else:
        st.warning(f"⚠️ {resultado.mensaje_error}")
    st.stop()

# ==============================================================================
# C. RESULTADOS Y RANKING
# ==============================================================================
st.subheader("🏆 Ranking de Años Análogos")

# Tarjetas KPI de resumen
c1, c2, c3, c4 = st.columns(4)
c1.metric("Año Objetivo", f"{resultado.year_objetivo}")
c2.metric("Mes de Cierre", f"{NOMBRES_MESES[resultado.mes_objetivo-1]} ({resultado.mes_objetivo})")
c3.metric("Años Candidatos Evaluados", f"{len(resultado.anios_candidatos)} años")
max_coinc = int(resultado.tabla_coincidencias["Total"].max()) if len(resultado.tabla_coincidencias) > 0 else 0
c4.metric("Máxima Coincidencia", f"{max_coinc} / {len(resultado.indices_evaluados)}")

# Ventana temporal utilizada
st.caption(f"**Ventana Retrospectiva de 6 Meses:** {' ➔ '.join(resultado.ventana_temporal)}")

# Tabla formateada de ranking
df_res = resultado.tabla_coincidencias.copy()
df_res_display = []

rank = 1
for yr, row in df_res.iterrows():
    tot = int(row["Total"])
    # Extraer nombres de índices que coincidieron (valor = 1)
    coincidentes = [
        col.replace("Coincidencias ", "")
        for col in df_res.columns
        if col.startswith("Coincidencias ") and row[col] == 1
    ]
    str_coincidentes = ", ".join(coincidentes) if coincidentes else "—"
    
    df_res_display.append({
        "Ranking": rank,
        "Año Análogo": int(yr),
        "Total Coincidencias": tot,
        "Índices Coincidentes": str_coincidentes
    })
    rank += 1

df_ranking = pd.DataFrame(df_res_display)

st.dataframe(
    df_ranking,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ranking": st.column_config.NumberColumn(format="%d"),
        "Año Análogo": st.column_config.NumberColumn(format="%d"),
        "Total Coincidencias": st.column_config.ProgressColumn(
            min_value=0,
            max_value=len(resultado.indices_evaluados),
            format="%d"
        )
    }
)

st.divider()

# ==============================================================================
# D & E. DETALLE Y TRAZABILIDAD DEL AÑO SELECCIONADO
# ==============================================================================
st.subheader("🔍 Detalle Estadístico y Trazabilidad por Año Análogo")

col_sel, col_info = st.columns([1, 2])

with col_sel:
    opciones_anios = [int(r["Año Análogo"]) for r in df_res_display]
    anio_seleccionado = st.selectbox(
        "Seleccione un Año Análogo para inspeccionar:",
        options=opciones_anios,
        index=0
    )

with col_info:
    fila_sel = next(item for item in df_res_display if item["Año Análogo"] == anio_seleccionado)
    st.markdown(
        f"**Año Análogo Seleccionado:** `{anio_seleccionado}` | "
        f"**Total Coincidencias:** `{fila_sel['Total Coincidencias']} / {len(resultado.indices_evaluados)}` | "
        f"**Índices Coincidentes:** `{fila_sel['Índices Coincidentes']}`"
    )

# D. Tabla de Métricas por Índice
df_trace_year = resultado.tabla_trazabilidad[resultado.tabla_trazabilidad["YEAR"] == anio_seleccionado].copy()

tabla_detalle = []
for _, row_t in df_trace_year.iterrows():
    cod_ind = row_t["Indice"]
    r_th, mad_th = UMBRALES_OSCILACIONES.get(cod_ind, (0.6, 0.6))
    coincide_bool = int(row_t["Coincidencia"]) == 1
    
    tabla_detalle.append({
        "Índice": cod_ind,
        "Descripción": NOMBRES_LEGIBLES.get(cod_ind, cod_ind),
        "Pearson (r)": f"{row_t['Pearson']:.4f}",
        "Umbral r": f"> {r_th:.2f}",
        "MAD": f"{row_t['MAD']:.4f}",
        "Umbral MAD": f"< {mad_th:.2f}",
        "Condición": "✅ Coincide" if coincide_bool else "❌ No Cumple"
    })

st.markdown("##### Métricas Estadísticas del Año Seleccionado:")
st.dataframe(pd.DataFrame(tabla_detalle), use_container_width=True, hide_index=True)

# E. Trazabilidad de los 6 meses (Objetivo vs Análogo)
st.markdown("##### Trazabilidad de Valores Mensuales de la Ventana (Objetivo vs. Análogo):")

trazabilidad_meses_data = []
v_temporal_desc = resultado.ventana_temporal

for cod_ind in resultado.indices_evaluados:
    df_osc = oscilaciones_disponibles[cod_ind]
    v_obj_vals = extraer_ventana(df_osc, resultado.year_objetivo, resultado.mes_objetivo)
    v_ana_vals = extraer_ventana(df_osc, anio_seleccionado, resultado.mes_objetivo)
    
    for idx_m in range(6):
        mes_desc = v_temporal_desc[idx_m]
        val_obj = v_obj_vals[idx_m] if v_obj_vals is not None else np.nan
        val_ana = v_ana_vals[idx_m] if v_ana_vals is not None else np.nan
        diff_abs = abs(val_obj - val_ana) if not (np.isnan(val_obj) or np.isnan(val_ana)) else np.nan
        
        trazabilidad_meses_data.append({
            "Índice": cod_ind,
            "Mes Ventana": mes_desc,
            f"Valor {resultado.year_objetivo} (Objetivo)": round(val_obj, 4),
            f"Valor {anio_seleccionado} (Análogo)": round(val_ana, 4),
            "Diferencia Absoluta": round(diff_abs, 4)
        })

st.dataframe(pd.DataFrame(trazabilidad_meses_data), use_container_width=True, hide_index=True)

st.divider()

# ==============================================================================
# F. VISUALIZACIONES GRÁFICAS
# ==============================================================================
st.subheader("📈 Visualizaciones Climatológicas")

tab_graf1, tab_graf2 = st.tabs(["Comparación Temporal de la Ventana (Objetivo vs. Análogo)", "Distribución del Ranking de Coincidencias"])

with tab_graf1:
    st.markdown(f"**Comparación de la trayectoria de 6 meses:** `{resultado.year_objetivo}` (Línea Continua Azul) vs. `{anio_seleccionado}` (Línea Discontinua Roja)")
    
    fig, axes = plt.subplots(
        nrows=len(resultado.indices_evaluados),
        ncols=1,
        figsize=(12, 3.5 * len(resultado.indices_evaluados)),
        sharex=True
    )
    if len(resultado.indices_evaluados) == 1:
        axes = [axes]
        
    meses_eje = [m.split("(")[0] for m in resultado.ventana_temporal]
    
    for ax, cod_ind in zip(axes, resultado.indices_evaluados):
        df_osc = oscilaciones_disponibles[cod_ind]
        v_obj = extraer_ventana(df_osc, resultado.year_objetivo, resultado.mes_objetivo)
        v_ana = extraer_ventana(df_osc, anio_seleccionado, resultado.mes_objetivo)
        
        row_t = df_trace_year[df_trace_year["Indice"] == cod_ind].iloc[0]
        r_val = row_t["Pearson"]
        mad_val = row_t["MAD"]
        coinc_str = "COINCIDE" if int(row_t["Coincidencia"]) == 1 else "NO COINCIDE"
        
        ax.plot(meses_eje, v_obj, marker="o", color="#1f77b4", linewidth=2.5, label=f"Año Objetivo ({resultado.year_objetivo})")
        ax.plot(meses_eje, v_ana, marker="s", color="#d62728", linewidth=2.0, linestyle="--", label=f"Año Análogo ({anio_seleccionado})")
        
        ax.set_title(f"{NOMBRES_LEGIBLES[cod_ind]} — [ r = {r_val:.4f} | MAD = {mad_val:.4f} | {coinc_str} ]", fontsize=11, fontweight="bold")
        ax.set_ylabel("Valor / Anomalía", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", fontsize=9)
        
    plt.xlabel("Meses de la Ventana", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with tab_graf2:
    st.markdown("**Cantidad de Indicadores Coincidentes por Año Histórico:**")
    fig_bar, ax_bar = plt.subplots(figsize=(14, 5))
    
    df_bar = resultado.tabla_coincidencias.sort_values(by="Total", ascending=False)
    ax_bar.bar(df_bar.index.astype(str), df_bar["Total"], color="#e74c3c", edgecolor="#c0392b")
    
    max_t = int(df_bar["Total"].max()) if len(df_bar) > 0 else 1
    ax_bar.set_yticks(np.arange(0, max_t + 2, 1))
    ax_bar.set_xticks(range(len(df_bar)))
    ax_bar.set_xticklabels(df_bar.index.astype(str), rotation=75, fontsize=8)
    ax_bar.set_title(f"Años Análogos (Año Objetivo: {resultado.year_objetivo}, Mes: {resultado.mes_objetivo})", fontsize=12, fontweight="bold")
    ax_bar.set_ylabel("Cantidad de Indicadores", fontsize=10)
    ax_bar.set_xlabel("Años Candidatos", fontsize=10)
    ax_bar.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig_bar)
    plt.close()

st.divider()

# ==============================================================================
# G. CENTRO DE EXPORTACIÓN Y DESCARGAS
# ==============================================================================
st.subheader("📥 Exportación de Resultados")

col_d1, col_d2, col_d3 = st.columns(3)

# 1. CSV de Resultados
csv_resultados = df_ranking.to_csv(index=False).encode("utf-8")
col_d1.download_button(
    label="📄 Descargar Ranking (CSV)",
    data=csv_resultados,
    file_name=f"ranking_analogos_{resultado.year_objetivo}_m{resultado.mes_objetivo}.csv",
    mime="text/csv",
    use_container_width=True
)

# 2. CSV de Trazabilidad
csv_trazabilidad = resultado.tabla_trazabilidad.to_csv(index=False).encode("utf-8")
col_d2.download_button(
    label="📊 Descargar Trazabilidad Completa (CSV)",
    data=csv_trazabilidad,
    file_name=f"trazabilidad_{resultado.year_objetivo}_m{resultado.mes_objetivo}.csv",
    mime="text/csv",
    use_container_width=True
)

# 3. Informe de Texto TXT
txt_buffer = []
txt_buffer.append("=" * 80)
txt_buffer.append("INFORME DE AÑOS ANÁLOGOS CLIMÁTICOS")
txt_buffer.append("=" * 80)
txt_buffer.append(f"Año Objetivo:      {resultado.year_objetivo}")
txt_buffer.append(f"Mes Objetivo:      {resultado.mes_objetivo} ({NOMBRES_MESES[resultado.mes_objetivo-1]})")
txt_buffer.append(f"Ventana Temporal:  {' - '.join(resultado.ventana_temporal)}")
txt_buffer.append(f"Índices Evaluados: {', '.join(resultado.indices_evaluados)}")
txt_buffer.append(f"Años Candidatos:   {len(resultado.anios_candidatos)} años")
txt_buffer.append("\n" + "=" * 80)
txt_buffer.append("RANKING FINAL:")
txt_buffer.append("=" * 80)
txt_buffer.append(df_ranking.to_string(index=False))
txt_buffer.append("\n" + "=" * 80)
txt_buffer.append("TRAZABILIDAD ESTADÍSTICA:")
txt_buffer.append("=" * 80)
txt_buffer.append(resultado.tabla_trazabilidad.to_string(index=False))

txt_contenido = "\n".join(txt_buffer).encode("utf-8")
col_d3.download_button(
    label="📝 Descargar Informe Completo (TXT)",
    data=txt_contenido,
    file_name=f"informe_analogos_{resultado.year_objetivo}_m{resultado.mes_objetivo}.txt",
    mime="text/plain",
    use_container_width=True
)
