"""
Sistema Interactivo de Selección de Años Análogos Climáticos
Gerencia de Meteorología — MARN El Salvador
Framework: Streamlit
"""

import os
import sys
import datetime
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
    verificar_y_descargar_datos,
    extraer_ventana,
    obtener_descripcion_ventana,
    cargar_catalogo_indices,
    determinar_ultimo_mes_disponible,
    obtener_estado_fuentes,
    obtener_umbrales_metodologicos,
    UMBRALES_OSCILACIONES,
    NOMBRES_MESES,
    LONGITUD_VENTANA_METODOLOGICA,
    LONGITUD_VENTANA_OPERACIONAL,
)

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Años Análogos Climáticos | MARN El Salvador",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 1. Cargar catálogo de índices estructurado
@st.cache_data(show_spinner=False)
def get_catalogo():
    return cargar_catalogo_indices()


CATALOGO = get_catalogo()

# Mapeo de nombres legibles para los 19 índices
NOMBRES_LEGIBLES = {}
for cod in UMBRALES_OSCILACIONES.keys():
    if cod in CATALOGO:
        NOMBRES_LEGIBLES[cod] = f"{cod} — {CATALOGO[cod].get('name', cod)}"
    else:
        NOMBRES_LEGIBLES[cod] = cod

MAPA_ETIQUETA_A_CODIGO = {v: k for k, v in NOMBRES_LEGIBLES.items()}


# Cache de carga de oscilaciones para rendimiento óptimo
@st.cache_resource(show_spinner="Cargando series históricas de oscilaciones...")
def obtener_datos_oscilaciones():
    return cargar_todas_oscilaciones(DIRECTORIO_ACTUAL)


oscilaciones_disponibles = obtener_datos_oscilaciones()

# Verificación inicial de datos: si faltan datos locales, descargar
if not oscilaciones_disponibles or len(oscilaciones_disponibles) < 10:
    st.info(
        "Inicializando datos climáticos... Verificando y descargando las series de índices climáticos. Este proceso puede tardar unos minutos."
    )
    with st.spinner("Descargando series históricas oficiales..."):
        verificar_y_descargar_datos(DIRECTORIO_ACTUAL)
        st.cache_resource.clear()
        oscilaciones_disponibles = obtener_datos_oscilaciones()

# Inicialización de estado en session_state
if "umbrales_usuario" not in st.session_state:
    st.session_state["umbrales_usuario"] = obtener_umbrales_metodologicos()

# Determinar fecha y mes operacional por defecto
year_op_default, mes_op_default = determinar_ultimo_mes_disponible(
    oscilaciones_disponibles
)

# ==============================================================================
# PANEL LATERAL DE NAVEGACIÓN Y PARÁMETROS
# ==============================================================================
posibles_rutas_logo = [
    os.path.join(DIRECTORIO_ACTUAL, "docs", "img", "logo_MARN.png"),
    os.path.join(DIRECTORIO_ACTUAL, "docs", "img", "logo_marn.png"),
    os.path.join(DIRECTORIO_ACTUAL, "docs", "img", "marn_logo.png"),
]
logo_encontrado = None
for ruta in posibles_rutas_logo:
    if os.path.isfile(ruta):
        logo_encontrado = ruta
        break

if logo_encontrado:
    st.sidebar.image(logo_encontrado, width=180)

st.sidebar.title("🌦️ AAnalogos")
st.sidebar.caption("**MARN El Salvador** | Gerencia de Meteorología")

seccion_seleccionada = st.sidebar.radio(
    "Navegación del Sistema:",
    [
        "🌦️ Análisis de Años Análogos",
        "📊 Explorador de Índices",
        "📚 Metodología de Cálculo",
        "📈 Estado de Datos",
        "⚙️ Configuración de Umbrales",
    ],
    index=0,
)

st.sidebar.divider()

# ==============================================================================
# SECCIÓN 1: ANÁLISIS DE AÑOS ANÁLOGOS
# ==============================================================================
if seccion_seleccionada == "🌦️ Análisis de Años Análogos":
    st.title("🌦️ Sistema de Selección de Años Análogos Climáticos")
    st.markdown("""
        **Gerencia de Meteorología — Observatorio de Amenazas y Recursos Naturales**
        *Ministerio de Medio Ambiente y Recursos Naturales (MARN), El Salvador*
        """)
    st.divider()

    # Selección de Modo de Análisis
    col_mode, col_info = st.columns([1, 2])
    with col_mode:
        modo_analisis = st.radio(
            "**Modo de Análisis:**",
            ["Operacional", "Reanálisis Histórico"],
            index=0,
            horizontal=True,
            help="El modo operacional utiliza automáticamente el año actual, el último mes publicado y una ventana de 12 meses.",
        )

    # Preselección de índices en Sidebar
    default_indices = [
        NOMBRES_LEGIBLES.get("PDO", "PDO"),
        NOMBRES_LEGIBLES.get("TNA", "TNA"),
        NOMBRES_LEGIBLES.get("ONIv5", "ONIv5"),
    ]

    indices_seleccionados_str = st.sidebar.multiselect(
        "Selección de Índices / Oscilaciones:",
        options=list(NOMBRES_LEGIBLES.values()),
        default=[
            NOMBRES_LEGIBLES[k] for k in ["PDO", "TNA", "ONIv5"] if k in NOMBRES_LEGIBLES
        ],
        help="Seleccione una o más oscilaciones climáticas para el análisis multivariado.",
    )
    indices_codigos = [
        MAPA_ETIQUETA_A_CODIGO[item] for item in indices_seleccionados_str
    ]

    # Determinar fecha operacional específica para los índices seleccionados
    year_op_calc, mes_op_calc = determinar_ultimo_mes_disponible(
        oscilaciones_disponibles, indices=indices_codigos
    )

    # Parámetros según el modo
    st.sidebar.subheader("⚙️ Parámetros del Cálculo")

    now_sys = datetime.datetime.now()
    mes_sys_nombre = NOMBRES_MESES[now_sys.month - 1]

    if modo_analisis == "Operacional":
        year_objetivo = year_op_calc
        mes_objetivo = mes_op_calc
        longitud_ventana = LONGITUD_VENTANA_OPERACIONAL
        max_year_corte = None
        st.sidebar.markdown(f"**Año Objetivo:** `{year_objetivo}` *(Operacional)*")
        st.sidebar.markdown(
            f"**Mes Objetivo:** `{mes_objetivo} — {NOMBRES_MESES[mes_objetivo - 1]}` *(Último utilizable)*"
        )
        st.sidebar.markdown(f"**Ventana:** `12 meses` *(Operacional)*")
    else:
        year_objetivo = st.sidebar.number_input(
            "Año Objetivo ($Y_{\\text{obj}}$):",
            min_value=1950,
            max_value=now_sys.year,
            value=2015,
            step=1,
            help="Año histórico que se desea reanalizar.",
        )
        opciones_meses = [f"{i} — {NOMBRES_MESES[i-1]}" for i in range(1, 13)]
        mes_seleccionado_str = st.sidebar.selectbox(
            "Mes Objetivo (Cierre de Ventana):",
            options=opciones_meses,
            index=9,  # Octubre por defecto
            help="Mes en el cual culmina la ventana retrospectiva.",
        )
        mes_objetivo = int(mes_seleccionado_str.split(" — ")[0])

        tipo_ventana_str = st.sidebar.selectbox(
            "Longitud de la Ventana Temporal:",
            options=["12 meses (Operacional)", "6 meses (Metodológica Histórica)"],
            index=0,
            help="12 meses es el estándar operacional; 6 meses es el estándar de la metodología histórica de referencia.",
        )
        longitud_ventana = 12 if "12" in tipo_ventana_str else 6

        tipo_reanalisis = st.sidebar.radio(
            "Alcance del Reanálisis:",
            [
                "Retrospectivo Completo (Todos los años históricos)",
                "Backtesting / Simulación Tiempo Real (Corte en $Y_{\\text{obj}}$)",
            ],
            index=0,
            help="Retrospectivo Completo compara con todos los años del registro (incluso posteriores a Y_obj). Backtesting simula lo que se habría observado evaluando solo años <= Y_obj.",
        )
        max_year_corte = year_objetivo if "Backtesting" in tipo_reanalisis else None

    # Información contextual en el panel principal
    with col_info:
        if modo_analisis == "Operacional":
            desc_v_op = obtener_descripcion_ventana(
                year_op_calc, mes_op_calc, longitud_ventana=longitud_ventana
            )
            ventana_str_op = f"{desc_v_op[0]} – {desc_v_op[-1]}"
            st.info(
                f"📅 **Fecha del Sistema:** {mes_sys_nombre} de {now_sys.year}  \n"
                f"📌 **Último Período Evaluable:** **{NOMBRES_MESES[mes_op_calc - 1]} de {year_op_calc}**  \n"
                f"🗓️ **Ventana Operacional (12 meses):** **{ventana_str_op}**  \n"
                f"📋 **Regla Operacional:** Los índices del mes en curso se evalúan a partir del mes siguiente ($M+1$). El mes calendario en curso **NO** se evalúa."
            )
        else:
            if max_year_corte is not None:
                st.warning(
                    f"🕰️ **Modo Backtesting / Simulación Histórica Activo ($Y \\le {year_objetivo}$):** "
                    f"Evaluando año objetivo **{year_objetivo}** (Mes: **{NOMBRES_MESES[mes_objetivo - 1]}**, Ventana: **{longitud_ventana} meses**). "
                    f"Se excluyen estrictamente los registros posteriores a {year_objetivo} para simular las condiciones disponibles en tiempo real."
                )
            else:
                st.info(
                    f"🔬 **Modo Reanálisis Retrospectivo Completo Activo:** "
                    f"Evaluando año objetivo **{year_objetivo}** (Mes: **{NOMBRES_MESES[mes_objetivo - 1]}**, Ventana: **{longitud_ventana} meses**) "
                    f"frente a todo el registro histórico ($Y_{{\\text{{cand}}}} \\neq {year_objetivo}$). Permite identificar qué años de todo el registro se asemejan al caso de estudio."
                )

    boton_calcular = st.sidebar.button(
        "🚀 Calcular Años Análogos", type="primary", use_container_width=True
    )

    # Estado de ejecución
    if "resultado" not in st.session_state or boton_calcular:
        if indices_codigos:
            with st.spinner("Procesando análisis climatológico multivariado..."):
                st.session_state["resultado"] = calcular_analogos(
                    year_objetivo=year_objetivo,
                    mes_objetivo=mes_objetivo,
                    indices=indices_codigos,
                    longitud_ventana=longitud_ventana,
                    umbrales_personalizados=st.session_state["umbrales_usuario"],
                    max_year_corte=max_year_corte,
                    modo_analisis=modo_analisis,
                    oscilaciones_cargadas=oscilaciones_disponibles,
                )
        else:
            st.session_state["resultado"] = None

    resultado = st.session_state.get("resultado")

    # Presentación de Resultados
    if resultado is None:
        st.warning(
            "⚠️ Debe seleccionar al menos un índice climático para realizar el cálculo."
        )
    elif not resultado.es_valido:
        st.error(f"❌ **Validación de Datos No Superada:** {resultado.mensaje_error}")
        if resultado.indices_no_disponibles:
            st.markdown(
                f"**Índices no disponibles para este período:** `{', '.join(resultado.indices_no_disponibles)}`"
            )
    else:
        # Métricas principales (KPIs)
        st.subheader("📌 Resumen del Análisis Climatológico")
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Año Objetivo ($Y_{\text{obj}}$)", f"{resultado.year_objetivo}")
        kpi2.metric(
            "Mes de Cierre",
            f"{NOMBRES_MESES[resultado.mes_objetivo - 1]} ({resultado.mes_objetivo})",
        )
        kpi3.metric("Ventana de Evaluación", f"{resultado.longitud_ventana} meses")
        kpi4.metric("Índices Evaluados", f"{len(resultado.indices_evaluados)}")
        kpi5.metric("Años Candidatos Comunes", f"{len(resultado.anios_candidatos)}")

        # Descripción de la ventana temporal evaluada
        st.caption(
            f"**Secuencia de la Ventana Temporal:** {' → '.join(resultado.ventana_temporal)}"
        )

        # Pestañas de resultados
        tab_tabla, tab_graficos, tab_trazabilidad, tab_exportar = st.tabs(
            [
                "🏆 Ranking de Años Análogos",
                "📊 Visualización Gráfica",
                "🔍 Trazabilidad Estadística Completa",
                "💾 Exportación de Resultados",
            ]
        )

        with tab_tabla:
            st.markdown("### Tabla Consolidada de Coincidencias")
            st.markdown(
                r"Años históricos ordenados en forma descendente según el número total de índices que cumplen "
                r"simultáneamente las condiciones $(r_k > r_{\text{umbral}, k}) \land (\text{MAD}_k < \text{MAD}_{\text{umbral}, k})$. "
                r"El año objetivo está estrictamente excluido."
            )
            df_tabla = resultado.tabla_coincidencias.copy()
            # Indicador de Coincidencia (Coincide: Sí / No)
            df_tabla["Coincide"] = df_tabla["Total"].apply(lambda t: "Sí" if t > 0 else "No")
            # Resaltar filas con coincidencias
            st.dataframe(
                df_tabla.style.background_gradient(subset=["Total"], cmap="YlOrRd"),
                use_container_width=True,
                height=400,
            )

        with tab_graficos:
            st.markdown("### Histograma de Coincidencias por Año Candidato")
            fig, ax = plt.subplots(figsize=(14, 4.5))
            df_plot = resultado.tabla_coincidencias.head(30)
            if len(df_plot) > 0:
                ax.bar(
                    df_plot.index.astype(str),
                    df_plot["Total"],
                    color="#D9381E",
                    edgecolor="black",
                    alpha=0.85,
                )
                ax.set_title(
                    f"Años Análogos Principales (Año Objetivo: {resultado.year_objetivo}, Mes: {NOMBRES_MESES[resultado.mes_objetivo - 1]})",
                    fontsize=13,
                    pad=10,
                )
                ax.set_ylabel("Total de Índices Coincidentes", fontsize=11)
                ax.set_xlabel("Año Candidato Histórico", fontsize=11)
                ax.set_yticks(np.arange(0, len(resultado.indices_evaluados) + 2, 1))
                ax.grid(axis="y", linestyle="--", alpha=0.6)
                plt.xticks(rotation=60, ha="right")
                plt.tight_layout()
                st.pyplot(fig)
            plt.close(fig)

            # Gráfico de comparación temporal interactivo para candidatos seleccionados
            st.divider()
            st.markdown("### 📈 Comparación de Trayectorias Temporales (Objetivo vs Análogos)")

            anios_coincidentes = [y for y, score in resultado.ranking if score > 0]
            opciones_candidatos = [y for y, _ in resultado.ranking]

            # Selección por defecto: Top análogos (hasta 3 coincidentes)
            default_selection = anios_coincidentes[:3] if anios_coincidentes else opciones_candidatos[:1]

            col_sel1, col_sel2 = st.columns([3, 1])
            with col_sel1:
                anios_a_graficar = st.multiselect(
                    "Seleccione los años análogos a graficar:",
                    options=opciones_candidatos,
                    default=default_selection,
                    format_func=lambda y: f"Año {y} (Coincidencias: {resultado.tabla_coincidencias.loc[y, 'Total']})"
                    if y in resultado.tabla_coincidencias.index
                    else f"Año {y}",
                    help="Permite visualizar y comparar uno o varios años candidatos simultáneamente contra el año objetivo."
                )

            with col_sel2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Ver solo Top #1", help="Graficar únicamente el primer análogo"):
                    st.session_state["anios_graf_override"] = [opciones_candidatos[0]] if opciones_candidatos else []

            if not anios_a_graficar:
                st.info("ℹ️ Seleccione al menos un año candidato en el menú superior para visualizar las curvas temporales.")
            else:
                colores_candidatos = ["#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                estilos_linea = ["--", "-.", ":", "--", "-.", ":", "--", "-.", ":"]

                fig_comp, axes = plt.subplots(
                    len(resultado.indices_evaluados),
                    1,
                    figsize=(12, 3.5 * len(resultado.indices_evaluados)),
                    sharex=True,
                )
                if len(resultado.indices_evaluados) == 1:
                    axes = [axes]

                for ax_i, osc in zip(axes, resultado.indices_evaluados):
                    df_osc = oscilaciones_disponibles[osc]
                    v_obj = extraer_ventana(
                        df_osc,
                        resultado.year_objetivo,
                        resultado.mes_objetivo,
                        longitud_ventana=resultado.longitud_ventana,
                    )
                    x_labels = resultado.ventana_temporal
                    ax_i.plot(
                        x_labels,
                        v_obj,
                        marker="o",
                        linewidth=2.4,
                        color="#1f77b4",
                        label=f"Objetivo ({resultado.year_objetivo})",
                        zorder=5,
                    )

                    for idx_c, y_cand in enumerate(anios_a_graficar):
                        v_cand = extraer_ventana(
                            df_osc,
                            y_cand,
                            resultado.mes_objetivo,
                            longitud_ventana=resultado.longitud_ventana,
                        )
                        if v_cand is not None:
                            c_color = colores_candidatos[idx_c % len(colores_candidatos)]
                            c_style = estilos_linea[idx_c % len(estilos_linea)]
                            total_cand = (
                                resultado.tabla_coincidencias.loc[y_cand, "Total"]
                                if y_cand in resultado.tabla_coincidencias.index
                                else 0
                            )
                            ax_i.plot(
                                x_labels,
                                v_cand,
                                marker="s",
                                markersize=4,
                                linewidth=1.8,
                                linestyle=c_style,
                                color=c_color,
                                label=f"Análogo {y_cand} (Total: {total_cand})",
                            )

                    ax_i.set_title(
                        f"Índice: {osc} ({CATALOGO.get(osc, {}).get('name', osc)})",
                        fontsize=11,
                        fontweight="bold",
                    )
                    ax_i.set_ylabel(
                        f"Valor ({CATALOGO.get(osc, {}).get('units', 'u')})",
                        fontsize=10,
                    )
                    ax_i.grid(True, linestyle=":", alpha=0.6)
                    ax_i.legend(loc="best", framealpha=0.9, fontsize=9)

                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig_comp)
                plt.close(fig_comp)

        with tab_trazabilidad:
            st.markdown("### Trazabilidad Estadística Detallada por Índice y Candidato")
            st.markdown(
                "Muestra los valores calculados de correlación de Pearson ($r$), distancia absoluta media (MAD), "
                "umbrales aplicados y el resultado booleano de coincidencia para cada par índice-año."
            )
            df_traz = resultado.tabla_trazabilidad.copy()
            st.dataframe(
                df_traz.style.format(
                    {
                        "Pearson": "{:.4f}",
                        "MAD": "{:.4f}",
                        "Umbral_r": "{:.2f}",
                        "Umbral_MAD": "{:.2f}",
                    }
                ),
                use_container_width=True,
                height=450,
            )

        with tab_exportar:
            st.markdown("### Descarga de Reportes y Resultados")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv_tabla = resultado.tabla_coincidencias.to_csv(index=True)
                st.download_button(
                    "📥 Descargar Ranking de Años Análogos (CSV)",
                    data=csv_tabla,
                    file_name=f"ranking_analogos_{resultado.year_objetivo}_m{resultado.mes_objetivo}_{resultado.longitud_ventana}m.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_d2:
                csv_traz = resultado.tabla_trazabilidad.to_csv(index=False)
                st.download_button(
                    "📥 Descargar Trazabilidad Estadística Completa (CSV)",
                    data=csv_traz,
                    file_name=f"trazabilidad_analogos_{resultado.year_objetivo}_m{resultado.mes_objetivo}_{resultado.longitud_ventana}m.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

# ==============================================================================
# SECCIÓN 2: EXPLORADOR DE ÍNDICES CLIMÁTICOS
# ==============================================================================
elif seccion_seleccionada == "📊 Explorador de Índices":
    st.title("📊 Explorador y Catálogo de Índices Climáticos")
    st.markdown(
        "Consulte la ficha científica, metadatos, fuente operacional y la evolución histórica "
        "de cualquiera de las 19 oscilaciones climáticas integradas en el sistema."
    )
    st.divider()

    indice_sel = st.selectbox(
        "Seleccione un Índice Climático:",
        options=list(NOMBRES_LEGIBLES.keys()),
        format_func=lambda x: NOMBRES_LEGIBLES[x],
        index=0,
    )

    meta = CATALOGO.get(indice_sel, {})
    df_ind_check = oscilaciones_disponibles.get(indice_sel)
    if df_ind_check is not None and len(df_ind_check) > 0:
        y_min_total = int(df_ind_check["YEAR"].min())
        y_max_total = int(df_ind_check["YEAR"].max())
        periodo_str = f"{y_min_total}–{y_max_total} ({len(df_ind_check)} años)"
    else:
        y_min_total, y_max_total = 1950, datetime.datetime.now().year
        periodo_str = f"{meta.get('period_start', 1950)}–Presente"

    col_card1, col_card2 = st.columns([1, 1])

    with col_card1:
        st.subheader(f"📌 Ficha Técnica: {indice_sel}")
        st.markdown(f"**Nombre Completo:** {meta.get('name', indice_sel)}")
        st.markdown(f"**Acrónimo:** `{indice_sel}`")
        st.markdown(
            f"**Variable Física:** {meta.get('variable', 'No especificada')}"
        )
        st.markdown(
            f"**Tipo de Variable:** `{meta.get('variable_type', 'anomalía').capitalize()}`"
        )
        st.markdown(
            f"**Variable Utilizada en Motor:** **{meta.get('exact_variable_used', meta.get('variable'))}**"
        )
        st.markdown(
            f"**Columna / Campo Fuente:** `{meta.get('variable_column', 'Matriz Mensual')}`"
        )
        st.markdown(
            f"**Región de Referencia:** {meta.get('region', 'No especificada')}"
        )
        st.markdown(f"**Unidades de Medida:** `{meta.get('units', 'Adimensional')}`")
        st.markdown(f"**Período Disponible:** `{periodo_str}`")
        st.markdown(f"**Frecuencia:** {meta.get('update_frequency', 'Mensual')}")

    with col_card2:
        st.subheader("⚙️ Parámetros, Fuentes y Referencias")
        r_def, mad_def = UMBRALES_OSCILACIONES.get(indice_sel, (0.6, 0.6))
        st.markdown(
            f"**Umbral Metodológico Pearson ($r_{{\\text{{umbral}}}}$):** `{r_def:.2f}`"
        )
        st.markdown(
            f"**Umbral Metodológico MAD ($\\text{{MAD}}_{{\\text{{umbral}}}}$):** `{mad_def:.2f}`"
        )
        st.markdown(
            f"**Fuente Operacional:** {meta.get('institution', 'No especificada')}"
        )
        if meta.get("url"):
            st.markdown(
                f"**Enlace Oficial:** [{meta.get('url')}]({meta.get('url')})"
            )
        if meta.get("reference"):
            st.markdown(f"**Referencia Científica:** *{meta.get('reference')}*")
        if meta.get("doi"):
            st.markdown(
                f"**DOI:** [{meta.get('doi')}](https://doi.org/{meta.get('doi')})"
            )

    # Descripción climatológica detallada
    if meta.get("description"):
        st.info(
            f"**Descripción y Relevancia Climatológica:** {meta.get('description')}"
        )

    st.divider()

    # Visualización de la Serie Temporal y Datos Tabulares
    if (
        indice_sel in oscilaciones_disponibles
        and oscilaciones_disponibles[indice_sel] is not None
    ):
        df_ind = oscilaciones_disponibles[indice_sel].copy()

        st.subheader(f"📈 Evolución Temporal del Índice {indice_sel}")

        # Filtro de rango de años
        filtro_tiempo = st.radio(
            "Rango Temporal:",
            [
                "Todo el registro",
                "Últimos 10 años",
                "Últimos 5 años",
                "Rango personalizado",
            ],
            horizontal=True,
        )

        y_min_total = int(df_ind["YEAR"].min())
        y_max_total = int(df_ind["YEAR"].max())

        if filtro_tiempo == "Últimos 10 años":
            y_start = max(y_min_total, y_max_total - 10)
            y_end = y_max_total
        elif filtro_tiempo == "Últimos 5 años":
            y_start = max(y_min_total, y_max_total - 5)
            y_end = y_max_total
        elif filtro_tiempo == "Rango personalizado":
            y_start, y_end = st.slider(
                "Seleccione rango de años:",
                min_value=y_min_total,
                max_value=y_max_total,
                value=(max(y_min_total, y_max_total - 20), y_max_total),
            )
        else:
            y_start, y_end = y_min_total, y_max_total

        df_filtered = df_ind[(df_ind["YEAR"] >= y_start) & (df_ind["YEAR"] <= y_end)]

        # Convertir a serie lineal mensual para graficar
        fechas = []
        valores = []
        for _, row in df_filtered.iterrows():
            y_val = int(row["YEAR"])
            for m in range(1, 13):
                fechas.append(pd.Timestamp(year=y_val, month=m, day=1))
                valores.append(row.iloc[m])

        df_ts = pd.DataFrame({"Fecha": fechas, "Valor": valores}).dropna()

        fig_ts, ax_ts = plt.subplots(figsize=(14, 4.5))
        ax_ts.plot(df_ts["Fecha"], df_ts["Valor"], color="#1f77b4", linewidth=1.4)
        ax_ts.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
        ax_ts.set_title(
            f"Serie Mensual: {meta.get('name', indice_sel)} ({y_start}–{y_end})",
            fontsize=12,
        )
        ax_ts.set_ylabel(f"Valor ({meta.get('units', 'u')})", fontsize=10)
        ax_ts.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_ts)
        plt.close(fig_ts)

        st.divider()

        # Sección C: Tabla de Datos Históricos Interactiva
        st.subheader(f"📋 Tabla de Datos Históricos — {indice_sel}")
        st.info(
            f"📌 **Variable exacta utilizada en el cálculo de años análogos:** "
            f"**`{meta.get('exact_variable_used', meta.get('variable'))}`** "
            f"(Columna / Campo: `{meta.get('variable_column', 'Matriz Mensual')}`)."
        )

        col_tbl_ctrl1, col_tbl_ctrl2 = st.columns([3, 1])
        with col_tbl_ctrl1:
            st.caption(f"Mostrando {len(df_filtered)} registros anuales correspondientes al período {y_start}–{y_end}.")
        with col_tbl_ctrl2:
            csv_export = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"💾 Descargar CSV ({indice_sel})",
                data=csv_export,
                file_name=f"{indice_sel}_{y_start}_{y_end}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Si es un índice SSTA o Atlántico con archivo compuesto, permitir ver vista matricial o compuesta
        if indice_sel in ["SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34", "AtlTROP", "SAtl", "NAtl"]:
            tab_matriz, tab_compuesto = st.tabs(["Matriz Mensual (Utilizada por Motor)", "Fuente Compuesta Original (SST Absoluta vs Anomalía)"])
            with tab_matriz:
                st.dataframe(df_filtered.style.format(precision=2, na_rep="-"), use_container_width=True, height=350)
            with tab_compuesto:
                raw_filename = "dataSSTA.csv" if "SSTA" in indice_sel else "dataSSTOI.csv"
                raw_path = os.path.join(DATA_DIR, raw_filename)
                if os.path.exists(raw_path):
                    df_raw = pd.read_csv(raw_path)
                    df_raw_filtered = df_raw[(df_raw["YEAR"] >= y_start) & (df_raw["YEAR"] <= y_end)]
                    st.caption(f"Archivo fuente: `{raw_filename}` — Observe que el motor climatológico selecciona estrictamente la columna de anomalía `{meta.get('variable_column')}`.")
                    st.dataframe(df_raw_filtered, use_container_width=True, height=350)
                else:
                    st.warning(f"No se encontró el archivo compuesto {raw_filename} en el almacenamiento local.")
        else:
            st.dataframe(df_filtered.style.format(precision=2, na_rep="-"), use_container_width=True, height=350)

    else:
        st.error(
            f"No se encontraron datos locales cargados para el índice {indice_sel}."
        )

# ==============================================================================
# SECCIÓN 3: METODOLOGÍA DE CÁLCULO
# ==============================================================================
elif seccion_seleccionada == "📚 Metodología de Cálculo":
    st.title("📚 Metodología Científica de Selección de Años Análogos")
    st.markdown(
        "Explicación técnica y matemática de los fundamentos estadísticos, ventanas temporales, "
        "métricas de similitud y algoritmos de coincidencia multivariada implementados en **AAnalogos**."
    )
    st.divider()

    st.markdown("### 1. Concepto y Objetivo Climatológico")
    st.markdown(
        "El método de años análogos busca identificar aquellos años del registro histórico cuyas condiciones atmosféricas y "
        "oceánicas evolucionaron de manera más semejante a la configuración observada en el período reciente. Permite a los "
        "meteorólogos evaluar qué patrones de precipitación o temperatura se manifestaron en el pasado ante configuraciones "
        "sinópticas similares."
    )
    st.divider()

    st.markdown("### 2. Ventana Temporal Móvil (6 vs 12 Meses)")
    st.markdown(
        "* **Ventana Operacional (12 meses):** Configuración predeterminada en operación. Evalúa el ciclo anual completo previo al mes de pronóstico (ej. para octubre de 2026, abarca desde noviembre de 2025 hasta octubre de 2026).\n"
        "* **Ventana Metodológica Histórica (6 meses):** Configuración de referencia científica original.\n"
        "* **Manejo de Cruces Interanuales:** Cuando la ventana cruza el cambio de año (ej. mes < longitud de ventana), los meses previos se extraen de $Y-1$ y los meses restantes de $Y$. La etiqueta del candidato es siempre el año de cierre $Y$."
    )
    st.divider()

    st.markdown("### 3. Exclusión Estricta del Año Objetivo")
    st.markdown("El año objetivo **jamás** se evalúa como candidato de sí mismo:")
    st.latex(r"Y_{\text{cand}} \neq Y_{\text{obj}}")
    st.markdown(
        r"Incluirlo generaría una correlación trivial $r = 1.0000$ y $\text{MAD} = 0.0000$, distorsionando el ranking."
    )
    st.divider()

    st.markdown("### 4. Métricas Estadísticas de Similitud")
    st.markdown(r"Para cada índice $k$, se comparan el vector candidato $\mathbf{x}$ y el vector objetivo $\mathbf{y}$:")

    st.markdown("#### 4.1 Coeficiente de Correlación Lineal de Pearson ($r$)")
    st.markdown("Evalúa la **similitud en la sincronía, tendencia y forma** de la oscilación:")
    st.latex(r"r = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}")

    st.markdown("#### 4.2 Distancia Absoluta Media (MAD)")
    st.markdown("En esta formulación climatológica, MAD representa la **Diferencia Absoluta Media (Mean Absolute Difference)**, evaluando la **cercanía en la magnitud física y amplitud de la anomalía**:")
    st.latex(r"\text{MAD} = \frac{1}{N} \sum_{i=1}^{N} |x_i - y_i|")
    st.divider()

    st.markdown("### 5. Criterio de Coincidencia Univariada y Ranking")
    st.markdown(r"Un año histórico se declara análogo para el índice $k$ si y solo si:")
    st.latex(r"C_k(Y_{\text{cand}}) = \begin{cases} 1 & \text{si } (r_k > r_{\text{umbral}, k}) \land (\text{MAD}_k < \text{MAD}_{\text{umbral}, k}) \\ 0 & \text{en caso contrario} \end{cases}")

    st.markdown("El puntaje total de coincidencia multivariado es:")
    st.latex(r"\text{Total}(Y_{\text{cand}}) = \sum_{k=1}^{K} C_k(Y_{\text{cand}}) \quad \in \{0, 1, \dots, K\}")

    st.markdown("Los años análogos se ordenan de forma descendente por `Total`, desempatando por el año más reciente.")
    st.divider()

    st.markdown("### 6. Control Estricto de Datos y Reanálisis sin Contaminación")
    st.markdown(
        "* **Aislamiento de Sentinelas:** Valores como `-99.99`, `-999.0` se transforman en `NaN` y anulan la ventana si están presentes.\n"
        "* **Sin Reducción Silenciosa:** Si un índice seleccionado no dispone de datos completos, el cálculo se detiene e informa al usuario.\n"
        "* **Prevención de Look-Ahead Bias:** En modo reanálisis, ningún dato posterior al año objetivo se utiliza en la evaluación."
    )

# ==============================================================================
# SECCIÓN 4: ESTADO Y ACTUALIZACIÓN DE DATOS
# ==============================================================================
elif seccion_seleccionada == "📈 Estado de Datos":
    st.title("📈 Diagnóstico de Salud y Actualización de Datos")
    st.markdown(
        "Supervise el estado de cobertura, registros históricos y disponibilidad operacional "
        "de las 19 series climáticas, o ejecute una actualización atómica y no destructiva."
    )
    st.divider()

    df_salud = obtener_estado_fuentes(oscilaciones_disponibles, CATALOGO)
    disponibles = len(df_salud[df_salud["Estado"] == "Disponible"])
    total_indices = len(df_salud)

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Series Disponibles", f"{disponibles} / {total_indices}")

    anios_reg_validos = pd.to_numeric(df_salud["Años Registrados"], errors="coerce").dropna()
    mean_anios = f"{int(anios_reg_validos.mean())} años" if not anios_reg_validos.empty else "0 años"
    col_stat2.metric("Cobertura Temporal Promedio", mean_anios)

    ult_anios_validos = pd.to_numeric(df_salud["Último Año"], errors="coerce").dropna()
    max_ult_anio = f"{int(ult_anios_validos.max())}" if not ult_anios_validos.empty else "-"
    col_stat3.metric("Último Año con Registros", max_ult_anio)

    # Botón de Actualización
    st.subheader("🔄 Actualización Atómica de Series Climáticas")
    st.markdown(
        "Al presionar el botón, el sistema descargará las series más recientes desde las fuentes oficiales "
        "de NOAA/CPC/PSL/CSU, validando su estructura antes de reemplazar los archivos locales. "
        "Si una descarga falla, el dato válido existente se conserva intacto de manera segura y no destructiva."
    )

    if st.button(
        "↻ Actualizar índices",
        type="primary",
        help="Descargar y verificar las últimas series desde fuentes oficiales",
    ):
        prog_bar = st.progress(0.0)
        status_text = st.empty()
        status_text.info("Actualizando y verificando índices climáticos...")

        def update_progress(codigo, actual, total):
            prog_bar.progress(actual / total)
            status_text.text(f"Actualizando {codigo} ({actual}/{total})...")

        res_update = verificar_y_descargar_datos(
            DIRECTORIO_ACTUAL, force_update=True, progress_callback=update_progress
        )
        prog_bar.empty()
        status_text.empty()

        st.cache_resource.clear()
        oscilaciones_disponibles = obtener_datos_oscilaciones()
        df_salud = obtener_estado_fuentes(oscilaciones_disponibles, CATALOGO)

        todos_ok = all(
            v["status"] in ["OK", "Sin cambios"] for v in res_update.values()
        )
        if todos_ok:
            st.success("✓ Índices actualizados correctamente.")
        else:
            st.warning(
                "⚠ Algunos índices no pudieron actualizarse (se conservaron las copias locales previas)."
            )

        # Resumen de actualización
        res_rows = []
        for k, v in res_update.items():
            res_rows.append(
                {"Índice": k, "Estado": v["status"], "Detalle": v["mensaje"]}
            )
        st.dataframe(pd.DataFrame(res_rows), use_container_width=True)

    st.subheader("📋 Inventario Detallado de Fuentes y Variables")
    cols_salud_show = [
        "Código",
        "Nombre",
        "Estado",
        "Primer Año",
        "Último Año",
        "Último Mes",
        "Años Registrados",
        "Tipo de Variable",
        "Variable en Motor",
        "Institución",
    ]
    st.dataframe(
        df_salud[[c for c in cols_salud_show if c in df_salud.columns]],
        use_container_width=True,
        height=450,
    )

# ==============================================================================
# SECCIÓN 5: CONFIGURACIÓN DE UMBRALES
# ==============================================================================
elif seccion_seleccionada == "⚙️ Configuración de Umbrales":
    st.title("⚙️ Configuración y Calibración de Umbrales Univariados")
    st.markdown(
        "Personalice los umbrales de correlación de Pearson ($r_{\text{umbral}}$) y distancia absoluta media "
        "($\text{MAD}_{\text{umbral}}$) para cada uno de los 19 índices. Los valores metodológicos oficiales "
        "se cargan como valores predeterminados y pueden ser restaurados en cualquier momento."
    )
    st.divider()

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn2:
        if st.button(
            "🔄 Restaurar Valores Metodológicos Predeterminados",
            use_container_width=True,
        ):
            st.session_state["umbrales_usuario"] = obtener_umbrales_metodologicos()
            st.success("Umbrales restaurados a los valores metodológicos oficiales.")

    st.subheader("🔧 Ajuste Individual por Índice Climático")
    cols_th = st.columns(3)

    indices_lista = list(UMBRALES_OSCILACIONES.keys())
    nuevos_umbrales = {}

    for i, cod in enumerate(indices_lista):
        with cols_th[i % 3]:
            st.markdown(f"**{cod}** — *{CATALOGO.get(cod, {}).get('name', cod)[:30]}*")
            r_metod, mad_metod = UMBRALES_OSCILACIONES[cod]
            r_curr, mad_curr = st.session_state["umbrales_usuario"].get(
                cod, (r_metod, mad_metod)
            )

            col_r, col_mad = st.columns(2)
            with col_r:
                r_val = st.number_input(
                    f"r ({cod})",
                    min_value=-1.0,
                    max_value=1.0,
                    value=float(r_curr),
                    step=0.05,
                    key=f"r_{cod}",
                    help=f"Predeterminado: {r_metod}",
                )
            with col_mad:
                mad_val = st.number_input(
                    f"MAD ({cod})",
                    min_value=0.0,
                    max_value=5.0,
                    value=float(mad_curr),
                    step=0.05,
                    key=f"mad_{cod}",
                    help=f"Predeterminado: {mad_metod}",
                )

            # Indicador de estado modificado vs default
            es_default = (abs(r_val - r_metod) < 1e-4) and (
                abs(mad_val - mad_metod) < 1e-4
            )
            if not es_default:
                st.caption("🟠 *Modificado por usuario*")
            else:
                st.caption("🟢 *Valor oficial*")

            nuevos_umbrales[cod] = (r_val, mad_val)

    st.session_state["umbrales_usuario"] = nuevos_umbrales
