import os
import sys
from streamlit.web import cli as stcli

# Ensure the current directory is in sys.path so local modules like utils can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Auto-run block removed to prevent conflicts
if __name__ == "__main__":
    if not os.environ.get("STREAMLIT_RUNNING_IN_SUBPROCESS"):
        os.environ["STREAMLIT_RUNNING_IN_SUBPROCESS"] = "true"
        sys.argv = ["streamlit", "run", sys.argv[0], "--server.port", "8501"]
        sys.exit(stcli.main())

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import requests
import io
import hashlib

# -----------------------------------------------------------------------------
# IMPORTAR MÓDULOS LOCALES
# -----------------------------------------------------------------------------
import charts
import utils
import styles

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gestor Académico Pro",
    layout="wide",
    page_icon="🎓",
)
st.markdown(styles.APP_STYLE, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES Y CACHÉ
# -----------------------------------------------------------------------------

class FileLike(io.BytesIO):
    """Wrapper para manejar archivos en memoria con atributo .name"""
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name

@st.cache_data(ttl=3600)
def cargar_datos_optimizado(file_or_url, es_url=False):
    """
    Carga y procesa el archivo. Usa caché para no recargar en cada interacción.
    """
    try:
        archivo_final = file_or_url
        
        if es_url:
            url = file_or_url.strip()
            # Forzar descarga en OneDrive
            if ("onedrive.live.com" in url or "1drv.ms" in url) and "download=1" not in url:
                sep = "&" if "?" in url else "?"
                url = url + sep + "download=1"
            
            resp = requests.get(url)
            resp.raise_for_status()
            
            # Inferir nombre
            nombre = "data_onedrive.xlsx"
            if ".csv" in url.lower(): nombre = "data_onedrive.csv"
            
            archivo_final = FileLike(resp.content, nombre)

        # Usamos la función load_data de tu utils.py
        df = utils.load_data(archivo_final)
        if df is None:
            return pd.DataFrame()
        return df

    except Exception as e:
        st.error(f"Error crítico al cargar datos: {e}")
        return pd.DataFrame()

# Funciones de cálculo rápido para los Tabs
def resumen_coordinadoras_semana(df_filtrado: pd.DataFrame) -> pd.DataFrame:
    if df_filtrado.empty: return pd.DataFrame()
    cols_req = ["Dia_Semana", "Modalidad_Calc", "PROGRAMA", "COORDINADORA RESPONSABLE"]
    if not all(c in df_filtrado.columns for c in cols_req): return pd.DataFrame()

    g = df_filtrado.groupby("COORDINADORA RESPONSABLE")
    base = g.agg(dias_clase_semana=("Dia_Semana", "nunique")).reset_index()
    
    # Concatenar textos únicos
    base["Modalidades"] = g["Modalidad_Calc"].apply(lambda x: ", ".join(sorted(x.dropna().unique())))
    base["Programas"] = g["PROGRAMA"].apply(lambda x: ", ".join(sorted(x.dropna().unique())))
    
    return base.rename(columns={
        "COORDINADORA RESPONSABLE": "Coordinadora", 
        "dias_clase_semana": "Días Activos (Semana)"
    })

def resumen_modalidad(df_f):
    if df_f.empty or "Modalidad_Calc" not in df_f.columns: return pd.DataFrame()
    return df_f.groupby("Modalidad_Calc", as_index=False).agg(
        Sesiones=("PROGRAMA", "size"), Programas=("PROGRAMA", "nunique")
    ).sort_values("Sesiones", ascending=False)

def resumen_sede(df_f):
    if df_f.empty or "SEDE" not in df_f.columns: return pd.DataFrame()
    return df_f.groupby("SEDE", as_index=False).agg(
        Sesiones=("PROGRAMA", "size"), Programas=("PROGRAMA", "nunique")
    ).sort_values("Sesiones", ascending=False)

def resumen_calidad_datos(df_all):
    campos = ["DIAS/FECHAS", "PROGRAMA", "COORDINADORA RESPONSABLE", "Modalidad_Calc", "SEDE", "HORARIO"]
    data = []
    total = len(df_all)
    if total == 0: return pd.DataFrame()
    for col in campos:
        if col in df_all.columns:
            faltantes = df_all[col].isna().sum()
            data.append({"Campo": col, "Faltantes": faltantes, "%": round((faltantes/total)*100, 1)})
    return pd.DataFrame(data)

# -----------------------------------------------------------------------------
# INTERFAZ: SIDEBAR
# -----------------------------------------------------------------------------
st.title("🎓 Dashboard de Gestión Académica")
st.markdown("---")

with st.sidebar:
    st.header("📂 Panel de Control")
    
    # Opción: Subir archivo o Link
    uploaded_file = st.file_uploader("Sube Excel o CSV", type=["xlsx", "csv"])
    onedrive_url = st.text_input("O pega un Link de OneDrive / SharePoint")
    
    df_base = pd.DataFrame()
    
    # Prioridad: Archivo subido > Link
    if uploaded_file:
        # Pasamos directamente el objeto uploaded_file
        df_base = cargar_datos_optimizado(uploaded_file, es_url=False)
            
    elif onedrive_url:
        # Pasamos la URL directamente
        df_base = cargar_datos_optimizado(onedrive_url, es_url=True)

    st.markdown("---")

    st.markdown("---")
    
    if not df_base.empty:
        st.success("✅ Datos cargados")
        # Botón descarga reporte completo
        excel_data = utils.generate_excel_report(df_base)
        st.download_button(
            label="📤 Reporte Completo (Excel)",
            data=excel_data,
            file_name="Reporte_Gestion_Total.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("---")
    if st.button("🧹 Resetear Filtros"):
        utils.reset_filters()
        st.rerun()

# Detener si no hay datos
if df_base.empty:
    st.info("👋 Para comenzar, por favor carga tu archivo de planificación.")
    st.stop()
    sys.exit()

# Validación extra de columnas antes de continuar
if "DIAS/FECHAS" not in df_base.columns:
    st.error("❌ Error: El archivo cargado no contiene la columna 'DIAS/FECHAS'. Por favor verifica el formato.")
    st.write("Columnas detectadas:", df_base.columns.tolist())
    st.stop()
    sys.exit()

# -----------------------------------------------------------------------------
# TABS PRINCIPALES
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab_gestion, tab_validaciones = st.tabs([
    "👩‍💼 Coordinadoras", 
    "📊 Comparativa", 
    "🌐 Global", 
    "🧾 Resumen Programas", 
    "🏫 Calidad & Sede",
    "🔒 Gestión",
    "🕵️ Validaciones"
])

# =============================================================================
# TAB 1: COORDINADORAS (FILTROS EN CASCADA / DEPENDIENTES)
# =============================================================================
with tab1:
    st.markdown("## 🔎 Gestión Detallada por Coordinadora")
    
    # --- LÓGICA DE CASCADA ---
    st.markdown(styles.card_start(), unsafe_allow_html=True)
    st.markdown("### 🔍 Filtros")
    # Paso 1: Año y Mes
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        years_disp = sorted(df_base["DIAS/FECHAS"].dt.year.unique())
        sel_year = st.multiselect("1. Año", years_disp, key="t1_year", placeholder="Todos")
        # Filtro
        df_1 = df_base[df_base["DIAS/FECHAS"].dt.year.isin(sel_year)] if sel_year else df_base

    with c2:
        meses_disp = sorted(df_1["Mes"].unique(), key=lambda x: utils.MESES.get(x.lower(), 99)) if "Mes" in df_1.columns else []
        sel_mes = st.multiselect("2. Mes", meses_disp, key="t1_mes", placeholder="Todos")
        df_2 = df_1[df_1["Mes"].isin(sel_mes)] if sel_mes else df_1
        
    with c3:
        coords_disp = sorted(df_2["COORDINADORA RESPONSABLE"].unique())
        sel_coord = st.multiselect("3. Coordinadora", coords_disp, key="t1_coord", placeholder="Todas")
        df_3 = df_2[df_2["COORDINADORA RESPONSABLE"].isin(sel_coord)] if sel_coord else df_2
        
    with c4:
        progs_disp = sorted(df_3["PROGRAMA"].unique())
        sel_prog = st.multiselect("4. Programa", progs_disp, key="t1_prog", placeholder="Todos")
        df_4 = df_3[df_3["PROGRAMA"].isin(sel_prog)] if sel_prog else df_3
    
    st.markdown(styles.card_end(), unsafe_allow_html=True)

    # Segunda fila de filtros
    c5, c6, c7, c8 = st.columns(4)
    
    # Paso 5: Sede
    with c5:
        sedes_disp = sorted(df_4["SEDE"].unique())
        sel_sede = st.multiselect("5. Sede", sedes_disp, key="t1_sede", placeholder="Todas")
        df_5 = df_4[df_4["SEDE"].isin(sel_sede)] if sel_sede else df_4

    # Paso 6: Modalidad
    with c6:
        mods_disp = sorted(df_5["Modalidad_Calc"].unique())
        sel_mod = st.multiselect("6. Modalidad", mods_disp, key="t1_mod", placeholder="Todas")
        df_6 = df_5[df_5["Modalidad_Calc"].isin(sel_mod)] if sel_mod else df_5

    # Paso 7: Profesor
    with c7:
        if "PROFESOR" in df_6.columns:
            profs_disp = sorted(df_6["PROFESOR"].dropna().astype(str).unique())
            sel_prof = st.multiselect("7. Profesor", profs_disp, key="t1_prof", placeholder="Todos")
            df_7 = df_6[df_6["PROFESOR"].isin(sel_prof)] if sel_prof else df_6
        else:
            df_7 = df_6

    # Paso 8: Día Semana
    with c8:
        dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dias_disp = sorted(df_7["Dia_Semana"].unique(), key=lambda x: dias_orden.index(x) if x in dias_orden else 99)
        sel_dia = st.multiselect("8. Día Semana", dias_disp, key="t1_dia", placeholder="Todos")
        # Filtro Final
        df_final_t1 = df_7[df_7["Dia_Semana"].isin(sel_dia)] if sel_dia else df_7

    st.markdown("---")

    if df_final_t1.empty:
        st.warning("⚠️ No se encontraron clases con esta combinación de filtros.")
    else:
        # KPIs
        total_sesiones = len(df_final_t1)
        total_progs = df_final_t1["PROGRAMA"].nunique()
        
        # Cálculo de carga diaria (Días con > 2 programas)
        carga_diaria = df_final_t1.groupby(["COORDINADORA RESPONSABLE", "DIAS/FECHAS"]).agg(
            N_Progs=("PROGRAMA", "nunique"),
            Programas=("PROGRAMA", lambda x: ", ".join(sorted(x.unique()))),
            Dia=("Dia_Semana", "first")
        ).reset_index()
        
        dias_criticos = carga_diaria[carga_diaria["N_Progs"] > 2]

        st.markdown(styles.card_start(), unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Sesiones", total_sesiones)
        k2.metric("Programas", total_progs)
        k3.metric("Días Activos", df_final_t1["DIAS/FECHAS"].nunique())
        k4.metric("Días Críticos (>2 Prog)", len(dias_criticos), delta_color="inverse")
        st.markdown(styles.card_end(), unsafe_allow_html=True)

        # Gráfico y Tabla de Críticos
        # col_g, col_t = st.columns([2, 1])  <-- Removed column layout
        
        st.markdown(styles.card_start(), unsafe_allow_html=True)
        # Gráfico (Arriba)
        df_plot = carga_diaria.copy()
        df_plot["Fecha"] = df_plot["DIAS/FECHAS"].dt.strftime("%d-%m-%Y")
        
        # Color dinámico: Si hay muchas coordinadoras, colorea por coord. Si es 1, colorea por intensidad.
        color_by = "COORDINADORA RESPONSABLE" if df_final_t1["COORDINADORA RESPONSABLE"].nunique() > 1 else "N_Progs"
        
        fig_d = px.bar(
            df_plot, x="Fecha", y="N_Progs", color=color_by,
            title="Intensidad de Programas por Día",
            labels={"N_Progs": "Nº Programas", "Fecha": "Fecha"},
            text="N_Progs"
        )
        fig_d.add_hline(y=2, line_dash="dot", annotation_text="Límite Ideal (2)")
        st.plotly_chart(charts.update_chart_layout(fig_d), use_container_width=True)

        # Tabla (Abajo)
        st.markdown("##### 🚨 Detalle Días Críticos")
        if not dias_criticos.empty:
            dias_criticos["Fecha"] = dias_criticos["DIAS/FECHAS"].dt.strftime("%d-%m-%Y")
            
            st.dataframe(
                dias_criticos[["Fecha", "Dia", "COORDINADORA RESPONSABLE", "N_Progs", "Programas"]],
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "COORDINADORA RESPONSABLE": "Coordinadora",
                    "N_Progs": st.column_config.NumberColumn("Nº", help="Cantidad de programas"),
                    "Programas": st.column_config.TextColumn("Programas", width="medium"),
                    "Dia": "Día"
                }
            )
        else:
            st.success("¡Excelente! No hay días con sobrecarga (>2 programas) en esta selección.")
        st.markdown(styles.card_end(), unsafe_allow_html=True)

    # =============================================================================
    # TABLA DETALLADA
    # =============================================================================
    if not df_final_t1.empty:
        st.markdown("---")
        st.subheader("📅 Calendario Detallado")
        cols_ver = ["DIAS/FECHAS", "Dia_Semana", "HORARIO", "PROGRAMA", "COORDINADORA RESPONSABLE", "SEDE", "Modalidad_Calc", "ASIGNATURA"]
        cols_existentes = [c for c in cols_ver if c in df_final_t1.columns]
        
        df_show = df_final_t1[cols_existentes].copy()
        df_show["DIAS/FECHAS"] = df_show["DIAS/FECHAS"].dt.strftime("%d-%m-%Y")
        
        st.dataframe(df_show, hide_index=True, use_container_width=True)
        
        # Botón descarga parcial
        st.download_button(
            "📥 Descargar esta vista (CSV)",
            data=df_show.to_csv(index=False).encode('utf-8'),
            file_name="calendario_filtrado.csv",
            mime="text/csv"
        )

# =============================================================================
# TAB 2: COMPARATIVA
# =============================================================================
with tab2:
    st.markdown("## 📊 Comparativa de Carga")
    st.info("💡 Filtros independientes (Vacío = Todos)")

    c2_1, c2_2, c2_3, c2_4 = st.columns(4)
    sel_y2 = c2_1.multiselect("Año", sorted(df_base["DIAS/FECHAS"].dt.year.unique()), key="t2_y", placeholder="Todos")
    sel_c2 = c2_2.multiselect("Coordinadoras", sorted(df_base["COORDINADORA RESPONSABLE"].unique()), key="t2_c", placeholder="Todas")
    sel_m2 = c2_3.multiselect("Modalidad", sorted(df_base["Modalidad_Calc"].unique()), key="t2_m", placeholder="Todas")
    
    # Nuevo filtro de Mes
    meses_disp_t2 = sorted(df_base["Mes"].unique(), key=lambda x: utils.MESES.get(x.lower(), 99)) if "Mes" in df_base.columns else []
    sel_mes2 = c2_4.multiselect("Mes", meses_disp_t2, key="t2_mes", placeholder="Todos")

    # Aplicar filtros
    mask2 = pd.Series(True, index=df_base.index)
    if sel_y2: mask2 &= df_base["DIAS/FECHAS"].dt.year.isin(sel_y2)
    if sel_c2: mask2 &= df_base["COORDINADORA RESPONSABLE"].isin(sel_c2)
    if sel_m2: mask2 &= df_base["Modalidad_Calc"].isin(sel_m2)
    if sel_mes2: mask2 &= df_base["Mes"].isin(sel_mes2)
    
    df_t2 = df_base[mask2].copy()

    if df_t2.empty:
        st.warning("No hay datos.")
    else:
        # Gráficos
        col_bar, col_pie = st.columns(2)
        with col_bar:
            carga = df_t2["COORDINADORA RESPONSABLE"].value_counts().reset_index()
            carga.columns = ["Coordinadora", "Sesiones"]
            fig_c = px.bar(carga, x="Coordinadora", y="Sesiones", color="Coordinadora", text="Sesiones", title="Total Sesiones por Coordinadora")
            st.plotly_chart(charts.update_chart_layout(fig_c), use_container_width=True)
        
        with col_pie:
            dist_dia = df_t2.groupby(["COORDINADORA RESPONSABLE", "Dia_Semana"]).size().reset_index(name="Cant")
            
            # Configuración de gráfico agrupado
            fig_p = px.bar(
                dist_dia, 
                x="COORDINADORA RESPONSABLE", 
                y="Cant", 
                color="Dia_Semana", 
                barmode="group", # Barras agrupadas
                title="Distribución por Día Semana (Comparativa)"
            )
            
            # Gráfico sin contenedor de scroll para asegurar alineación
            st.plotly_chart(charts.update_chart_layout(fig_p), use_container_width=True)

        # Resumen Tabla
        st.markdown("### Resumen de Actividad")
        df_res = resumen_coordinadoras_semana(df_t2)
        st.dataframe(df_res, hide_index=True, use_container_width=True)

# =============================================================================
# TAB 3: GLOBAL
# =============================================================================
with tab3:
    st.markdown("## 🌐 Visión Global")
    
    col3_1, col3_2, col3_3 = st.columns(3)
    sel_y3 = col3_1.multiselect("Año", sorted(df_base["DIAS/FECHAS"].dt.year.unique()), key="t3_y", placeholder="Todos")
    modo_ver = col3_2.radio("Agrupar tiempo por:", ["Mes", "Día Semana"], horizontal=True)
    top_n = col3_3.slider("Top Programas", 3, 20, 10)

    df_t3 = df_base.copy()
    if sel_y3: df_t3 = df_t3[df_t3["DIAS/FECHAS"].dt.year.isin(sel_y3)]

    # Preparar datos
    df_t3["Mes"] = df_t3["DIAS/FECHAS"].dt.to_period("M").astype(str)
    eje_x = "Mes" if modo_ver == "Mes" else "Dia_Semana"
    
    # Ranking
    top_progs = df_t3["PROGRAMA"].value_counts().head(top_n).index
    df_plot = df_t3[df_t3["PROGRAMA"].isin(top_progs)]
    
    data_g = df_plot.groupby([eje_x, "PROGRAMA"]).size().reset_index(name="Sesiones")
    
    # Ordenar días si es necesario
    if modo_ver == "Día Semana":
        dias_ord = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        data_g[eje_x] = pd.Categorical(data_g[eje_x], categories=dias_ord, ordered=True)
        data_g = data_g.sort_values(eje_x)
    else:
        data_g = data_g.sort_values(eje_x)

    fig_g = px.bar(data_g, x=eje_x, y="Sesiones", color="PROGRAMA", title=f"Evolución de Clases (Top {top_n})")
    st.plotly_chart(charts.update_chart_layout(fig_g), use_container_width=True)

    # Choques Globales
    st.markdown("### 🔥 Mapa de Calor: Choques de Coordinación")
    st.caption("Días donde múltiples coordinadoras tienen clases simultáneamente.")
    
    # Filtros locales para el mapa de calor
    c_heat_1, c_heat_2, c_heat_3, c_heat_4, c_heat_5 = st.columns(5)
    
    # Filtro Mes
    # Usamos map con MESES_NOMBRE para asegurar nombres en español consistentes
    meses_nombres = df_t3["DIAS/FECHAS"].dt.month.map(utils.MESES_NOMBRE).unique()
    meses_disp = sorted(meses_nombres, key=lambda x: utils.MESES.get(utils.quitar_acentos(str(x)).lower(), 99))
    sel_mes_heat = c_heat_1.multiselect("Filtrar Mes", meses_disp, key="t3_heat_mes", placeholder="Todos")
    
    # Filtro Día Semana
    dias_heat_disp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    sel_dia_heat = c_heat_2.multiselect("Filtrar Día Semana", dias_heat_disp, key="t3_heat_dia", placeholder="Todos")

    # Filtro Sede
    sedes_heat_disp = sorted(df_t3["SEDE"].unique())
    sel_sede_heat = c_heat_3.multiselect("Filtrar Sede", sedes_heat_disp, key="t3_heat_sede", placeholder="Todas")
    
    # Filtro Coordinadora
    coords_heat_disp = sorted(df_t3["COORDINADORA RESPONSABLE"].unique())
    sel_coord_heat = c_heat_4.multiselect("Filtrar Coord.", coords_heat_disp, key="t3_heat_coord", placeholder="Todas")

    # Filtro Rango Fechas
    min_date = df_t3["DIAS/FECHAS"].min().date()
    max_date = df_t3["DIAS/FECHAS"].max().date()
    sel_date_range = c_heat_5.date_input("Rango de Fechas", [min_date, max_date], key="t3_heat_date")
    
    # Aplicar filtros
    df_heat = df_t3.copy()
    if sel_mes_heat:
        df_heat = df_heat[df_heat["DIAS/FECHAS"].dt.month_name().isin(sel_mes_heat)]
    if sel_dia_heat:
        df_heat = df_heat[df_heat["Dia_Semana"].isin(sel_dia_heat)]
    if sel_sede_heat:
        df_heat = df_heat[df_heat["SEDE"].isin(sel_sede_heat)]
    if sel_coord_heat:
        df_heat = df_heat[df_heat["COORDINADORA RESPONSABLE"].isin(sel_coord_heat)]
    if len(sel_date_range) == 2:
        df_heat = df_heat[
            (df_heat["DIAS/FECHAS"].dt.date >= sel_date_range[0]) & 
            (df_heat["DIAS/FECHAS"].dt.date <= sel_date_range[1])
        ]
    
    choques = df_heat.groupby("DIAS/FECHAS")["COORDINADORA RESPONSABLE"].nunique().reset_index(name="N_Coords")
    choques = choques[choques["N_Coords"] > 1]
    
    if not choques.empty:
        choques["Fecha"] = choques["DIAS/FECHAS"].dt.strftime("%d-%m-%Y")
        fig_ch = px.scatter(choques, x="Fecha", y="N_Coords", size="N_Coords", color="N_Coords", 
                            color_continuous_scale="Reds", range_color=[0, 6], title="Días con múltiples coordinadoras")
        st.plotly_chart(charts.update_chart_layout(fig_ch), use_container_width=True)
    else:
        st.info("No se detectaron días con múltiples coordinadoras.")

# =============================================================================
# TAB 4: RESUMEN PROGRAMAS (CON CASCADA SIMPLE)
# =============================================================================
with tab4:
    st.markdown("## 🧾 Estado de Programas")
    
    with st.expander("🔍 Filtros de Programa", expanded=True):
        f1, f2, f3 = st.columns(3)
        # Cascada simplificada
        s_y4 = f1.multiselect("Año", sorted(df_base["DIAS/FECHAS"].dt.year.unique()), key="t4_y", placeholder="Todos")
        d4_1 = df_base[df_base["DIAS/FECHAS"].dt.year.isin(s_y4)] if s_y4 else df_base
        
        s_c4 = f2.multiselect("Coordinadora", sorted(d4_1["COORDINADORA RESPONSABLE"].unique()), key="t4_c", placeholder="Todas")
        d4_2 = d4_1[d4_1["COORDINADORA RESPONSABLE"].isin(s_c4)] if s_c4 else d4_1
        
        s_p4 = f3.multiselect("Programa", sorted(d4_2["PROGRAMA"].unique()), key="t4_p", placeholder="Todos")
        df_final_t4 = d4_2[d4_2["PROGRAMA"].isin(s_p4)] if s_p4 else d4_2

    if df_final_t4.empty:
        st.warning("No hay datos.")
    else:
        hoy = datetime.now()
        stats = df_final_t4.groupby("PROGRAMA").agg(
            Inicio=("DIAS/FECHAS", "min"),
            Fin=("DIAS/FECHAS", "max"),
            Sesiones=("DIAS/FECHAS", "count"),
            Sum_Horas=("Duracion_Horas", "sum"),
            Coords=("COORDINADORA RESPONSABLE", lambda x: ", ".join(sorted(x.unique())))
        ).reset_index()

        # Calcular Avance %
        def get_avance(r):
            if pd.isna(r["Inicio"]) or pd.isna(r["Fin"]): return 0
            total = (r["Fin"] - r["Inicio"]).days
            if total <= 0: return 100
            elapsed = (hoy - r["Inicio"]).days
            return 100 if elapsed >= total else max(0, int((elapsed/total)*100))

        stats["% Avance"] = stats.apply(get_avance, axis=1)

        # Mostrar tabla pro
        st.dataframe(
            stats.sort_values("% Avance", ascending=False),
            column_config={
                "% Avance": st.column_config.ProgressColumn(
                    "Progreso Temporal", format="%d%%", min_value=0, max_value=100
                ),
                "Inicio": st.column_config.DateColumn("Inicio", format="DD/MM/YYYY"),
                "Fin": st.column_config.DateColumn("Fin", format="DD/MM/YYYY"),
                "Sesiones": st.column_config.NumberColumn("Nº Clases"),
                "Sum_Horas": st.column_config.NumberColumn("Total Horas", format="%.1f hrs")
            },
            hide_index=True,
            use_container_width=True
        )

        # Detalle de Asignaturas
        st.markdown("---")
        st.markdown("### 📅 Detalle de Asignaturas")
        
        if "ASIGNATURA" in df_final_t4.columns:
            # Filtros locales para esta tabla
            c_asig_1, c_asig_2 = st.columns(2)
            
            # Filtro Coordinadora
            coords_asig = sorted(df_final_t4["COORDINADORA RESPONSABLE"].unique())
            sel_coord_asig = c_asig_1.multiselect(
                "Filtrar Coordinadora", 
                coords_asig, 
                key="t4_asig_coord", 
                placeholder="Todas"
            )
            
            df_asig_filt = df_final_t4.copy()
            if sel_coord_asig:
                df_asig_filt = df_asig_filt[df_asig_filt["COORDINADORA RESPONSABLE"].isin(sel_coord_asig)]
            
            # Filtro Programa (dependiente)
            progs_asig = sorted(df_asig_filt["PROGRAMA"].unique())
            sel_prog_asig = c_asig_2.multiselect(
                "Filtrar Programa", 
                progs_asig, 
                key="t4_asig_prog", 
                placeholder="Todos"
            )
            
            if sel_prog_asig:
                df_asig_filt = df_asig_filt[df_asig_filt["PROGRAMA"].isin(sel_prog_asig)]

            asignaturas = df_asig_filt.groupby(["PROGRAMA", "ASIGNATURA"]).agg(
                Inicio=("DIAS/FECHAS", "min"),
                Fin=("DIAS/FECHAS", "max")
            ).reset_index()
            
            st.dataframe(
                asignaturas,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Inicio": st.column_config.DateColumn("Inicio", format="DD/MM/YYYY"),
                    "Fin": st.column_config.DateColumn("Fin", format="DD/MM/YYYY")
                }
            )
        else:
            st.info("No se encontró la columna 'ASIGNATURA' en los datos.")

# =============================================================================
# TAB 5: CALIDAD & SEDE
# =============================================================================
with tab5:
    st.markdown("## 🏫 Sede, Modalidad y Calidad")
    
    # Filtros simples
    f5_1, f5_2 = st.columns(2)
    sy5 = f5_1.multiselect("Año", sorted(df_base["DIAS/FECHAS"].dt.year.unique()), key="t5_y", placeholder="Todos")
    df_t5 = df_base[df_base["DIAS/FECHAS"].dt.year.isin(sy5)] if sy5 else df_base

    if df_t5.empty:
        st.warning("No hay datos.")
    else:
        cm, cs = st.columns(2)
        with cm:
            st.markdown("### Modalidad")
            df_m = resumen_modalidad(df_t5)
            if not df_m.empty:
                fig_m = px.pie(df_m, names="Modalidad_Calc", values="Sesiones", hole=0.4)
                st.plotly_chart(charts.update_chart_layout(fig_m), use_container_width=True)
                st.dataframe(df_m, hide_index=True, use_container_width=True)
        
        with cs:
            st.markdown("### Sede")
            df_s = resumen_sede(df_t5)
            if not df_s.empty:
                fig_s = px.bar(df_s, x="SEDE", y="Sesiones", color="Sesiones")
                st.plotly_chart(charts.update_chart_layout(fig_s), use_container_width=True)
                st.dataframe(df_s, hide_index=True, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🧹 Auditoría de Datos (Valores Faltantes)")
        df_q = resumen_calidad_datos(df_base) # Usamos la base completa para auditoría
        st.dataframe(df_q, hide_index=True, use_container_width=True)

# =============================================================================
# TAB 6: GESTIÓN (PROTEGIDO)
# =============================================================================
with tab_gestion:
    st.markdown("## 🔒 Gestión y Carga Laboral")
    
    password = st.text_input("Ingrese Contraseña de Administrador", type="password", key="gestion_pwd")
    
    if password == "admin":
        st.success("Acceso Concedido")
        
        # Filtro de Año independiente para esta pestaña
        years_gestion = sorted(df_base["DIAS/FECHAS"].dt.year.unique())
        sel_year_g = st.multiselect("Filtrar por Año", years_gestion, key="tg_year", default=years_gestion)
        
        if sel_year_g:
            df_g = df_base[df_base["DIAS/FECHAS"].dt.year.isin(sel_year_g)].copy()
            
            # =============================================================================
            # MATRIZ DE SESIONES MENSUALES
            # =============================================================================
            st.markdown("### 🗓️ Matriz de Sesiones Mensuales")
            st.caption("Visualización de la carga de sesiones por mes y coordinadora.")

            # Mapeo de meses (para evitar problemas de idioma local)
            mapa_meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }

            if not df_g.empty:
                # Preparar datos para la matriz
                df_matrix = df_g.copy()
                
                df_matrix["Mes_Num"] = df_matrix["DIAS/FECHAS"].dt.month
                df_matrix["Mes"] = df_matrix["Mes_Num"].map(mapa_meses)
                
                # Compactar nombres de programas
                def compactar_nombre(nombre):
                    n = str(nombre).upper()
                    reemplazos = {
                        "MAGISTER": "MAG.", "DIPLOMADO": "DIPL.", "DIRECCION": "DIR.",
                        "GESTION": "GEST.", "NEGOCIOS": "NEG.", "PRESENCIAL": "PRES.",
                        "CORPORATIVO": "CORP.", "ORGANIZACIONES": "ORG.", "MARKETING": "MKT.",
                        "MANAGEMENT": "MGMT.", "SOSTENIBLES": "SOST.", "INNOVACION": "INNOV."
                    }
                    for k, v in reemplazos.items():
                        n = n.replace(k, v)
                    # Truncar si es muy largo
                    if len(n) > 40:
                        n = n[:37] + "..."
                    return n

                df_matrix["PROGRAMA"] = df_matrix["PROGRAMA"].apply(compactar_nombre)

                # Pivotar: Index=Coord+Programa, Columns=Mes, Values=Count
                matrix = df_matrix.pivot_table(
                    index=["COORDINADORA RESPONSABLE", "PROGRAMA"], 
                    columns="Mes", 
                    values="DIAS/FECHAS", 
                    aggfunc="count",
                    fill_value=0
                )
                
                # Ordenar columnas de meses cronológicamente
                meses_orden = [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ]
                cols_existentes = [m for m in meses_orden if m in matrix.columns]
                matrix = matrix[cols_existentes]
                
                # Mostrar con gradiente (heatmap)
                st.dataframe(
                    matrix.style.background_gradient(cmap="RdYlGn_r", axis=None, vmin=0, vmax=20), # Rojo=Alto, Verde=Bajo
                    use_container_width=True
                )
            else:
                st.info("No hay datos disponibles para el año seleccionado.")

            # =============================================================================
            # CÁLCULO DE CARGA LABORAL
            # =============================================================================
            st.markdown("---")
            st.markdown("### ⚖️ Carga Laboral (Puntaje)")
            st.caption("Cálculo basado en Factor Sesiones (Sesiones/4) x Factor Alumnos.")

            # Filtro de Mes para Carga Laboral
            # Usar el mismo mapeo para el selector
            df_g["Mes_Nombre"] = df_g["DIAS/FECHAS"].dt.month.map(mapa_meses)
            # Ordenar meses disponibles por número de mes
            meses_disponibles_num = sorted(df_g["DIAS/FECHAS"].dt.month.unique())
            meses_carga = ["Todos los meses"] + [mapa_meses[m] for m in meses_disponibles_num]
            
            sel_mes_carga = st.selectbox("Seleccionar Mes para Cálculo", meses_carga, key="tg_carga_mes")

            if sel_mes_carga:
                if sel_mes_carga == "Todos los meses":
                    df_carga = df_g.copy()
                else:
                    # Filtrar por mes (usando el nombre mapeado)
                    df_carga = df_g[df_g["Mes_Nombre"] == sel_mes_carga].copy()
                
                if not df_carga.empty:
                    # Buscar columna exacta o parecida
                    col_alumnos = "Nº ALUMNOS"
                    if col_alumnos not in df_carga.columns:
                        # Intentar buscar algo similar si no está la exacta
                        col_alumnos = next((c for c in df_carga.columns if "ALUMNO" in c.upper()), None)
                    
                    # Si no existe, crearla con 0 para que el cálculo no falle, pero avisar
                    if not col_alumnos:
                        df_carga["Nº ALUMNOS"] = 0
                        col_alumnos = "Nº ALUMNOS"
                        st.warning("⚠️ No se encontró la columna 'Nº ALUMNOS'. Se asume 0 alumnos (Factor 1.0) y se marca como 'Por definir'.")

                    # Agrupar por Coordinadora y Programa
                    # Asumimos que el número de alumnos es constante por programa, tomamos el max
                    # Rellenar NaN con 0
                    df_carga[col_alumnos] = df_carga[col_alumnos].fillna(0)
                    
                    carga_prog = df_carga.groupby(["COORDINADORA RESPONSABLE", "PROGRAMA"]).agg(
                        Sesiones=("DIAS/FECHAS", "count"),
                        Alumnos=(col_alumnos, "max")
                    ).reset_index()
                    
                    # 1. Factor Sesiones
                    carga_prog["Factor_Sesiones"] = carga_prog["Sesiones"] / 4
                    
                    # 2. Factor Alumnos
                    def get_factor_alumnos(n):
                        if n == 0: return 1.0 # Default si es 0 o Por definir
                        if n < 20: return 1.0
                        if n < 30: return 1.2
                        if n < 40: return 1.4
                        if n < 49: return 1.7 # Ajustado a <49 según requerimiento (40-49)
                        return 2.0
                    
                    carga_prog["Factor_Alumnos"] = carga_prog["Alumnos"].apply(get_factor_alumnos)
                    
                    # 3. Puntaje Final
                    carga_prog["Puntaje"] = carga_prog["Factor_Sesiones"] * carga_prog["Factor_Alumnos"]
                    
                    # Resumen por Coordinadora
                    resumen_carga = carga_prog.groupby("COORDINADORA RESPONSABLE")["Puntaje"].sum().reset_index()
                    resumen_carga = resumen_carga.sort_values("Puntaje", ascending=False)
                    
                    # Mostrar Tabla Resumen
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.dataframe(
                            resumen_carga,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Puntaje": st.column_config.NumberColumn("Puntaje Total", format="%.2f"),
                                "COORDINADORA RESPONSABLE": "Coordinadora"
                            }
                        )
                    with c2:
                        avg_score = resumen_carga["Puntaje"].mean()
                        st.metric("Promedio Gestión", f"{avg_score:.2f}")
                        
                    # Detalle Desplegable
                    with st.expander("Ver Detalle por Programa"):
                        # Filtro por Coordinadora
                        coords_detalle = sorted(carga_prog["COORDINADORA RESPONSABLE"].unique())
                        sel_coord_det = st.multiselect("Filtrar por Coordinadora", coords_detalle, key="filter_coord_detail")
                        
                        df_show_prog = carga_prog.copy()
                        if sel_coord_det:
                            df_show_prog = df_show_prog[df_show_prog["COORDINADORA RESPONSABLE"].isin(sel_coord_det)]

                        # Marcar visualmente si alumnos es 0
                        df_show_prog["Estado Alumnos"] = df_show_prog["Alumnos"].apply(lambda x: "Por definir" if x == 0 else "Ok")
                        
                        st.dataframe(
                            df_show_prog,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Factor_Sesiones": st.column_config.NumberColumn("Fac. Sesiones", format="%.2f"),
                                "Factor_Alumnos": st.column_config.NumberColumn("Fac. Alumnos", format="%.1f"),
                                "Puntaje": st.column_config.NumberColumn("Puntaje", format="%.2f"),
                                "Alumnos": st.column_config.NumberColumn("Nº Alumnos"),
                                "Estado Alumnos": st.column_config.TextColumn("Estado", width="small")
                            }
                        )

                    # =============================================================================
                    # SIMULADOR DE BALANCEO DE CARGA
                    # =============================================================================
                    st.markdown("---")
                    st.subheader("⚖️ Simulador de Balanceo de Carga")
                    st.info("💡 Los cambios aquí son temporales (simulación) y no afectan el archivo original.")

                    # Inicializar estado de simulación
                    if "sim_cambios" not in st.session_state:
                        st.session_state["sim_cambios"] = {} # {Programa: Nueva_Coord}

                    # Interfaz de Reasignación
                    col_sim1, col_sim2, col_sim3 = st.columns(3)
                    
                    # Lista de programas disponibles en el mes seleccionado
                    progs_mes = sorted(df_carga["PROGRAMA"].unique())
                    coords_disp = sorted(df_base["COORDINADORA RESPONSABLE"].unique())

                    with col_sim1:
                        prog_sel = st.selectbox("Seleccionar Programa a Reasignar", progs_mes, key="sim_prog")
                    
                    # Obtener coordinadora actual (considerando simulación previa)
                    coord_actual_real = df_carga[df_carga["PROGRAMA"] == prog_sel]["COORDINADORA RESPONSABLE"].iloc[0]
                    coord_actual_sim = st.session_state["sim_cambios"].get(prog_sel, coord_actual_real)
                    
                    with col_sim2:
                        st.text_input("Coordinadora Actual (Simulada)", value=coord_actual_sim, disabled=True)
                    
                    with col_sim3:
                        nueva_coord = st.selectbox("Asignar a Nueva Coordinadora", coords_disp, key="sim_new_coord")

                    if st.button("🔄 Aplicar Cambio (Simulación)"):
                        st.session_state["sim_cambios"][prog_sel] = nueva_coord
                        st.success(f"Programa '{prog_sel}' reasignado a '{nueva_coord}' en la simulación.")
                        st.rerun()

                    # Botón Reset
                    if st.session_state["sim_cambios"]:
                        if st.button("🗑️ Borrar Simulación"):
                            st.session_state["sim_cambios"] = {}
                            st.rerun()

                    # --- CÁLCULO SIMULADO ---
                    if st.session_state["sim_cambios"]:
                        # Crear copia para simulación
                        df_sim = df_carga.copy()
                        
                        # Aplicar cambios
                        for p, c in st.session_state["sim_cambios"].items():
                            df_sim.loc[df_sim["PROGRAMA"] == p, "COORDINADORA RESPONSABLE"] = c
                        
                        # Recalcular métricas simuladas
                        sim_prog = df_sim.groupby(["COORDINADORA RESPONSABLE", "PROGRAMA"]).agg(
                            Sesiones=("DIAS/FECHAS", "count"),
                            Alumnos=(col_alumnos, "max")
                        ).reset_index()
                        
                        sim_prog["Factor_Sesiones"] = sim_prog["Sesiones"] / 4
                        sim_prog["Factor_Alumnos"] = sim_prog["Alumnos"].apply(get_factor_alumnos)
                        sim_prog["Puntaje"] = sim_prog["Factor_Sesiones"] * sim_prog["Factor_Alumnos"]
                        
                        resumen_sim = sim_prog.groupby("COORDINADORA RESPONSABLE")["Puntaje"].sum().reset_index()
                        
                        # Comparativa
                        st.markdown("#### 📊 Impacto de la Simulación")
                        
                        # Merge Real vs Simulado
                        comparativa = pd.merge(
                            resumen_carga[["COORDINADORA RESPONSABLE", "Puntaje"]],
                            resumen_sim[["COORDINADORA RESPONSABLE", "Puntaje"]],
                            on="COORDINADORA RESPONSABLE",
                            how="outer",
                            suffixes=("_Actual", "_Simulado")
                        ).fillna(0)
                        
                        comparativa["Diferencia"] = comparativa["Puntaje_Simulado"] - comparativa["Puntaje_Actual"]
                        comparativa = comparativa.sort_values("Puntaje_Simulado", ascending=False)
                        
                        st.dataframe(
                            comparativa,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Puntaje_Actual": st.column_config.NumberColumn("Carga Actual", format="%.2f"),
                                "Puntaje_Simulado": st.column_config.NumberColumn("Carga Simulada", format="%.2f"),
                                "Diferencia": st.column_config.NumberColumn(
                                    "Variación", 
                                    format="%.2f",
                                    help="Positivo: Aumenta carga | Negativo: Disminuye carga"
                                )
                            }
                        )

                else:
                    st.info(f"No hay datos para el mes de {sel_mes_carga}.")
            
            # =============================================================================
            # DISTRIBUCIÓN SEMANAL (GRÁFICO DE ARAÑA)
            # =============================================================================
            st.markdown("---")
            st.subheader("🕸️ Distribución Semanal de Carga")
            st.caption("Visualiza qué días de la semana concentran más clases según los filtros seleccionados.")

            # Filtros específicos para el gráfico de araña
            c_rad1, c_rad2, c_rad3, c_rad4 = st.columns(4)
            
            # 1. Coordinadora
            coords_rad = sorted(df_g["COORDINADORA RESPONSABLE"].unique())
            sel_coord_rad = c_rad1.multiselect("Coordinadora", coords_rad, key="rad_coord", placeholder="Todas")
            
            # Filtrar df base para siguientes opciones
            df_rad = df_g.copy()
            if sel_coord_rad:
                df_rad = df_rad[df_rad["COORDINADORA RESPONSABLE"].isin(sel_coord_rad)]
            
            # 2. Mes (Usamos el mapeo existente)
            df_rad["Mes_Nombre"] = df_rad["DIAS/FECHAS"].dt.month.map(mapa_meses)
            meses_rad = sorted(df_rad["Mes_Nombre"].unique(), key=lambda x: list(mapa_meses.values()).index(x) if x in mapa_meses.values() else 99)
            sel_mes_rad = c_rad2.multiselect("Mes", meses_rad, key="rad_mes", placeholder="Todos")
            
            if sel_mes_rad:
                df_rad = df_rad[df_rad["Mes_Nombre"].isin(sel_mes_rad)]
                
            # 3. Sede
            sedes_rad = sorted(df_rad["SEDE"].unique())
            sel_sede_rad = c_rad3.multiselect("Sede", sedes_rad, key="rad_sede", placeholder="Todas")
            
            if sel_sede_rad:
                df_rad = df_rad[df_rad["SEDE"].isin(sel_sede_rad)]
                
            # 4. Programa
            progs_rad = sorted(df_rad["PROGRAMA"].unique())
            sel_prog_rad = c_rad4.multiselect("Programa", progs_rad, key="rad_prog", placeholder="Todos")
            
            if sel_prog_rad:
                df_rad = df_rad[df_rad["PROGRAMA"].isin(sel_prog_rad)]
            
            if df_rad.empty:
                st.warning("No hay datos con los filtros seleccionados.")
            else:
                # Layout de 3 columnas para gráficos
                col_r1, col_r2, col_r3 = st.columns(3)
                
                # Estilo común para los gráficos de araña
                radar_style = dict(
                    line_close=True,
                    color_discrete_sequence=["#FF4B4B"], # Color rojo intenso
                    markers=True,
                )

                # 1. Gráfico Día
                with col_r1:
                    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                    conteo_dias = df_rad["Dia_Semana"].value_counts().reindex(dias_orden, fill_value=0).reset_index()
                    conteo_dias.columns = ["Dia", "Clases"]
                    
                    fig_rad = px.line_polar(
                        conteo_dias, r='Clases', theta='Dia', 
                        title="<b>Por Día Semana</b>", 
                        line_close=True,
                        color_discrete_sequence=["black"],
                        markers=True # Enable markers for hover
                    )
                    fig_rad.update_traces(fill='toself', line=dict(color='black', width=3))
                    st.plotly_chart(charts.update_chart_layout(fig_rad), use_container_width=True)

                # 2. Gráfico Sede
                with col_r2:
                    conteo_sede = df_rad["SEDE"].value_counts().reset_index()
                    conteo_sede.columns = ["Sede", "Clases"]
                    
                    fig_sede = px.line_polar(
                        conteo_sede, r='Clases', theta='Sede', 
                        title="<b>Por Sede</b>", 
                        line_close=True,
                        color_discrete_sequence=["black"],
                        markers=True # Enable markers for hover
                    )
                    fig_sede.update_traces(fill='toself', line=dict(color='black', width=3))
                    st.plotly_chart(charts.update_chart_layout(fig_sede), use_container_width=True)

                # 3. Gráfico Modalidad
                with col_r3:
                    conteo_mod = df_rad["Modalidad_Calc"].value_counts().reset_index()
                    conteo_mod.columns = ["Modalidad", "Clases"]
                    
                    fig_mod = px.line_polar(
                        conteo_mod, r='Clases', theta='Modalidad', 
                        title="<b>Por Modalidad</b>", 
                        line_close=True,
                        color_discrete_sequence=["black"],
                        markers=True # Enable markers for hover
                    )
                    fig_mod.update_traces(fill='toself', line=dict(color='black', width=3))
                    st.plotly_chart(charts.update_chart_layout(fig_mod), use_container_width=True)

                # Detalle Dinámico por Día
                st.markdown("##### 📅 Detalle por Día Semana")
                
                # Calcular día con más carga para ponerlo por defecto
                if not df_rad.empty:
                    dias_counts = df_rad["Dia_Semana"].value_counts()
                    dia_max_carga = dias_counts.idxmax()
                    
                    # Ordenar días para el selector
                    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                    dias_disponibles = sorted(df_rad["Dia_Semana"].unique(), key=lambda x: dias_orden.index(x) if x in dias_orden else 99)
                    
                    # Selector de día
                    idx_def = dias_disponibles.index(dia_max_carga) if dia_max_carga in dias_disponibles else 0
                    sel_dia_det = st.selectbox("Seleccionar Día para ver detalle:", dias_disponibles, index=idx_def, key="sel_dia_detalle_rad")
                    
                    # Filtrar y mostrar
                    df_dia_det = df_rad[df_rad["Dia_Semana"] == sel_dia_det].copy()
                    coords_dia = sorted(df_dia_det["COORDINADORA RESPONSABLE"].unique())
                    
                    if not df_dia_det.empty:
                        st.success(f"**Coordinadoras con turno en {sel_dia_det}:** {', '.join(coords_dia)}")
                        
                        # Ordenar por fecha
                        df_dia_det = df_dia_det.sort_values("DIAS/FECHAS")
                        df_dia_det["Fecha"] = df_dia_det["DIAS/FECHAS"].dt.strftime("%d-%m-%Y")
                        
                        st.dataframe(
                            df_dia_det[["Fecha", "COORDINADORA RESPONSABLE", "PROGRAMA", "SEDE"]],
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "COORDINADORA RESPONSABLE": "Coordinadora",
                                "PROGRAMA": "Programa",
                                "SEDE": "Sede"
                            }
                        )
                    else:
                        st.info(f"No hay clases para {sel_dia_det} con los filtros actuales.")
                else:
                    st.info("No hay datos para mostrar detalle.")
        else:
            st.info("Selecciona un año para ver la información.")
    elif password:
        st.error("Contraseña incorrecta")
    else:
        st.info("🔒 Esta sección está protegida. Ingrese la contraseña para continuar.")

# =============================================================================
# TAB 7: VALIDACIONES (CHOQUES DE HORARIO)
# =============================================================================
with tab_validaciones:
    st.markdown("## 🕵️ Detección de Conflictos de Horario")
    st.write("Esta sección busca automáticamente si un mismo **Profesor** tiene dos clases asignadas al mismo tiempo.")
    
    # Verificar si tenemos datos de horas
    cols_horas = ["HORA_INICIO", "HORA_FIN"]
    if not all(c in df_base.columns for c in cols_horas):
        st.warning("⚠️ No se detectaron columnas de hora ('HORA INICIO', 'HORA FIN') en el archivo. No es posible validar choques.")
    else:
        # Preparar datos
        df_val = df_base.dropna(subset=["HORA_INICIO", "HORA_FIN", "PROFESOR"]).copy()
        
        # Crear datetimes completos para comparar
        try:
            # Función auxiliar para combinar fecha y hora
            def combine_dt(row, col_hora):
                t = row[col_hora]
                if pd.isna(t): return pd.NaT
                # Si es string, intentar parsear
                if isinstance(t, str):
                    try: t = datetime.strptime(t, "%H:%M:%S").time()
                    except: 
                        try: t = datetime.strptime(t, "%H:%M").time()
                        except: return pd.NaT
                
                # Validación extra para fecha
                fecha = row["DIAS/FECHAS"]
                if pd.isna(fecha): return pd.NaT
                
                try:
                    return datetime.combine(fecha.date(), t)
                except:
                    return pd.NaT

            df_val["start_dt"] = df_val.apply(lambda x: combine_dt(x, "HORA_INICIO"), axis=1)
            df_val["end_dt"] = df_val.apply(lambda x: combine_dt(x, "HORA_FIN"), axis=1)
            
            df_val = df_val.dropna(subset=["start_dt", "end_dt"])
            
            choques = []
            
            # Agrupar por Profesor y buscar solapamientos
            for prof, sub in df_val.groupby("PROFESOR"):
                if prof == "SIN PROFESOR" or prof == "POR DEFINIR": continue
                
                sub = sub.sort_values("start_dt")
                # Iterar
                for i in range(len(sub) - 1):
                    curr = sub.iloc[i]
                    next_row = sub.iloc[i+1]
                    
                    # Chequear overlap: Start_Next < End_Curr
                    if next_row["start_dt"] < curr["end_dt"]:
                        choques.append({
                            "Profesor": prof,
                            "Fecha": curr["DIAS/FECHAS"].strftime("%d-%m-%Y"),
                            "Conflicto": f"{curr['PROGRAMA']} ({curr['HORA_INICIO']} - {curr['HORA_FIN']}) vs {next_row['PROGRAMA']} ({next_row['HORA_INICIO']} - {next_row['HORA_FIN']})"
                        })
            
            if choques:
                st.error(f"⚠️ Se encontraron {len(choques)} conflictos de horario.")
                st.dataframe(pd.DataFrame(choques), use_container_width=True)
            else:
                st.success("✅ No se detectaron choques de horario para los profesores asignados.")
                
        except Exception as e:
            st.error(f"Error al procesar las fechas/horas para validación: {e}")

    # =============================================================================
    # VALIDACIÓN: COORDINADORAS EN MÚLTIPLES SEDES
    # =============================================================================
    st.markdown("---")
    st.subheader("🌍 Coordinadoras en Múltiples Sedes")
    st.caption("Detecta coordinadoras que tienen asignadas clases en más de una sede distinta.")

    if "SEDE" in df_base.columns and "COORDINADORA RESPONSABLE" in df_base.columns:
        # Agrupar por coordinadora y contar sedes únicas
        multi_sede = df_base.groupby("COORDINADORA RESPONSABLE")["SEDE"].unique().reset_index()
        multi_sede["Cantidad_Sedes"] = multi_sede["SEDE"].apply(len)
        multi_sede["Sedes"] = multi_sede["SEDE"].apply(lambda x: ", ".join(sorted(x)))
        
        # Filtrar las que tienen > 1 sede
        multi_sede_filt = multi_sede[multi_sede["Cantidad_Sedes"] > 1].sort_values("Cantidad_Sedes", ascending=False)
        
        if not multi_sede_filt.empty:
            st.warning(f"⚠️ Se encontraron {len(multi_sede_filt)} coordinadoras gestionando múltiples sedes.")
            st.dataframe(
                multi_sede_filt[["COORDINADORA RESPONSABLE", "Cantidad_Sedes", "Sedes"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "COORDINADORA RESPONSABLE": "Coordinadora",
                    "Cantidad_Sedes": st.column_config.NumberColumn("Nº Sedes"),
                    "Sedes": "Sedes Asignadas"
                }
            )
        else:
            st.success("✅ Cada coordinadora está asignada a una única sede.")
    else:
        st.info("No se encontró información de Sede o Coordinadora para realizar esta validación.")

# (Auto-run block removed)
