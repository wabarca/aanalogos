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
    cargar_configuracion_institucional,
    generar_grafico_individual_indice,
    obtener_documentos_disponibles,
    transformar_enlaces_markdown,
    buscar_etiqueta_documento,
    UMBRALES_OSCILACIONES,
    NOMBRES_MESES,
    LONGITUD_VENTANA_METODOLOGICA,
    LONGITUD_VENTANA_OPERACIONAL,
)

# Cargar configuración institucional para personalización de despliegue
CONFIG_INSTITUCION = cargar_configuracion_institucional()

# Configuración de página de Streamlit
st.set_page_config(
    page_title=f"Años Análogos Climáticos | {CONFIG_INSTITUCION['name']}",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo CSS Institucional — Paleta Pear & Bosque (MARN El Salvador)
st.markdown(
    """
    <style>
    /* Tipografía y jerarquía visual institucional */
    h1, h2, h3 {
        color: #2E5D34 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
    }
    
    /* Botones primarios en verde bosque con acento pear */
    div.stButton > button[kind="primary"], div.stButton > button:first-child {
        background-color: #2E5D34;
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #2E5D34;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #5C8A3D;
        border-color: #D1E231;
        color: #ffffff;
        box-shadow: 0 0 8px rgba(209, 226, 49, 0.4);
    }

    /* Pestañas (tabs) activas con acento Pear */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2E5D34 !important;
        border-bottom-color: #D1E231 !important;
        border-bottom-width: 3px !important;
        font-weight: 700;
    }

    /* Tarjetas de métricas con fondo crema claro y borde salvia */
    div[data-testid="metric-container"] {
        background-color: #F4F6E8;
        border: 1px solid #A8C686;
        border-left: 4px solid #D1E231;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(38, 50, 56, 0.05);
    }
    div[data-testid="metric-container"] label {
        color: #2E5D34 !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #263238 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
if CONFIG_INSTITUCION.get("logo"):
    st.sidebar.image(CONFIG_INSTITUCION["logo"], width=180)

st.sidebar.title("🌦️ AAnalogos")
st.sidebar.caption(f"**{CONFIG_INSTITUCION['name']}**  \n*{CONFIG_INSTITUCION['division']}*")

# Si el usuario hace clic en un enlace de documentación, navegar automáticamente a la sección 6
seccion_inicial_idx = 5 if st.query_params.get("doc") else 2

seccion_seleccionada = st.sidebar.radio(
    "Navegación del Sistema:",
    [
        "1. Estado de datos disponibles",
        "2. Configuración de umbrales",
        "3. Análisis de años análogos",
        "4. Explorador de índices",
        "5. Metodología",
        "Documentación y créditos",
    ],
    index=seccion_inicial_idx,
)

# Si el usuario navega fuera de la documentación, limpiar el parámetro 'doc' de la URL
if seccion_seleccionada != "Documentación y créditos" and "doc" in st.query_params:
    del st.query_params["doc"]

st.sidebar.divider()

# ==============================================================================
# ENCABEZADO INSTITUCIONAL PERSISTENTE
# ==============================================================================
if CONFIG_INSTITUCION.get("logo"):
    col_head_txt, col_head_logo = st.columns([4, 1])
    with col_head_txt:
        st.title("🌦️ Sistema de Selección de Años Análogos Climáticos")
        st.markdown(
            f"**{CONFIG_INSTITUCION['division']}**  \n*{CONFIG_INSTITUCION['name']}*"
        )
    with col_head_logo:
        st.image(CONFIG_INSTITUCION["logo"], width=140)
else:
    st.title("🌦️ Sistema de Selección de Años Análogos Climáticos")
    st.markdown(
        f"**{CONFIG_INSTITUCION['division']}**  \n*{CONFIG_INSTITUCION['name']}*"
    )

st.divider()

# ==============================================================================
# SECCIÓN 3: ANÁLISIS DE AÑOS ANÁLOGOS
# ==============================================================================
if seccion_seleccionada == "3. Análisis de años análogos":
    st.header("3. Análisis de años análogos")
    st.divider()

    # Selección de Modo de Análisis y Ventana
    col_mode, col_vent = st.columns([1, 1])
    with col_mode:
        modo_analisis = st.radio(
            "**Modo de Análisis:**",
            ["Operacional", "Reanálisis Histórico"],
            index=0,
            horizontal=True,
            help="El modo operacional utiliza automáticamente el año actual, el último mes publicado y la ventana seleccionada.",
        )
    with col_vent:
        sel_ventana_str = st.selectbox(
            "Ventana de análisis:",
            options=["12 meses", "6 meses"],
            index=0,
            key="selector_ventana_analisis",
            help="12 meses es la opción predeterminada actual; 6 meses permite evaluar con la ventana de la metodología original.",
        )
        longitud_ventana = 12 if "12" in sel_ventana_str else 6

    # Preselección de índices en Sidebar por defecto: RONI, TNA y ONIv6
    default_indices = [
        NOMBRES_LEGIBLES.get("RONI", "RONI"),
        NOMBRES_LEGIBLES.get("TNA", "TNA"),
        NOMBRES_LEGIBLES.get("ONIv6", "ONIv6"),
    ]

    indices_seleccionados_str = st.sidebar.multiselect(
        "Selección de Índices / Oscilaciones:",
        options=list(NOMBRES_LEGIBLES.values()),
        default=[
            NOMBRES_LEGIBLES[k] for k in ["RONI", "TNA", "ONIv6"] if k in NOMBRES_LEGIBLES
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

    # Parámetros según el modo en Sidebar
    st.sidebar.subheader("⚙️ Parámetros del Cálculo")

    now_sys = datetime.datetime.now()
    mes_sys_nombre = NOMBRES_MESES[now_sys.month - 1]

    if modo_analisis == "Operacional":
        year_objetivo = year_op_calc
        mes_objetivo = mes_op_calc
        max_year_corte = None
        st.sidebar.markdown(f"**Año Objetivo:** `{year_objetivo}` *(Operacional)*")
        st.sidebar.markdown(
            f"**Mes Objetivo:** `{mes_objetivo} — {NOMBRES_MESES[mes_objetivo - 1]}` *(Último utilizable)*"
        )
        st.sidebar.markdown(f"**Ventana:** `{longitud_ventana} meses` *(Operacional)*")
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
        st.sidebar.markdown(f"**Ventana:** `{longitud_ventana} meses`")

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
    if modo_analisis == "Operacional":
        desc_v_op = obtener_descripcion_ventana(
            year_op_calc, mes_op_calc, longitud_ventana=longitud_ventana
        )
        ventana_str_op = f"{desc_v_op[0]} – {desc_v_op[-1]}"
        st.info(
            f"📅 **Fecha del Sistema:** {mes_sys_nombre} de {now_sys.year}  \n"
            f"📌 **Último Período Evaluable:** **{NOMBRES_MESES[mes_op_calc - 1]} de {year_op_calc}**  \n"
            f"🗓️ **Ventana Operacional ({longitud_ventana} meses):** **{ventana_str_op}**  \n"
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
        "🚀 Calcular Años Análogos", type="primary", width="stretch"
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
            # Resaltar filas con coincidencias mediante degradado verde institucional
            st.dataframe(
                df_tabla.style.background_gradient(subset=["Total"], cmap="YlGn"),
                width="stretch",
                height=400,
            )

            # ==================================================================
            # REPRESENTACIÓN GRÁFICA INDIVIDUAL POR ÍNDICE
            # ==================================================================
            st.divider()
            st.subheader("Representación gráfica por índice")
            st.markdown(
                "Visualice simultáneamente el coeficiente de correlación de Pearson ($r$), la distancia absoluta "
                "media ($\text{MAD}$), los umbrales configurados y los años candidatos evaluados para cada índice."
            )

            indices_analisis = resultado.indices_evaluados
            if not indices_analisis:
                st.info("No hay índices evaluados disponibles en el análisis actual.")
            else:
                col_sel_idx, col_espacio = st.columns([2, 2])
                with col_sel_idx:
                    idx_seleccionado = st.selectbox(
                        "Índice:",
                        options=indices_analisis,
                        format_func=lambda x: f"{x} — {NOMBRES_LEGIBLES.get(x, x)}",
                        key="selector_grafico_individual_indice"
                    )

                df_traz_indice = (
                    resultado.tabla_trazabilidad[resultado.tabla_trazabilidad["Indice"] == idx_seleccionado]
                    if resultado.tabla_trazabilidad is not None and not resultado.tabla_trazabilidad.empty
                    else pd.DataFrame()
                )

                if df_traz_indice.empty or df_traz_indice.dropna(subset=["Pearson", "MAD"]).empty:
                    st.warning(
                        f"⚠️ No existen datos suficientes de correlación y MAD para el índice {idx_seleccionado} en el período seleccionado."
                    )
                else:
                    # Generar figura científica fiel a la referencia
                    fig_ind = generar_grafico_individual_indice(
                        resultado=resultado,
                        codigo_indice=idx_seleccionado,
                        catalogo=CATALOGO
                    )
                    st.pyplot(fig_ind, clear_figure=True)

                    # Exportar imagen en memoria para botón de descarga opcional
                    import io
                    buf_img = io.BytesIO()
                    fig_ind.savefig(buf_img, format="png", dpi=150, facecolor=fig_ind.get_facecolor(), edgecolor="none")
                    buf_img.seek(0)
                    plt.close(fig_ind)

                    # Paneles de parámetros y resumen debajo del gráfico
                    col_p1, col_p2 = st.columns(2)
                    r_th_actual = float(df_traz_indice["Umbral_r"].iloc[0])
                    mad_th_actual = float(df_traz_indice["Umbral_MAD"].iloc[0])
                    anios_analogos_idx = df_traz_indice[df_traz_indice["Coincidencia"] == 1]["YEAR"].tolist()
                    total_anios_eval = len(df_traz_indice["YEAR"].unique())

                    with col_p1:
                        st.info(
                            f"**Parámetros de umbral**  \n"
                            f"• Umbral de correlación (r) mínimo: **{r_th_actual:.2f}**  \n"
                            f"• Umbral de MAD máximo: **{mad_th_actual:.2f}**"
                        )
                    with col_p2:
                        st.success(
                            f"**Resumen**  \n"
                            f"• Total de años evaluados: **{total_anios_eval}**  \n"
                            f"• Años análogos encontrados: **{len(anios_analogos_idx)}**"
                        )

                    # Lista de años análogos
                    if anios_analogos_idx:
                        str_anios = ", ".join(str(y) for y in sorted(anios_analogos_idx))
                        st.markdown(f"**Años análogos para el índice seleccionado:** {str_anios}")
                    else:
                        st.markdown(f"**Años análogos para el índice seleccionado:** Ninguno (Años análogos encontrados: 0)")

                    # Botón de descarga de la figura
                    st.download_button(
                        label=f"📥 Descargar Gráfico {idx_seleccionado} (PNG)",
                        data=buf_img,
                        file_name=f"grafico_{idx_seleccionado}_{resultado.year_objetivo}_m{resultado.mes_objetivo}.png",
                        mime="image/png"
                    )

        with tab_graficos:
            st.markdown("### Histograma de Coincidencias por Año Candidato")
            fig, ax = plt.subplots(figsize=(14, 4.5))
            df_plot = resultado.tabla_coincidencias.head(30)
            if len(df_plot) > 0:
                ax.bar(
                    df_plot.index.astype(str),
                    df_plot["Total"],
                    color="#2E5D34",
                    edgecolor="#5C8A3D",
                    linewidth=0.8,
                    alpha=0.9,
                )
                ax.set_title(
                    f"Años Análogos Principales (Año Objetivo: {resultado.year_objetivo}, Mes: {NOMBRES_MESES[resultado.mes_objetivo - 1]})",
                    fontsize=13,
                    pad=10,
                    color="#2E5D34",
                    fontweight="bold",
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
                # Paleta de candidatos (tonos contrastantes sin azul para preservar azul exclusivamente al año objetivo)
                colores_candidatos = [
                    "#2E5D34",  # Verde bosque
                    "#D9A441",  # Ámbar dorado
                    "#D32F2F",  # Rojo institucional
                    "#8E24AA",  # Púrpura
                    "#00897B",  # Verde azulado / Teal
                    "#E65100",  # Naranja
                    "#5D4037",  # Marrón cálido
                    "#455A64",  # Gris pizarra
                ]
                estilos_linea = ["--", "-.", ":", "--", "-.", ":", "--", "-."]

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
                    # Año Objetivo destacado en tono azul
                    ax_i.plot(
                        x_labels,
                        v_obj,
                        marker="o",
                        linewidth=2.8,
                        color="#1565C0",
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
                        color="#2E5D34",
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
                width="stretch",
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
                    width="stretch",
                )
            with col_d2:
                csv_traz = resultado.tabla_trazabilidad.to_csv(index=False)
                st.download_button(
                    "📥 Descargar Trazabilidad Estadística Completa (CSV)",
                    data=csv_traz,
                    file_name=f"trazabilidad_analogos_{resultado.year_objetivo}_m{resultado.mes_objetivo}_{resultado.longitud_ventana}m.csv",
                    mime="text/csv",
                    width="stretch",
                )

# ==============================================================================
# SECCIÓN 4: EXPLORADOR DE ÍNDICES
# ==============================================================================
elif seccion_seleccionada == "4. Explorador de índices":
    st.header("4. Explorador de índices")
    st.markdown(
        "Consulte la ficha científica, metadatos, fuente operacional y la evolución histórica "
        "de cualquiera de las 21 oscilaciones climáticas integradas en el sistema."
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
        ax_ts.plot(df_ts["Fecha"], df_ts["Valor"], color="#2E5D34", linewidth=1.5)
        ax_ts.fill_between(df_ts["Fecha"], df_ts["Valor"], 0, where=(df_ts["Valor"] >= 0), color="#A8C686", alpha=0.4, label="Anomalía positiva / Fase activa")
        ax_ts.fill_between(df_ts["Fecha"], df_ts["Valor"], 0, where=(df_ts["Valor"] < 0), color="#CFD8DC", alpha=0.4, label="Anomalía negativa / Fase inactiva")
        ax_ts.axhline(0, color="#263238", linestyle="--", linewidth=0.8, alpha=0.8)
        ax_ts.set_title(
            f"Serie Mensual: {meta.get('name', indice_sel)} ({y_start}–{y_end})",
            fontsize=12,
            fontweight="bold",
            color="#2E5D34",
        )
        ax_ts.set_ylabel(f"Valor ({meta.get('units', 'u')})", fontsize=10)
        ax_ts.grid(True, linestyle=":", alpha=0.6)
        ax_ts.legend(loc="upper left", framealpha=0.9, fontsize=9)
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
                width="stretch",
            )

        # Si es un índice SSTA o Atlántico con archivo compuesto, permitir ver vista matricial o compuesta
        if indice_sel in ["SSTA_12", "SSTA_3", "SSTA_4", "SSTA_34", "AtlTROP", "SAtl", "NAtl"]:
            tab_matriz, tab_compuesto = st.tabs(["Matriz Mensual (Utilizada por Motor)", "Fuente Compuesta Original (SST Absoluta vs Anomalía)"])
            with tab_matriz:
                st.dataframe(df_filtered.style.format(precision=2, na_rep="NaN"), width="stretch", height=350)
            with tab_compuesto:
                raw_filename = "dataSSTA.csv" if "SSTA" in indice_sel else "dataSSTOI.csv"
                raw_path = os.path.join(DATA_DIR, raw_filename)
                if os.path.exists(raw_path):
                    df_raw = pd.read_csv(raw_path)
                    df_raw_filtered = df_raw[(df_raw["YEAR"] >= y_start) & (df_raw["YEAR"] <= y_end)]
                    st.caption(f"Archivo fuente: `{raw_filename}` — Observe que el motor climatológico selecciona estrictamente la columna de anomalía `{meta.get('variable_column')}`.")
                    st.dataframe(df_raw_filtered, width="stretch", height=350)
                else:
                    st.warning(f"No se encontró el archivo compuesto {raw_filename} en el almacenamiento local.")
        else:
            st.dataframe(df_filtered.style.format(precision=2, na_rep="NaN"), width="stretch", height=350)

    else:
        st.error(
            f"No se encontraron datos locales cargados para el índice {indice_sel}."
        )

# ==============================================================================
# SECCIÓN 5: METODOLOGÍA
# ==============================================================================
elif seccion_seleccionada == "5. Metodología":
    st.header("5. Metodología")
    st.markdown(
        "Fundamentos físicos, formulación matemática y aplicación práctica del método de "
        "selección de años análogos climáticos implementado en **AAnalogos**."
    )
    st.divider()

    # 5.1 ¿Qué es un año análogo?
    st.subheader("5.1 ¿Qué es un año análogo?")
    st.markdown(
        "El método de **años análogos** es una técnica empírica de diagnóstico y pronóstico climático basada en el "
        "principio físico de que estados oceánicos y atmosféricos similares en el pasado tienden a evolucionar de forma semejante "
        "y generar patrones de precipitación y temperatura comparables a escala regional.\n\n"
        "Al identificar qué años históricos presentaron la trayectoria más parecida en las principales oscilaciones climáticas "
        "(ENOS, Atlántico, Pacífico Norte, Ártico y circulación global), los meteorólogos y climatólogos obtienen escenarios "
        "de referencia objetivos para orientar la perspectiva climática estacional."
    )
    st.divider()

    # 5.2 Flujo del método
    st.subheader("5.2 Flujo del método")
    st.markdown(
        "El procedimiento científico de selección sigue una secuencia lógica estricta y reproducible:\n\n"
        "1. **Definición de la Ventana Temporal:** Se extrae una ventana móvil retrospectiva ($N = 12$ meses en operación estándar, "
        "o $N = 6$ meses en la metodología histórica) que culmina en el mes objetivo ($m_{\\text{obj}}$) del año objetivo ($Y_{\\text{obj}}$).\n"
        "2. **Exclusión Estricta del Año Objetivo:** El año objetivo **nunca** se evalúa como candidato ($Y_{\\text{cand}} \\neq Y_{\\text{obj}}$) "
        "para evitar correlaciones triviales espurias ($r=1.0$, $\\text{MAD}=0.0$).\n"
        "3. **Comparación Univariada:** Para cada índice climático $k$, se calculan el coeficiente de correlación de Pearson ($r$) "
        "y la distancia absoluta media (MAD) entre la serie del año objetivo y cada año candidato del registro histórico.\n"
        "4. **Aplicación Conjunta de Umbrales:** Se evalúa si el año candidato cumple simultáneamente ambos criterios ($r > r_{\\text{umbral}} \\land \\text{MAD} < \\text{MAD}_{\\text{umbral}}$).\n"
        "5. **Consolidación y Ranking Multivariado:** Se suman las coincidencias obtenidas en todos los índices analizados para jerarquizar los años análogos."
    )
    st.divider()

    # 5.3 Pearson (r)
    st.subheader("5.3 Coeficiente de Correlación de Pearson ($r$)")
    st.markdown(
        "El coeficiente de correlación lineal de Pearson evalúa la **similitud en la sincronía, tendencia y forma** "
        "de la oscilación climática a lo largo de la ventana de análisis:"
    )
    st.latex(
        r"r = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}"
    )
    st.markdown(
        "* **Pregunta que responde:** *¿Las anomalías climáticas evolucionaron con la misma trayectoria temporal?*\n"
        "* **Rango:** $r \\in [-1, 1]$. Valores cercanos a $+1$ reflejan trayectorias paralelas; valores próximos a $0$ denotan ausencia de relación lineal; y valores negativos indican tendencias opuestas.\n"
        "* **Criterio de aceptación:** $r > r_{\\text{umbral}, k}$ (por encima del umbral mínimo de correlación)."
    )
    st.divider()

    # 5.4 MAD
    st.subheader("5.4 Distancia Absoluta Media (MAD)")
    st.markdown(
        "En la formulación climatológica del sistema, MAD representa la **Diferencia Absoluta Media (Mean Absolute Difference)**, "
        "evaluando la **cercanía en la magnitud física y amplitud térmica/barométrica** de la anomalía:"
    )
    st.latex(
        r"\text{MAD} = \frac{1}{N} \sum_{i=1}^{N} |x_i - y_i|"
    )
    st.markdown(
        "* **Pregunta que responde:** *¿Los valores observados estuvieron suficientemente próximos en magnitud real?*\n"
        "* **Rango:** $\\text{MAD} \\ge 0$. Preserva las unidades físicas del índice ($^\\circ\\text{C}$, desv. est., $10^6\\text{ km}^2$). Valores menores indican mayor cercanía física.\n"
        "* **Criterio de aceptación:** $\\text{MAD} < \\text{MAD}_{\\text{umbral}, k}$ (por debajo del umbral máximo de diferencia)."
    )
    st.divider()

    # 5.5 Criterio conjunto de selección
    st.subheader("5.5 Criterio conjunto de selección")
    st.markdown(
        "Un año candidato $Y_{\\text{cand}}$ se declara **año análogo** para el índice $k$ si y solo si satisface **ambos criterios de forma simultánea**:"
    )
    st.latex(
        r"C_k(Y_{\text{cand}}) = \begin{cases} 1 & \text{si } (r_k > r_{\text{umbral}, k}) \;\land\; (\text{MAD}_k < \text{MAD}_{\text{umbral}, k}) \\ 0 & \text{en caso contrario} \end{cases}"
    )
    st.info(
        "💡 **¿Por qué son indispensables ambos criterios?**  \n"
        "• **Pearson sin MAD** aceptaría años con la misma forma de curva temporal pero con anomalías térmicas desfasadas por varios grados (ej. una fase cálida extrema frente a una fase neutra leve).  \n"
        "• **MAD sin Pearson** aceptaría años con anomalías numéricamente cercanas a cero pero con tendencias físicas opuestas (ej. un calentamiento rápido frente a un enfriamiento rápido).  \n"
        "• **La combinación conjunta ($r \\land \\text{MAD}$)** asegura que el análogo coincida tanto en la dirección temporal de la oscilación como en su intensidad física."
    )
    st.divider()

    # 5.6 Ejemplo práctico y reproducible
    st.subheader("5.6 Ejemplo práctico y reproducible (Caso Benchmark AMO 2015)")
    st.markdown(
        "A continuación se presenta un caso real con los datos históricos oficiales y los cálculos exactos "
        "generados por el motor de **AAnalogos** para el caso de referencia validado:"
    )

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown(
            "* **Índice evaluado:** `AMO` (Oscilación Multidecadal del Atlántico)\n"
            "* **Año Objetivo ($Y_{\\text{obj}}$):** `2015`\n"
            "* **Mes Objetivo ($m_{\\text{obj}}$):** `10` (Octubre)\n"
            "* **Ventana de análisis:** `6 meses` (Mayo a Octubre 2015)"
        )
    with col_e2:
        r_amo_th, mad_amo_th = UMBRALES_OSCILACIONES.get("AMO", (0.60, 0.15))
        st.markdown(
            f"* **Umbral de correlación ($r_{{\\text{{umbral}}}}$):** `>{r_amo_th:.2f}`\n"
            f"* **Umbral de proximidad ($\\text{{MAD}}_{{\\text{{umbral}}}}$):** `<{mad_amo_th:.2f} °C`\n"
            "* **Total de años candidatos evaluados:** `74 años` (1948–2022, excluyendo 2015)"
        )

    st.markdown("#### Datos de la Ventana: Año Objetivo 2015 vs Año Candidato 2013")

    serie_amo_ej = oscilaciones_disponibles.get("AMO")
    if serie_amo_ej is not None and not serie_amo_ej.empty:
        v_2015 = np.array(extraer_ventana(serie_amo_ej, 2015, 10, 6), dtype=float)
        v_2013 = np.array(extraer_ventana(serie_amo_ej, 2013, 10, 6), dtype=float)
        meses_nombres = ["Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre"]

        # Medias y desviaciones
        y_bar = np.mean(v_2015)
        x_bar = np.mean(v_2013)
        dy = v_2015 - y_bar
        dx = v_2013 - x_bar
        prod_d = dx * dy
        abs_d = np.abs(v_2013 - v_2015)

        # Construcción de la tabla Markdown con encabezados matemáticos KaTeX renderizados
        md_tabla_calc = [
            "| Mes | $y_i$ (2015 Objetivo) | $x_i$ (2013 Candidato) | $y_i - \\bar{y}$ | $x_i - \\bar{x}$ | $(x_i - \\bar{x})(y_i - \\bar{y})$ | $\\lvert x_i - y_i \\rvert$ |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]
        for i in range(len(meses_nombres)):
            md_tabla_calc.append(
                f"| **{meses_nombres[i]}** | {v_2015[i]:+.3f} °C | {v_2013[i]:+.3f} °C | {dy[i]:+.3f} | {dx[i]:+.3f} | {prod_d[i]:+.4f} | {abs_d[i]:.3f} °C |"
            )
        st.markdown("\n".join(md_tabla_calc))

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### Cálculo de Pearson ($r$)")
            st.markdown(
                f"* Media Objetivo: $\\bar{{y}} = {y_bar:.4f}\\ ^\\circ\\text{{C}}$\n"
                f"* Media Candidato: $\\bar{{x}} = {x_bar:.4f}\\ ^\\circ\\text{{C}}$\n"
                f"* Numerador (Covarianza): $\\sum (x_i-\\bar{{x}})(y_i-\\bar{{y}}) = {np.sum(prod_d):.4f}$\n"
                f"* Denominador: $\\sqrt{{\\sum(x_i-\\bar{{x}})^2 \\sum(y_i-\\bar{{y}})^2}} = {np.sqrt(np.sum(dx**2)*np.sum(dy**2)):.4f}$\n"
                f"* **Resultado:** **$r = 0.9583$** $\\implies$ **$0.9583 > 0.60$ (Cumple ✓)**"
            )
        with col_p2:
            st.markdown("#### Cálculo de MAD")
            st.markdown(
                f"* Suma de diferencias absolutas: $\\sum |x_i - y_i| = {np.sum(abs_d):.4f}\\ ^\\circ\\text{{C}}$\n"
                f"* Longitud de ventana: $N = 6$\n"
                f"* $\\text{{MAD}} = \\frac{1}{6} \\times {np.sum(abs_d):.4f} = {np.mean(abs_d):.4f}\\ ^\\circ\\text{{C}}$\n\n"
                f"* **Resultado:** **$\\text{{MAD}} = 0.0365\\ ^\\circ\\text{{C}}$** $\\implies$ **$0.0365 < 0.15$ (Cumple ✓)**"
            )

        st.markdown("#### Contraste de Casos Reales y Aplicación de Umbrales")
        st.markdown(
            "La siguiente tabla demuestra la necesidad de aplicar ambos criterios contrastando cuatro años reales "
            "del registro histórico de AMO frente a 2015:"
        )

        md_tabla_contraste = [
            "| Año Candidato | Pearson ($r$) | Umbral $r$ | MAD | Umbral MAD | Condición $(r > 0.60) \\land (\\text{MAD} < 0.15)$ | Dictamen | Explicación Física |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
            "| **2013** | **0.9583** | $> 0.60$ (✓) | **0.0365 °C** | $< 0.15$ °C (✓) | Cumple ambos | 🟢 **Año Análogo** | Sincronía temporal casi perfecta y anomalías térmicas prácticamente idénticas. |",
            "| **1972** | **0.9805** | $> 0.60$ (✓) | **0.5430 °C** | $< 0.15$ °C (✗) | Falla MAD | 🔴 **No Análogo** | Excelente correlación mensual, pero anomalía térmica desfasada en más de 0.5 °C. |",
            "| **1958** | **-0.4390** | $> 0.60$ (✗) | **0.1098 °C** | $< 0.15$ °C (✓) | Falla Pearson | 🔴 **No Análogo** | Valores térmicos numéricamente cercanos, pero con tendencia y evolución temporal invertida. |",
            "| **1953** | **-0.6729** | $> 0.60$ (✗) | **0.1768 °C** | $< 0.15$ °C (✗) | Falla ambos | 🔴 **No Análogo** | Tendencia opuesta y discrepancia en amplitud térmica. |",
        ]
        st.markdown("\n".join(md_tabla_contraste))

    st.divider()

    # 5.7 Gráfica del ejemplo e interpretación
    st.subheader("5.7 Representación Gráfica del Ejemplo e Interpretación")
    st.markdown(
        "Visualización simultánea de Pearson ($r$, azul), MAD (rojo) y umbrales operacionales para los 74 años "
        "candidatos de AMO generada por el motor de cálculo:"
    )

    res_ejemplo = calcular_analogos(
        year_objetivo=2015,
        mes_objetivo=10,
        indices=["AMO"],
        longitud_ventana=6,
        oscilaciones_cargadas=oscilaciones_disponibles,
    )
    if res_ejemplo.es_valido:
        fig_ejemplo = generar_grafico_individual_indice(res_ejemplo, "AMO", CATALOGO)
        st.pyplot(fig_ejemplo, clear_figure=True)
        plt.close(fig_ejemplo)

    st.markdown(
        "> **Interpretación visual:**  \n"
        "> • **Línea verde horizontal:** Marca el umbral mínimo de correlación ($r_{\\text{umbral}} = 0.60$). Los puntos de la serie azul por encima de ella satisfacen el criterio de sincronía.  \n"
        "> • **Línea naranja horizontal:** Marca el umbral máximo de diferencia ($MAD_{\\text{umbral}} = 0.15\\ ^\\circ\\text{C}$). Los puntos de la serie roja por debajo de ella satisfacen el criterio de proximidad.  \n"
        "> • **Bandas verdes verticales y etiquetas superiores a 45°:** Identifican los años análogos que cumplen **simultáneamente** ambos umbrales (ej. 1949, 1957, 1959, 1990, 1997, 2001, 2013, 2014, 2018, 2021).  \n"
        "> • **Puntos grises:** Años candidatos que no superaron al menos uno de los dos filtros."
    )

# ==============================================================================
# SECCIÓN 1: ESTADO DE DATOS DISPONIBLES
# ==============================================================================
elif seccion_seleccionada == "1. Estado de datos disponibles":
    st.header("1. Estado de datos disponibles")
    st.markdown(
        "Supervise el estado de cobertura, registros históricos y disponibilidad operacional "
        "de las 21 series climáticas, o ejecute una actualización atómica y no destructiva."
    )
    st.divider()

    df_salud = obtener_estado_fuentes(oscilaciones_disponibles, CATALOGO)
    disponibles = len(df_salud[df_salud["Estado"].str.contains("Disponible", na=False)])
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
            v["status"] in ["OK", "Sin cambios", "actualizado", "disponible"] for v in res_update.values()
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
        st.dataframe(pd.DataFrame(res_rows), width="stretch")

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
        width="stretch",
        height=450,
        column_config={
            "Primer Año": st.column_config.NumberColumn("Primer Año", format="%d"),
            "Último Año": st.column_config.NumberColumn("Último Año", format="%d"),
            "Años Registrados": st.column_config.NumberColumn("Años Registrados", format="%d"),
        },
        hide_index=True,
    )

# ==============================================================================
# SECCIÓN 2: CONFIGURACIÓN DE UMBRALES
# ==============================================================================
elif seccion_seleccionada == "2. Configuración de umbrales":
    st.header("2. Configuración de umbrales")
    st.markdown(
        "Personalice los umbrales de correlación de Pearson ($r_{\text{umbral}}$) y distancia absoluta media "
        "($\text{MAD}_{\text{umbral}}$) para cada uno de los 21 índices. Los valores metodológicos oficiales "
        "se cargan como valores predeterminados y pueden ser restaurados en cualquier momento."
    )
    st.divider()

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn2:
        if st.button(
            "🔄 Restaurar Valores Metodológicos Predeterminados",
            width="stretch",
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

# ==============================================================================
# SECCIÓN: DOCUMENTACIÓN Y CRÉDITOS
# ==============================================================================
elif seccion_seleccionada == "Documentación y créditos":
    st.header("Documentación y créditos")
    st.markdown(
        "Acceso centralizado a los manuales de usuario, arquitectura técnica, procedimientos de instalación, "
        "fuentes oficiales de datos y referencias científicas del sistema **AAnalogos**."
    )
    st.divider()

    tab_docs, tab_creditos = st.tabs(["📚 Documentación del Sistema", "🏛️ Créditos y Atribución"])

    with tab_docs:
        st.subheader("📚 Visor Integrado de Documentación")
        st.markdown(
            "Consulte directamente las guías de usuario, metodología científica, catálogo de índices y manuales "
            "técnicos del sistema. Los enlaces internos entre documentos navegan de forma interactiva sin recargar la página."
        )

        docs_disponibles = obtener_documentos_disponibles(DIRECTORIO_ACTUAL)

        if not docs_disponibles:
            st.warning("⚠️ No se encontraron documentos Markdown en el directorio `docs/`.")
        else:
            opciones_docs = list(docs_disponibles.keys())

            # 1. Determinar documento activo a partir de query_param o sesión
            doc_param = st.query_params.get("doc")
            etiqueta_desde_url = None
            if doc_param:
                etiqueta_desde_url = buscar_etiqueta_documento(doc_param, docs_disponibles, DIRECTORIO_ACTUAL)
                if not etiqueta_desde_url:
                    st.warning(f"⚠️ El documento solicitado en el enlace (`{doc_param}`) no fue encontrado.")

            if etiqueta_desde_url and etiqueta_desde_url in opciones_docs:
                idx_default = opciones_docs.index(etiqueta_desde_url)
            elif "doc_activo_etiqueta" in st.session_state and st.session_state["doc_activo_etiqueta"] in opciones_docs:
                idx_default = opciones_docs.index(st.session_state["doc_activo_etiqueta"])
            else:
                idx_default = 0

            # 2. Barra de navegación y selector sincronizado
            col_nav_home, col_sel_doc = st.columns([1, 3])
            with col_nav_home:
                if st.button("📑 Índice General", width="stretch", help="Volver al índice general de la documentación"):
                    st.query_params["doc"] = "docs/README.md"
                    st.session_state["doc_activo_etiqueta"] = "📖 Índice General (docs/README)"
                    st.rerun()

            with col_sel_doc:
                doc_sel_etiqueta = st.selectbox(
                    "Documento:",
                    options=opciones_docs,
                    index=idx_default,
                    key="selector_doc_markdown",
                    help="Seleccione el documento Markdown que desea visualizar."
                )

            st.session_state["doc_activo_etiqueta"] = doc_sel_etiqueta
            ruta_doc_sel = docs_disponibles[doc_sel_etiqueta]

            # Mantener query_param actualizado con la ruta relativa del documento activo
            rel_path_act = os.path.relpath(ruta_doc_sel, DIRECTORIO_ACTUAL).replace("\\", "/")
            if st.query_params.get("doc") != rel_path_act:
                st.query_params["doc"] = rel_path_act

            if not os.path.isfile(ruta_doc_sel):
                st.warning(f"⚠️ El archivo `{os.path.basename(ruta_doc_sel)}` no se encuentra disponible en `{ruta_doc_sel}`.")
            else:
                try:
                    with open(ruta_doc_sel, "r", encoding="utf-8") as f_doc:
                        contenido_raw = f_doc.read()

                    # Transformar enlaces internos .md a formato de navegación interna
                    contenido_trans = transformar_enlaces_markdown(
                        contenido_raw,
                        ruta_doc_actual=ruta_doc_sel,
                        directorio_base=DIRECTORIO_ACTUAL
                    )

                    st.divider()
                    st.markdown(contenido_trans, unsafe_allow_html=True)
                except Exception as err_doc:
                    st.error(f"❌ Error al leer el documento '{doc_sel_etiqueta}': {err_doc}")

    with tab_creditos:
        st.subheader("🌦️ Acerca de Aanalogos")
        st.markdown(
            f"**Sistema de Selección de Años Análogos Climáticos — Versión 3.2.0**  \n\n"
            f"**Propósito:** Proporcionar una herramienta estadística, reproducible y auditable para identificar patrones históricos análogos "
            f"en la evolución de oscilaciones climáticas acopladas océano-atmósfera, facilitando la toma de decisiones en pronósticos estacionales.\n\n"
            f"**Personalización Institucional Activa:**  \n"
            f"* **Institución:** {CONFIG_INSTITUCION['name']}  \n"
            f"* **División / Departamento:** {CONFIG_INSTITUCION['division']}  \n"
            f"* **Logotipo:** `{'Configurado (' + str(CONFIG_INSTITUCION['logo']) + ')' if CONFIG_INSTITUCION.get('logo') else 'Modo Neutro (Sin logo)'}`\n"
        )

        st.divider()
        st.subheader("👨‍💻 Desarrollo y Mantenimiento")
        st.markdown(
            "**William Abarca**  \n"
            "Gerencia de Meteorología — Observatorio de Amenazas y Recursos Naturales  \n"
            "*Ministerio de Medio Ambiente y Recursos Naturales*  \n"
            "El Salvador  \n"
            "✉️ [wabarca@ambiente.gob.sv](mailto:wabarca@ambiente.gob.sv)"
        )

        st.divider()
        st.subheader("🌐 Fuentes Oficiales de Datos")
        st.markdown(
            "- NOAA Climate Prediction Center (CPC)  \n"
            "- NOAA Physical Sciences Laboratory (PSL)  \n"
            "- NOAA National Centers for Environmental Information (NCEI)  \n"
            "- Colorado State University (CSU) Department of Atmospheric Science  \n\n"
            "**Licencia y Uso:** Código abierto para servicios meteorológicos e instituciones de investigación."
        )

