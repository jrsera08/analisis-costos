"""
dashboard.py
------------
Dashboard de análisis de costos de importación.
Lee el archivo Condensado generado por transformar.py.

Instalación (una sola vez):
    pip install streamlit plotly pandas openpyxl

Uso:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis de Costos de Importación",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main-title {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2.4rem;
        color: #0f172a;
        letter-spacing: -1px;
        margin-bottom: 0;
    }
    .sub-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 300;
        font-size: 1rem;
        color: #64748b;
        margin-top: 4px;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 20px 24px;
        color: white;
        border: 1px solid #334155;
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 4px;
    }
    .section-header {
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }
    .stSelectbox label, .stMultiSelect label {
        font-weight: 500;
        color: #374151;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    div[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stMultiSelect label {
        color: #94a3b8 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ── Paleta de colores para gráficos ──────────────────────────────────────────
COLORES = [
    "#3b82f6", "#f59e0b", "#10b981", "#ef4444",
    "#8b5cf6", "#06b6d4", "#f97316", "#ec4899",
]

# ── Columnas de costos disponibles ────────────────────────────────────────────
COLUMNAS_COSTOS = [
    "Precio compra EUROS",
    "Costo pieza mxn",
    "Flete Maritimo ($/pieza)",
    "DTA ($/pieza)",
    "IGI ($/pieza)",
    "Aduana y Flete Terrestre ($/pieza)",
    "COSTO DE IMPORTACION X PIEZA ($/pieza)",
    "Gastos Locales Naviera $/pieza",
    "Costo Compra Ana Dis ($/pieza)",
    "Precio Unitario Compra Pasta Mia",
]

COLUMNAS_TIPO_CAMBIO = [
    "TIPO DE CAMBIO",
    "DÓLAR (DOF)",
    "FACTORAJE (DOF)",
]

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_excel(archivo)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Año"]   = df["Fecha"].dt.year
    df["Mes"]   = df["Fecha"].dt.to_period("M").astype(str)
    for col in COLUMNAS_COSTOS + COLUMNAS_TIPO_CAMBIO:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def delta_color(val):
    if val > 0:
        return "color: #f59e0b"
    elif val < 0:
        return "color: #10b981"
    return "color: #94a3b8"


# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📦 Importaciones")
    st.markdown("---")

    archivo = st.file_uploader(
        "CARGAR CONDENSADO (.xlsx)",
        type=["xlsx"],
        help="Sube el archivo generado por transformar.py",
    )

    if archivo:
        df = cargar_datos(archivo)
        años_disponibles = sorted(df["Año"].dropna().unique().astype(int))

        st.markdown("### PERÍODO")
        años_sel = st.multiselect(
            "AÑOS A VISUALIZAR",
            options=años_disponibles,
            default=años_disponibles[-2:] if len(años_disponibles) >= 2 else años_disponibles,
        )

        st.markdown("### COMPARACIÓN")
        comparar = st.checkbox("Comparar dos años específicos", value=True)
        if comparar and len(años_disponibles) >= 2:
            año_a = st.selectbox("AÑO BASE", años_disponibles, index=len(años_disponibles)-2)
            año_b = st.selectbox("AÑO COMPARAR", años_disponibles, index=len(años_disponibles)-1)
        else:
            año_a = año_b = None

        st.markdown("### FILTROS")
        productos_disp = sorted(df["Producto/Presentación"].dropna().unique())
        productos_sel  = st.multiselect(
            "PRODUCTOS",
            options=productos_disp,
            default=productos_disp,
        )

        exportadores_disp = sorted(df["Exportador"].dropna().unique())
        exportadores_sel  = st.multiselect(
            "EXPORTADOR",
            options=exportadores_disp,
            default=exportadores_disp,
        )

        st.markdown("### VISUALIZACIÓN")
        tipo_grafico = st.radio(
            "TIPO DE GRÁFICO",
            ["Barras", "Línea", "Barras + Línea"],
            index=0,
        )


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="main-title">Análisis de Costos de Importación</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Comparativa anual · Comportamiento por producto · Tipo de cambio</p>', unsafe_allow_html=True)

if not archivo:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 **Carga tu archivo Condensado** desde el panel izquierdo para comenzar.")
    st.stop()

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df_filtrado = df[
    df["Producto/Presentación"].isin(productos_sel) &
    df["Exportador"].isin(exportadores_sel)
]
if años_sel:
    df_filtrado = df_filtrado[df_filtrado["Año"].isin(años_sel)]

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
#  MÉTRICAS RESUMEN
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">Resumen del período seleccionado</p>', unsafe_allow_html=True)

cols_metricas = st.columns(4)
metricas = [
    ("Registros totales",       len(df_filtrado),                                          None),
    ("Productos únicos",        df_filtrado["Producto/Presentación"].nunique(),             None),
    ("Precio compra EUR (prom)", df_filtrado["Precio compra EUROS"].mean()                 if "Precio compra EUROS" in df_filtrado else None, "€"),
    ("Costo importación (prom)", df_filtrado["COSTO DE IMPORTACION X PIEZA ($/pieza)"].mean() if "COSTO DE IMPORTACION X PIEZA ($/pieza)" in df_filtrado else None, "$"),
]

for col, (label, val, sym) in zip(cols_metricas, metricas):
    with col:
        display = f"{sym}{val:,.4f}" if (val is not None and sym) else (f"{val:,}" if isinstance(val, (int, float)) else "—")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{display}</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  TABS PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Comparativa de Costos",
    "🔁 Comparación entre Años",
    "💱 Tipo de Cambio",
    "📋 Datos Detallados",
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — Comparativa de costos por producto/año
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<p class="section-header">Costos por producto y año</p>', unsafe_allow_html=True)

    col_izq, col_der = st.columns([1, 3])
    with col_izq:
        costo_sel = st.selectbox(
            "Selecciona el costo a analizar",
            options=[c for c in COLUMNAS_COSTOS if c in df_filtrado.columns],
        )
        agrupar_por = st.radio("Agrupar por", ["Producto", "Año", "Mes"], index=0)

    with col_der:
        if agrupar_por == "Producto":
            grp = df_filtrado.groupby(["Producto/Presentación", "Año"])[costo_sel].mean().reset_index()
            fig = go.Figure()
            for i, año in enumerate(sorted(grp["Año"].unique())):
                datos_año = grp[grp["Año"] == año]
                color = COLORES[i % len(COLORES)]
                if tipo_grafico == "Barras":
                    fig.add_trace(go.Bar(
                        name=str(año),
                        x=datos_año["Producto/Presentación"],
                        y=datos_año[costo_sel],
                        marker_color=color,
                        text=datos_año[costo_sel].round(4),
                        textposition="outside",
                    ))
                elif tipo_grafico == "Línea":
                    fig.add_trace(go.Scatter(
                        name=str(año),
                        x=datos_año["Producto/Presentación"],
                        y=datos_año[costo_sel],
                        mode="lines+markers",
                        line=dict(color=color, width=2.5),
                        marker=dict(size=8),
                    ))
                else:  # Barras + Línea
                    fig.add_trace(go.Bar(
                        name=f"{año} (barra)",
                        x=datos_año["Producto/Presentación"],
                        y=datos_año[costo_sel],
                        marker_color=color,
                        opacity=0.7,
                    ))
                    fig.add_trace(go.Scatter(
                        name=f"{año} (línea)",
                        x=datos_año["Producto/Presentación"],
                        y=datos_año[costo_sel],
                        mode="lines+markers",
                        line=dict(color=color, width=2, dash="dot"),
                    ))

        elif agrupar_por == "Año":
            grp = df_filtrado.groupby("Año")[costo_sel].mean().reset_index()
            fig = go.Figure()
            if tipo_grafico in ["Barras", "Barras + Línea"]:
                fig.add_trace(go.Bar(
                    x=grp["Año"].astype(str),
                    y=grp[costo_sel],
                    marker_color=COLORES[:len(grp)],
                    text=grp[costo_sel].round(4),
                    textposition="outside",
                ))
            if tipo_grafico in ["Línea", "Barras + Línea"]:
                fig.add_trace(go.Scatter(
                    x=grp["Año"].astype(str),
                    y=grp[costo_sel],
                    mode="lines+markers",
                    line=dict(color=COLORES[1], width=3),
                    marker=dict(size=10),
                ))

        else:  # Mes
            grp = df_filtrado.groupby(["Mes", "Año"])[costo_sel].mean().reset_index().sort_values("Mes")
            fig = go.Figure()
            for i, año in enumerate(sorted(grp["Año"].unique())):
                datos_año = grp[grp["Año"] == año]
                color = COLORES[i % len(COLORES)]
                if tipo_grafico == "Barras":
                    fig.add_trace(go.Bar(name=str(año), x=datos_año["Mes"], y=datos_año[costo_sel], marker_color=color))
                else:
                    fig.add_trace(go.Scatter(
                        name=str(año), x=datos_año["Mes"], y=datos_año[costo_sel],
                        mode="lines+markers", line=dict(color=color, width=2.5), marker=dict(size=7),
                    ))

        fig.update_layout(
            title=dict(text=f"<b>{costo_sel}</b> — promedio por {agrupar_por.lower()}", font=dict(size=15, color="#1e293b")),
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="DM Sans", size=12, color="#374151"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
            yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickformat=",.4f"),
            height=450,
            margin=dict(t=60, b=40, l=40, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Todos los costos en una sola vista
    st.markdown('<p class="section-header">Todos los costos — vista general</p>', unsafe_allow_html=True)
    costos_disponibles = [c for c in COLUMNAS_COSTOS if c in df_filtrado.columns]
    grp_todos = df_filtrado.groupby("Año")[costos_disponibles].mean().reset_index()

    fig_todos = go.Figure()
    for i, costo in enumerate(costos_disponibles):
        fig_todos.add_trace(go.Bar(
            name=costo,
            x=grp_todos["Año"].astype(str),
            y=grp_todos[costo],
            marker_color=COLORES[i % len(COLORES)],
        ))
    fig_todos.update_layout(
        barmode="group",
        title=dict(text="<b>Todos los costos</b> agrupados por año", font=dict(size=15, color="#1e293b")),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=11, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9", tickformat=",.4f"),
        height=480, margin=dict(t=80, b=40, l=40, r=20),
    )
    st.plotly_chart(fig_todos, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — Comparación directa entre dos años
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<p class="section-header">Comparación directa entre dos años</p>', unsafe_allow_html=True)

    if not comparar or año_a is None:
        st.info("Activa la comparación de dos años en el panel izquierdo.")
    else:
        df_a = df_filtrado[df_filtrado["Año"] == año_a]
        df_b = df_filtrado[df_filtrado["Año"] == año_b]

        costos_disp = [c for c in COLUMNAS_COSTOS if c in df_filtrado.columns]

        media_a = df_a[costos_disp].mean()
        media_b = df_b[costos_disp].mean()
        delta   = ((media_b - media_a) / media_a * 100).round(2)

        # Tabla resumen
        resumen = pd.DataFrame({
            "Costo":           costos_disp,
            f"Prom {año_a}":   media_a.values,
            f"Prom {año_b}":   media_b.values,
            "Δ %":             delta.values,
        })

        st.dataframe(
            resumen.style
                .format({f"Prom {año_a}": "{:,.4f}", f"Prom {año_b}": "{:,.4f}", "Δ %": "{:+.2f}%"})
                .applymap(lambda v: "color: #ef4444" if isinstance(v, float) and v > 0
                          else ("color: #10b981" if isinstance(v, float) and v < 0 else ""), subset=["Δ %"]),
            use_container_width=True, hide_index=True,
        )

        st.markdown('<p class="section-header">Gráfico comparativo por costo</p>', unsafe_allow_html=True)

        fig_comp = make_subplots(rows=1, cols=2, subplot_titles=(
            f"Valores promedio ({año_a} vs {año_b})",
            f"Variación porcentual ({año_a} → {año_b})"
        ))

        fig_comp.add_trace(go.Bar(name=str(año_a), x=costos_disp, y=media_a.values,
                                  marker_color=COLORES[0], text=media_a.round(4), textposition="outside"), row=1, col=1)
        fig_comp.add_trace(go.Bar(name=str(año_b), x=costos_disp, y=media_b.values,
                                  marker_color=COLORES[1], text=media_b.round(4), textposition="outside"), row=1, col=1)

        colores_delta = ["#ef4444" if v > 0 else "#10b981" for v in delta.values]
        fig_comp.add_trace(go.Bar(
            name="Δ %", x=costos_disp, y=delta.values,
            marker_color=colores_delta,
            text=[f"{v:+.2f}%" for v in delta.values],
            textposition="outside",
        ), row=1, col=2)

        fig_comp.update_layout(
            barmode="group", height=500,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans", size=11, color="#374151"),
            showlegend=True,
            margin=dict(t=60, b=100, l=40, r=20),
        )
        fig_comp.update_xaxes(tickangle=-35)
        fig_comp.update_yaxes(gridcolor="#f1f5f9")
        st.plotly_chart(fig_comp, use_container_width=True)

        # Por producto
        st.markdown('<p class="section-header">Variación por producto</p>', unsafe_allow_html=True)
        costo_prod = st.selectbox("Costo a comparar por producto", costos_disp, key="costo_prod")

        grp_prod_a = df_a.groupby("Producto/Presentación")[costo_prod].mean()
        grp_prod_b = df_b.groupby("Producto/Presentación")[costo_prod].mean()
        productos_comunes = grp_prod_a.index.intersection(grp_prod_b.index)

        if len(productos_comunes) > 0:
            fig_prod = go.Figure()
            fig_prod.add_trace(go.Bar(name=str(año_a), x=list(productos_comunes),
                                      y=grp_prod_a[productos_comunes].values, marker_color=COLORES[0]))
            fig_prod.add_trace(go.Bar(name=str(año_b), x=list(productos_comunes),
                                      y=grp_prod_b[productos_comunes].values, marker_color=COLORES[1]))
            fig_prod.update_layout(
                barmode="group", height=400,
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="DM Sans", size=12, color="#374151"),
                yaxis=dict(gridcolor="#f1f5f9", tickformat=",.4f"),
                xaxis=dict(showgrid=False),
                margin=dict(t=40, b=40, l=40, r=20),
            )
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("No hay productos comunes entre los dos años seleccionados.")


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — Tipo de Cambio
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<p class="section-header">Evolución del tipo de cambio</p>', unsafe_allow_html=True)

    tc_disponibles = [c for c in COLUMNAS_TIPO_CAMBIO if c in df_filtrado.columns]
    tc_sel = st.multiselect("Variables a graficar", tc_disponibles, default=tc_disponibles)

    if tc_sel:
        col_a, col_b = st.columns([3, 1])
        with col_b:
            agrupar_tc = st.radio("Agrupar por", ["Mes", "Año"], key="tc_agrup")
            tipo_tc    = st.radio("Tipo", ["Línea", "Barras"], key="tc_tipo")

        with col_a:
            grp_col = "Mes" if agrupar_tc == "Mes" else "Año"
            grp_tc  = df_filtrado.groupby([grp_col, "Año"])[tc_sel].mean().reset_index().sort_values(grp_col)

            fig_tc = make_subplots(
                rows=len(tc_sel), cols=1,
                shared_xaxes=True,
                subplot_titles=tc_sel,
                vertical_spacing=0.08,
            )

            for idx, variable in enumerate(tc_sel, start=1):
                for i, año in enumerate(sorted(grp_tc["Año"].unique())):
                    datos = grp_tc[grp_tc["Año"] == año]
                    color = COLORES[i % len(COLORES)]
                    if tipo_tc == "Línea":
                        fig_tc.add_trace(go.Scatter(
                            name=f"{variable} {año}",
                            x=datos[grp_col].astype(str),
                            y=datos[variable],
                            mode="lines+markers",
                            line=dict(color=color, width=2.5),
                            marker=dict(size=6),
                            showlegend=(idx == 1),
                        ), row=idx, col=1)
                    else:
                        fig_tc.add_trace(go.Bar(
                            name=f"{variable} {año}",
                            x=datos[grp_col].astype(str),
                            y=datos[variable],
                            marker_color=color,
                            showlegend=(idx == 1),
                        ), row=idx, col=1)

            fig_tc.update_layout(
                height=300 * len(tc_sel),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="DM Sans", size=11, color="#374151"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=60, b=40, l=40, r=20),
            )
            fig_tc.update_yaxes(gridcolor="#f1f5f9", tickformat=",.4f")
            fig_tc.update_xaxes(showgrid=False, tickangle=-30)
            st.plotly_chart(fig_tc, use_container_width=True)

        # Tabla resumen tipo de cambio por año
        st.markdown('<p class="section-header">Estadísticas por año</p>', unsafe_allow_html=True)
        stats_tc = df_filtrado.groupby("Año")[tc_sel].agg(["mean", "min", "max"]).round(4)
        stats_tc.columns = [f"{col[0]} ({col[1]})" for col in stats_tc.columns]
        st.dataframe(stats_tc, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — Datos detallados
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<p class="section-header">Tabla de datos completa</p>', unsafe_allow_html=True)

    buscar = st.text_input("🔍 Buscar en tabla", placeholder="Producto, exportador, factura...")
    df_tabla = df_filtrado.copy()
    if buscar:
        mask = df_tabla.apply(lambda col: col.astype(str).str.contains(buscar, case=False, na=False)).any(axis=1)
        df_tabla = df_tabla[mask]

    st.dataframe(
        df_tabla.drop(columns=["Año", "Mes"], errors="ignore").style.format(
            {c: "{:,.4f}" for c in COLUMNAS_COSTOS + COLUMNAS_TIPO_CAMBIO if c in df_tabla.columns}
        ),
        use_container_width=True, height=500,
    )
    st.caption(f"{len(df_tabla):,} registros mostrados")

    col_dl1, col_dl2 = st.columns([1, 5])
    with col_dl1:
        csv = df_tabla.drop(columns=["Año", "Mes"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "exportacion_filtrada.csv", "text/csv")
