import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestor Académico Pro", layout="wide", page_icon="📅")

# --- ESTILOS CSS PARA MEJORAR VISUALIZACIÓN ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #d6d6d6;
    }
    </style>
""", unsafe_allow_html=True)


import pandas as pd
import streamlit as st

# -----------------------------------------------------
# 1. COLOCA AQUÍ TU LINK DIRECTO DE ONEDRIVE
#    Ejemplo: "https://onedrive.live.com/download?cid=XXX&resid=YYY&authkey=ZZZ"
# -----------------------------------------------------
onedrive_url = https://alumnosuaicl-my.sharepoint.com/:x:/g/personal/javier_silva_c_uai_cl/EW6UyrrQQdtOj-lSMWzmS7ABNWxDZ4BbXiCd0NIkzjf5Pg?e=3GHCUQ

# -----------------------------------------------------
# 2. FUNCIÓN PARA CARGAR AUTOMÁTICAMENTE EL EXCEL
#    Se refresca sola cada 60 segundos (puedes cambiarlo)
# -----------------------------------------------------
@st.cache_data(ttl=60)
def cargar_excel():
    return pd.read_excel(onedrive_url)

# -----------------------------------------------------
# 3. CARGAR AUTOMÁTICAMENTE EL ARCHIVO DESDE ONEDRIVE
# -----------------------------------------------------
try:
    df = cargar_excel()
except Exception as e:
    st.error("❌ Error al cargar el archivo desde OneDrive.")
    st.error(str(e))
    st.stop()


# --- FUNCIÓN PARA CARGAR DATOS ---
@st.cache_data
def load_data(file_or_path):
    try:
        # Si es un string (ruta), leer desde ahí
        if isinstance(file_or_path, str):
            if file_or_path.endswith('.xlsx') or file_or_path.endswith('.xls'):
                df = pd.read_excel(file_or_path)
            else:
                df = pd.read_csv(file_or_path)
        # Si es un objeto archivo (UploadedFile)
        else:
            if file_or_path.name.endswith('.xlsx') or file_or_path.name.endswith('.xls'):
                df = pd.read_excel(file_or_path)
            else:
                df = pd.read_csv(file_or_path)
        
        # Limpieza de nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Validar que existan las columnas esenciales
        columnas_requeridas = ['COORDINADORA RESPONSABLE', 'DIAS/FECHAS']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            st.error(f"El archivo no contiene las columnas requeridas: {', '.join(columnas_faltantes)}")
            return None
        
        # Filtrar filas vacías clave
        df = df.dropna(subset=['COORDINADORA RESPONSABLE', 'DIAS/FECHAS'])
        
        # Convertir fecha
        df['DIAS/FECHAS'] = pd.to_datetime(df['DIAS/FECHAS'], errors='coerce')
        
        # Normalizar textos (solo si las columnas existen)
        df['COORDINADORA RESPONSABLE'] = df['COORDINADORA RESPONSABLE'].str.upper().str.strip()
        
        if 'SEDE' in df.columns:
            df['SEDE'] = df['SEDE'].fillna('ONLINE/OTRO').str.upper().str.strip()
        else:
            df['SEDE'] = 'ONLINE/OTRO'
            
        if 'PROGRAMA' in df.columns:
            df['PROGRAMA'] = df['PROGRAMA'].fillna('Sin Programa').str.upper().str.strip()
        else:
            df['PROGRAMA'] = 'Sin Programa'
            
        if 'DIA SEMANA' in df.columns:
            df['DIA SEMANA'] = df['DIA SEMANA'].fillna('-').str.upper()
        else:
            df['DIA SEMANA'] = '-'
        
        # Crear una columna combinada para el Tooltip del gráfico (solo si las columnas existen)
        if all(col in df.columns for col in ['PROGRAMA', 'HORARIO', 'ASIGNATURA']):
            df['DETALLE_CLASE'] = (
            "<b>" + df['PROGRAMA'] + "</b><br>" +
            "⏰ " + df['HORARIO'].astype(str) + "<br>" +
            "📚 " + df['ASIGNATURA'].astype(str)
        )
        
        return df
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None

# --- GESTIÓN DE CONFIGURACIÓN (ONEDRIVE) ---
import json
import os

CONFIG_FILE = 'config_onedrive.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'onedrive_path': path}, f)

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Dashboard de Gestión Académica")
st.markdown("---")

# SIDEBAR
with st.sidebar:
    st.header("📂 Configuración")
    
    # 1. Carga Manual
    uploaded_file = st.file_uploader("Sube tu archivo CSV/Excel (Prioritario)", type=["csv", "xlsx"])
    
    st.markdown("---")
    
    # 2. Configuración Automática (OneDrive)
    config = load_config()
    saved_path = config.get('onedrive_path', '')
    
    with st.expander("⚙️ Configuración Ruta Automática (OneDrive)", expanded=not bool(saved_path)):
        st.write("Configura una ruta local para cargar el archivo automáticamente al iniciar.")
        input_path = st.text_input("Ruta absoluta del archivo:", value=saved_path)
        if st.button("Guardar Ruta"):
            if os.path.exists(input_path):
                save_config(input_path)
                st.success("¡Ruta guardada! Recarga la página.")
                st.rerun()
            else:
                st.error("La ruta no existe. Verifica e intenta de nuevo.")
    
    # Lógica de Selección de Archivo
    file_to_process = None
    source_msg = ""
    
    if uploaded_file is not None:
        file_to_process = uploaded_file
        source_msg = "Archivo cargado manualmente."
    elif saved_path and os.path.exists(saved_path):
        file_to_process = saved_path
        source_msg = f"✅ Archivo cargado automáticamente desde: `{os.path.basename(saved_path)}`"
        st.success(source_msg)
    elif saved_path:
        st.warning(f"⚠️ No se encontró el archivo en la ruta guardada: {saved_path}")

    st.markdown("---")
    st.info("El sistema detecta automáticamente duplicidad de programas y genera cronogramas comparativos.")
    
    st.markdown("---")
    with st.expander("🚀 Sugerencias y Mejoras"):
        st.write("¿Tienes alguna idea para mejorar esta herramienta?")
        sugerencia = st.text_area("Escribe tu comentario aquí:", height=100)
        if st.button("Enviar Sugerencia"):
            if sugerencia:
                st.success("¡Gracias! Tu comentario ha sido recibido.")
            else:
                st.warning("Por favor escribe algo antes de enviar.")

if file_to_process is not None:
    df = load_data(file_to_process)
    
    if df is not None:
        # Crear 4 pestañas
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Agenda Individual", 
            "📊 Comparativa de Carga", 
            "🧩 Dashboard Global & Cronograma",
            "📝 Resumen General"
        ])

        # ==============================================================================
        # TAB 1: AGENDA INDIVIDUAL (Lógica de Intensidad Diaria)
        # ==============================================================================
        with tab1:
            col_sel, col_info = st.columns([1, 3])
            
            with col_sel:
                st.subheader("Selector")
                
                # --- FILTRO DE AÑO ---
                if pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                    lista_anos = sorted(df['DIAS/FECHAS'].dt.year.unique())
                    # Convertir a lista de enteros para mejor visualización
                    lista_anos = [int(x) for x in lista_anos]
                    anos_seleccionados = st.multiselect(
                        "Año(s):",
                        lista_anos,
                        default=lista_anos,
                        help="Filtrar por año"
                    )
                else:
                    anos_seleccionados = []
                # ---------------------

                lista_coord = sorted(df['COORDINADORA RESPONSABLE'].unique())
                coords_seleccionadas = st.multiselect(
                    "Coordinadora(s):", 
                    lista_coord,
                    default=[lista_coord[0]] if lista_coord else [],
                    help="Selecciona una o más coordinadoras para comparar"
                )
            
            # Validar que haya al menos una seleccionada
            if not coords_seleccionadas:
                st.warning("⚠️ Por favor selecciona al menos una coordinadora.")
                st.stop()
            
            # Filtrar data según selección (Coordinadora y Año)
            mask_coord = df['COORDINADORA RESPONSABLE'].isin(coords_seleccionadas)
            mask_year = True
            if anos_seleccionados and pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                mask_year = df['DIAS/FECHAS'].dt.year.isin(anos_seleccionados)
            
            df_coord = df[mask_coord & mask_year].sort_values(by='DIAS/FECHAS')
            
            # Determinar si es vista individual o comparativa
            es_comparativa = len(coords_seleccionadas) > 1

            # CÁLCULO DE PROGRAMAS POR DÍA
            if es_comparativa:
                # Para comparativa, agrupar por coordinadora y fecha
                carga_diaria = df_coord.groupby(['COORDINADORA RESPONSABLE', 'DIAS/FECHAS'])['PROGRAMA'].nunique().reset_index()
                carga_diaria.columns = ['Coordinadora', 'Fecha', 'Cant_Programas']
                # Calcular días críticos por coordinadora
                dias_criticos_por_coord = carga_diaria.groupby('Coordinadora').apply(
                    lambda x: len(x[x['Cant_Programas'] > 2])
                ).to_dict()
            else:
                # Vista individual
                carga_diaria = df_coord.groupby('DIAS/FECHAS')['PROGRAMA'].nunique().reset_index()
                carga_diaria.columns = ['Fecha', 'Cant_Programas']
                dias_criticos = carga_diaria[carga_diaria['Cant_Programas'] > 2]

            with col_info:
                if es_comparativa:
                    st.markdown(f"### 📊 Comparativa: {', '.join(coords_seleccionadas)}")
                    # Métricas comparativas
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Sesiones", len(df_coord))
                    m2.metric("Programas Únicos", df_coord['PROGRAMA'].nunique())
                    dias_unicos = df_coord['DIAS/FECHAS'].nunique()
                    m3.metric("Días con Clases", dias_unicos)
                    total_dias_criticos = sum(dias_criticos_por_coord.values())
                    m4.metric("Días Multiprograma (Total)", total_dias_criticos)
                else:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Sesiones", len(df_coord))
                    m2.metric("Programas Únicos", df_coord['PROGRAMA'].nunique())
                    # Calcular días únicos con clases
                    dias_unicos = df_coord['DIAS/FECHAS'].nunique()
                    m3.metric("Días con Clases", dias_unicos)
                    m4.metric("Días Multiprograma", len(dias_criticos), 
                              delta="Alerta" if len(dias_criticos) > 0 else "Ok", delta_color="inverse")

            st.markdown("#### 🔥 Análisis de Intensidad Diaria")
            if not carga_diaria.empty:
                if es_comparativa:
                    # Gráfico comparativo
                    fig_daily = px.bar(
                        carga_diaria, 
                        x='Fecha', 
                        y='Cant_Programas',
                        color='Coordinadora',
                        labels={'Cant_Programas': 'Nº Programas Distintos'},
                        barmode='group',
                        title="Comparativa de Intensidad Diaria por Coordinadora"
                    )
                    fig_daily.add_hline(y=2, line_dash="dot", annotation_text="Carga Normal")
                    st.plotly_chart(fig_daily, use_container_width=True)
                    
                    # Mostrar días críticos por coordinadora
                    st.markdown("##### ⚠️ Días Multiprograma por Coordinadora")
                    for coord in coords_seleccionadas:
                        coord_data = carga_diaria[carga_diaria['Coordinadora'] == coord]
                        coord_criticos = coord_data[coord_data['Cant_Programas'] > 2]
                        if not coord_criticos.empty:
                            with st.expander(f"⚠️ {coord} - {len(coord_criticos)} días con múltiples programas", expanded=False):
                                df_coord_actual = df[df['COORDINADORA RESPONSABLE'] == coord]
                                fechas_criticas = coord_criticos['Fecha'].dt.date.tolist() if pd.api.types.is_datetime64_any_dtype(coord_criticos['Fecha']) else coord_criticos['Fecha'].tolist()
                                
                                if pd.api.types.is_datetime64_any_dtype(df_coord_actual['DIAS/FECHAS']):
                                    detalle_critico = df_coord_actual[df_coord_actual['DIAS/FECHAS'].dt.date.isin(fechas_criticas)]
                                else:
                                    detalle_critico = df_coord_actual[df_coord_actual['DIAS/FECHAS'].isin(fechas_criticas)]
                                
                                columnas_disponibles = ['DIAS/FECHAS', 'PROGRAMA']
                                columnas_opcionales = ['HORARIO', 'ASIGNATURA', 'SEDE']
                                for col in columnas_opcionales:
                                    if col in detalle_critico.columns:
                                        columnas_disponibles.append(col)
                                
                                st.dataframe(
                                    detalle_critico[columnas_disponibles],
                                    hide_index=True,
                                    use_container_width=True
                                )
                        else:
                            st.success(f"✅ {coord} no tiene choques de múltiples programas.")
                else:
                    # Vista individual
                    fig_daily = px.bar(
                        carga_diaria, x='Fecha', y='Cant_Programas',
                        labels={'Cant_Programas': 'Nº Programas Distintos'},
                        color='Cant_Programas',
                        color_continuous_scale=['#90EE90', '#FF4B4B'] # Verde a Rojo
                    )
                    fig_daily.add_hline(y=2, line_dash="dot", annotation_text="Carga Normal")
                    st.plotly_chart(fig_daily, use_container_width=True)
                    
                    if not dias_criticos.empty:
                        with st.expander("⚠️ Ver Días con Múltiples Programas (Click para desplegar)", expanded=False):
                            if pd.api.types.is_datetime64_any_dtype(dias_criticos['Fecha']):
                                fechas_criticas = dias_criticos['Fecha'].dt.date.tolist()
                                detalle_critico = df_coord[df_coord['DIAS/FECHAS'].dt.date.isin(fechas_criticas)]
                            else:
                                fechas_criticas = dias_criticos['Fecha'].tolist()
                                detalle_critico = df_coord[df_coord['DIAS/FECHAS'].isin(fechas_criticas)]
                            
                            # Crear copia para no afectar el original
                            detalle_critico = detalle_critico.copy()
                            
                            # Agregar columna de Día y Año
                            if pd.api.types.is_datetime64_any_dtype(detalle_critico['DIAS/FECHAS']):
                                dias_map = {
                                    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                                }
                                detalle_critico['Día'] = detalle_critico['DIAS/FECHAS'].dt.day_name().map(dias_map)
                                detalle_critico['Año'] = detalle_critico['DIAS/FECHAS'].dt.year.astype(str)
                            else:
                                detalle_critico['Día'] = '-'
                                detalle_critico['Año'] = '-'

                            # Seleccionar solo las columnas que existen
                            columnas_disponibles = ['DIAS/FECHAS', 'Día', 'Año', 'PROGRAMA']
                            columnas_opcionales = ['HORARIO', 'ASIGNATURA', 'SEDE']
                            for col in columnas_opcionales:
                                if col in detalle_critico.columns:
                                    columnas_disponibles.append(col)
                            
                            st.dataframe(
                                detalle_critico[columnas_disponibles],
                                hide_index=True,
                                use_container_width=True
                            )
                    else:
                        st.success("✅ Esta coordinadora no tiene choques de múltiples programas en un mismo día.")
            
            # --- NUEVA SECCIÓN: DETALLE DE DÍAS CON CLASES ---
            st.markdown("---")
            if es_comparativa:
                st.markdown("### 📆 Detalle de Días con Clases (Comparativa)")
            else:
                st.markdown("### 📆 Detalle de Días con Clases")
            
            # Agrupar por día y contar clases (incluir coordinadora si es comparativa)
            if es_comparativa:
                group_by_cols = ['COORDINADORA RESPONSABLE', 'DIAS/FECHAS']
            else:
                group_by_cols = ['DIAS/FECHAS']
            
            agg_dict = {
                'PROGRAMA': ['count', 'nunique']
            }
            
            # Agregar columnas opcionales si existen
            if 'HORARIO' in df_coord.columns:
                agg_dict['HORARIO'] = lambda x: ', '.join(x.dropna().astype(str).unique()[:5])
            if 'ASIGNATURA' in df_coord.columns:
                agg_dict['ASIGNATURA'] = lambda x: ', '.join(x.dropna().astype(str).unique()[:3])
            if 'SEDE' in df_coord.columns:
                agg_dict['SEDE'] = lambda x: ', '.join(x.dropna().astype(str).unique()[:5])
            
            resumen_dias = df_coord.groupby(group_by_cols).agg(agg_dict).reset_index()
            
            # Aplanar nombres de columnas
            if es_comparativa:
                new_columns = ['Coordinadora', 'Fecha', 'Total_Clases', 'Programas_Distintos']
            else:
                new_columns = ['Fecha', 'Total_Clases', 'Programas_Distintos']
            
            if 'HORARIO' in df_coord.columns:
                new_columns.append('Horarios')
            if 'ASIGNATURA' in df_coord.columns:
                new_columns.append('Asignaturas')
            if 'SEDE' in df_coord.columns:
                new_columns.append('Sedes')
            
            resumen_dias.columns = new_columns
            
            # Agregar día de la semana si es posible
            fecha_col = 'Fecha'
            if pd.api.types.is_datetime64_any_dtype(resumen_dias[fecha_col]):
                # Mapear días de la semana al español
                dias_semana_esp = {
                    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                }
                resumen_dias['Dia_Semana'] = resumen_dias[fecha_col].dt.strftime('%A').map(dias_semana_esp).fillna(resumen_dias[fecha_col].dt.strftime('%A'))
                resumen_dias['Fecha_Formato'] = resumen_dias[fecha_col].dt.strftime('%d/%m/%Y')
                # Ordenar por fecha (y coordinadora si es comparativa)
                if es_comparativa:
                    resumen_dias = resumen_dias.sort_values(['Coordinadora', fecha_col])
                else:
                    resumen_dias = resumen_dias.sort_values(fecha_col)
            else:
                resumen_dias['Dia_Semana'] = '-'
                resumen_dias['Fecha_Formato'] = resumen_dias[fecha_col].astype(str)
            
            # Mostrar resumen de días
            if es_comparativa:
                # Vista comparativa: mostrar tabla con todas las coordinadoras
                st.markdown("#### 📊 Resumen por Día y Coordinadora")
                columnas_resumen = ['Coordinadora', 'Fecha_Formato', 'Dia_Semana', 'Total_Clases', 'Programas_Distintos']
                if 'Sedes' in resumen_dias.columns:
                    columnas_resumen.append('Sedes')
                st.dataframe(
                    resumen_dias[columnas_resumen].rename(columns={
                        'Coordinadora': 'Coordinadora',
                        'Fecha_Formato': 'Fecha',
                        'Dia_Semana': 'Día',
                        'Total_Clases': 'Clases',
                        'Programas_Distintos': 'Programas',
                        'Sedes': 'Sedes'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Detalle expandible por coordinadora
                st.markdown("#### 📋 Detalle Expandible por Coordinadora y Día")
                
                # Campo de búsqueda
                busqueda_comparativa = st.text_input("🔍 Buscar en días (fecha, día de semana, coordinadora):", 
                                                     key="busqueda_comparativa",
                                                     placeholder="Ej: Lunes, 15/03, o nombre coordinadora...")
                
                for coord in coords_seleccionadas:
                    coord_resumen = resumen_dias[resumen_dias['Coordinadora'] == coord]
                    
                    # Filtrar por búsqueda si hay texto
                    if busqueda_comparativa:
                        busqueda_lower = busqueda_comparativa.lower()
                        coord_resumen_filtrado = coord_resumen[
                            coord_resumen['Fecha_Formato'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
                            coord_resumen['Dia_Semana'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
                            coord_resumen['Coordinadora'].astype(str).str.lower().str.contains(busqueda_lower, na=False)
                        ]
                    else:
                        coord_resumen_filtrado = coord_resumen
                    
                    if len(coord_resumen_filtrado) > 0:
                        with st.expander(f"👤 {coord} - {len(coord_resumen_filtrado)} días con clases", expanded=False):
                            for idx, row in coord_resumen_filtrado.iterrows():
                                fecha_str = row['Fecha_Formato']
                                dia_semana = row['Dia_Semana']
                                total_clases = int(row['Total_Clases'])
                                programas = int(row['Programas_Distintos'])
                                
                                # Obtener detalle de ese día para esta coordinadora
                                df_coord_actual = df[df['COORDINADORA RESPONSABLE'] == coord]
                                if pd.api.types.is_datetime64_any_dtype(df_coord_actual['DIAS/FECHAS']):
                                    fecha_dt = pd.to_datetime(row['Fecha'])
                                    detalle_dia = df_coord_actual[df_coord_actual['DIAS/FECHAS'].dt.date == fecha_dt.date()]
                                else:
                                    detalle_dia = df_coord_actual[df_coord_actual['DIAS/FECHAS'] == row['Fecha']]
                                
                                # Crear título del expander
                                titulo = f"📅 {fecha_str} ({dia_semana}) - {total_clases} clase{'s' if total_clases > 1 else ''} - {programas} programa{'s' if programas > 1 else ''}"
                                
                                with st.expander(titulo, expanded=False):
                                    columnas_detalle = ['PROGRAMA']
                                    columnas_opcionales_detalle = ['HORARIO', 'ASIGNATURA', 'SEDE', 'DIA SEMANA']
                                    for col in columnas_opcionales_detalle:
                                        if col in detalle_dia.columns:
                                            columnas_detalle.append(col)
                                    
                                    st.dataframe(
                                        detalle_dia[columnas_detalle],
                                        hide_index=True,
                                        use_container_width=True
                                    )
            else:
                # Vista individual
                col_resumen1, col_resumen2 = st.columns(2)
                
                with col_resumen1:
                    st.markdown("#### 📊 Resumen por Día")
                    # Crear tabla resumida
                    columnas_resumen = ['Fecha_Formato', 'Dia_Semana', 'Total_Clases', 'Programas_Distintos']
                    if 'Sedes' in resumen_dias.columns:
                        columnas_resumen.append('Sedes')
                    st.dataframe(
                        resumen_dias[columnas_resumen].rename(columns={
                            'Fecha_Formato': 'Fecha',
                            'Dia_Semana': 'Día',
                            'Total_Clases': 'Clases',
                            'Programas_Distintos': 'Programas',
                            'Sedes': 'Sedes'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                
                with col_resumen2:
                    st.markdown("#### 📋 Detalle Expandible por Día")
                    
                    # Campo de búsqueda con ícono de lupa
                    busqueda_dias = st.text_input("🔍 Buscar en días (fecha, día de semana):", 
                                                  key="busqueda_dias",
                                                  placeholder="Ej: Lunes, 15/03, Marzo...")
                    
                    # Filtrar resumen_dias por búsqueda si hay texto
                    if busqueda_dias:
                        busqueda_lower = busqueda_dias.lower()
                        resumen_dias_filtrado = resumen_dias[
                            resumen_dias['Fecha_Formato'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
                            resumen_dias['Dia_Semana'].astype(str).str.lower().str.contains(busqueda_lower, na=False)
                        ]
                        if len(resumen_dias_filtrado) == 0:
                            st.info(f"🔍 No se encontraron días que coincidan con '{busqueda_dias}'")
                    else:
                        resumen_dias_filtrado = resumen_dias
                    
                    # Crear expanders para cada día filtrado
                    for idx, row in resumen_dias_filtrado.iterrows():
                        fecha_str = row['Fecha_Formato']
                        dia_semana = row['Dia_Semana']
                        total_clases = int(row['Total_Clases'])
                        programas = int(row['Programas_Distintos'])
                        
                        # Obtener detalle de ese día
                        if pd.api.types.is_datetime64_any_dtype(df_coord['DIAS/FECHAS']):
                            fecha_dt = pd.to_datetime(row['Fecha'])
                            detalle_dia = df_coord[df_coord['DIAS/FECHAS'].dt.date == fecha_dt.date()]
                        else:
                            detalle_dia = df_coord[df_coord['DIAS/FECHAS'] == row['Fecha']]
                        
                        # Crear título del expander
                        titulo = f"📅 {fecha_str} ({dia_semana}) - {total_clases} clase{'s' if total_clases > 1 else ''} - {programas} programa{'s' if programas > 1 else ''}"
                        
                        with st.expander(titulo, expanded=False):
                            # Seleccionar columnas disponibles
                            columnas_detalle = ['PROGRAMA']
                            columnas_opcionales_detalle = ['HORARIO', 'ASIGNATURA', 'SEDE', 'DIA SEMANA']
                            for col in columnas_opcionales_detalle:
                                if col in detalle_dia.columns:
                                    columnas_detalle.append(col)
                            
                            st.dataframe(
                                detalle_dia[columnas_detalle],
                                hide_index=True,
                                use_container_width=True
                            )
            
            st.markdown("---")
            st.markdown("### 📅 Calendario Completo de Clases")
            # Seleccionar solo las columnas que existen
            if es_comparativa:
                columnas_calendario = ['COORDINADORA RESPONSABLE', 'DIAS/FECHAS', 'PROGRAMA']
            else:
                columnas_calendario = ['DIAS/FECHAS', 'PROGRAMA']
            
            columnas_opcionales_cal = ['DIA SEMANA', 'HORARIO', 'ASIGNATURA', 'SEDE']
            for col in columnas_opcionales_cal:
                if col in df_coord.columns:
                    columnas_calendario.append(col)
            
            st.dataframe(
                df_coord[columnas_calendario],
                hide_index=True,
                use_container_width=True
            )

        # ==============================================================================
        # TAB 2: COMPARATIVA DE CARGA
        # ==============================================================================
        with tab2:
            st.subheader("Comparativa de Gestión")
            
            # --- FILTRO DE AÑO (TAB 2) ---
            if pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                lista_anos_t2 = sorted(df['DIAS/FECHAS'].dt.year.unique())
                lista_anos_t2 = [int(x) for x in lista_anos_t2]
                anos_sel_t2 = st.multiselect(
                    "Filtrar por Año:",
                    lista_anos_t2,
                    default=lista_anos_t2,
                    key="anos_tab2"
                )
            else:
                anos_sel_t2 = []
            # -----------------------------

            coords_a_comparar = st.multiselect(
                "Seleccionar Coordinadoras:", 
                lista_coord, 
                default=lista_coord[:min(3, len(lista_coord))] if lista_coord else []
            )
            
            if coords_a_comparar:
                # Filtrar por año primero
                mask_year_t2 = True
                if anos_sel_t2 and pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                    mask_year_t2 = df['DIAS/FECHAS'].dt.year.isin(anos_sel_t2)
                
                df_comp = df[mask_year_t2 & df['COORDINADORA RESPONSABLE'].isin(coords_a_comparar)]
                
                # Gráfico de Carga Total
                fig_bar = px.bar(
                    df_comp.groupby('COORDINADORA RESPONSABLE').size().reset_index(name='Total Clases'),
                    x='COORDINADORA RESPONSABLE',
                    y='Total Clases',
                    color='COORDINADORA RESPONSABLE',
                    text_auto=True,
                    title="Carga Total de Sesiones"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Comparativa de Intensidad
                resumen_intensidad = []
                for coord in coords_a_comparar:
                    data_c = df[df['COORDINADORA RESPONSABLE'] == coord]
                    dias_c = data_c.groupby('DIAS/FECHAS')['PROGRAMA'].nunique()
                    cant_dias_complejos = (dias_c > 1).sum()
                    resumen_intensidad.append({'Coordinadora': coord, 'Días Multiprograma': cant_dias_complejos})
                
                df_intensidad = pd.DataFrame(resumen_intensidad)
                
                fig_int = px.bar(
                    df_intensidad,
                    x='Coordinadora',
                    y='Días Multiprograma',
                    title="Días con Sobrecarga (Múltiples Programas el mismo día)",
                    color='Días Multiprograma',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_int, use_container_width=True)

        # ==============================================================================
        # TAB 3: DASHBOARD GLOBAL
        # ==============================================================================
        with tab3:
            st.subheader("Vista Global del Sistema")
            
            # --- FILTRO DE AÑO (TAB 3) ---
            if pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                lista_anos_t3 = sorted(df['DIAS/FECHAS'].dt.year.unique())
                lista_anos_t3 = [int(x) for x in lista_anos_t3]
                anos_sel_t3 = st.multiselect(
                    "Filtrar por Año:",
                    lista_anos_t3,
                    default=lista_anos_t3,
                    key="anos_tab3"
                )
                
                # Aplicar filtro
                mask_year_t3 = df['DIAS/FECHAS'].dt.year.isin(anos_sel_t3)
                df = df[mask_year_t3].copy()
            # -----------------------------

            st.info("Resumen general de todas las coordinadoras y sus cargas de trabajo.")
            
            # Resumen general
            resumen_global = df.groupby('COORDINADORA RESPONSABLE').agg({
                'PROGRAMA': 'nunique',
                'DIAS/FECHAS': 'count'
            }).reset_index()
            resumen_global.columns = ['Coordinadora', 'Programas Únicos', 'Total Sesiones']
            
            st.dataframe(resumen_global, hide_index=True, use_container_width=True)
            
            st.markdown("---")
            
            # --- GRÁFICO DE DÍAS DE LA SEMANA O MES CON CLASES ---
            st.markdown("### 📅 Distribución de Clases")
            
            # Selector para tipo de vista (Día de la Semana o Mes)
            tipo_vista = st.radio(
                "Ver por:",
                ["Día de la Semana", "Mes"],
                horizontal=True,
                key="tipo_vista_global"
            )
            
            # Crear columna de día de la semana si no existe o si las fechas son datetime
            if pd.api.types.is_datetime64_any_dtype(df['DIAS/FECHAS']):
                df['DIA_SEMANA_NUM'] = df['DIAS/FECHAS'].dt.dayofweek
                # Mapear a nombres en español
                dias_semana_map = {
                    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
                    4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
                }
                df['DIA_SEMANA_NOMBRE'] = df['DIA_SEMANA_NUM'].map(dias_semana_map)
                
                # Crear columna de mes
                meses_map = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }
                df['MES_NUM'] = df['DIAS/FECHAS'].dt.month
                df['MES_NOMBRE'] = df['MES_NUM'].map(meses_map)
                df['MES_ANIO'] = df['DIAS/FECHAS'].dt.to_period('M').astype(str)
            elif 'DIA SEMANA' in df.columns:
                df['DIA_SEMANA_NOMBRE'] = df['DIA SEMANA']
                df['MES_NOMBRE'] = 'Sin Mes'
                df['MES_ANIO'] = 'Sin Mes'
            else:
                st.warning("⚠️ No se puede determinar el día de la semana o mes. Asegúrate de que las fechas estén en formato correcto.")
                df['DIA_SEMANA_NOMBRE'] = 'Sin Día'
                df['MES_NOMBRE'] = 'Sin Mes'
                df['MES_ANIO'] = 'Sin Mes'
            
            # Selector para tipo de agrupación
            tipo_agrupacion = st.radio(
                "Agrupar por:",
                ["Programa", "Coordinadora", "Ambos"],
                horizontal=True,
                key="tipo_agrupacion_global"
            )
            
            # Preparar datos según el tipo de vista y agrupación
            if tipo_vista == "Día de la Semana":
                columna_agrupacion = 'DIA_SEMANA_NOMBRE'
                orden_valores = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                titulo_base = "Cantidad de Clases por Día de la Semana"
                label_x = 'Día de la Semana'
            else:  # Mes
                columna_agrupacion = 'MES_ANIO'
                # Ordenar por fecha
                orden_valores = sorted(df[columna_agrupacion].unique())
                titulo_base = "Cantidad de Clases por Mes"
                label_x = 'Mes'
            
            if tipo_agrupacion == "Programa":
                # Agrupar por columna seleccionada y programa
                datos_grafico = df.groupby([columna_agrupacion, 'PROGRAMA']).size().reset_index(name='Cantidad_Clases')
                
                # Ordenar
                if tipo_vista == "Día de la Semana":
                    datos_grafico[columna_agrupacion] = pd.Categorical(
                        datos_grafico[columna_agrupacion], 
                        categories=orden_valores, 
                        ordered=True
                    )
                datos_grafico = datos_grafico.sort_values(columna_agrupacion)
                
                # Crear gráfico de barras agrupadas
                fig_dias = px.bar(
                    datos_grafico,
                    x=columna_agrupacion,
                    y='Cantidad_Clases',
                    color='PROGRAMA',
                    title=f"{titulo_base} - Por Programa",
                    labels={columna_agrupacion: label_x, 'Cantidad_Clases': 'Cantidad de Clases'},
                    barmode='group',
                    text='Cantidad_Clases'
                )
                fig_dias.update_traces(texttemplate='%{text}', textposition='outside')
                if tipo_vista == "Mes":
                    fig_dias.update_xaxes(tickangle=-45)
                
            elif tipo_agrupacion == "Coordinadora":
                # Agrupar por columna seleccionada y coordinadora
                datos_grafico = df.groupby([columna_agrupacion, 'COORDINADORA RESPONSABLE']).size().reset_index(name='Cantidad_Clases')
                
                # Ordenar
                if tipo_vista == "Día de la Semana":
                    datos_grafico[columna_agrupacion] = pd.Categorical(
                        datos_grafico[columna_agrupacion], 
                        categories=orden_valores, 
                        ordered=True
                    )
                datos_grafico = datos_grafico.sort_values(columna_agrupacion)
                
                # Crear gráfico de barras agrupadas
                fig_dias = px.bar(
                    datos_grafico,
                    x=columna_agrupacion,
                    y='Cantidad_Clases',
                    color='COORDINADORA RESPONSABLE',
                    title=f"{titulo_base} - Por Coordinadora",
                    labels={columna_agrupacion: label_x, 'Cantidad_Clases': 'Cantidad de Clases', 'COORDINADORA RESPONSABLE': 'Coordinadora'},
                    barmode='group',
                    text='Cantidad_Clases'
                )
                fig_dias.update_traces(texttemplate='%{text}', textposition='outside')
                if tipo_vista == "Mes":
                    fig_dias.update_xaxes(tickangle=-45)
                
            else:  # Ambos
                # Agrupar por columna seleccionada, programa y coordinadora
                datos_grafico = df.groupby([columna_agrupacion, 'PROGRAMA', 'COORDINADORA RESPONSABLE']).size().reset_index(name='Cantidad_Clases')
                
                # Ordenar
                if tipo_vista == "Día de la Semana":
                    datos_grafico[columna_agrupacion] = pd.Categorical(
                        datos_grafico[columna_agrupacion], 
                        categories=orden_valores, 
                        ordered=True
                    )
                datos_grafico = datos_grafico.sort_values(columna_agrupacion)
                
                # Crear gráfico de barras apiladas
                fig_dias = px.bar(
                    datos_grafico,
                    x=columna_agrupacion,
                    y='Cantidad_Clases',
                    color='PROGRAMA',
                    facet_col='COORDINADORA RESPONSABLE',
                    title=f"{titulo_base} - Por Programa y Coordinadora",
                    labels={columna_agrupacion: label_x, 'Cantidad_Clases': 'Cantidad de Clases'},
                    barmode='stack'
                )
                fig_dias.update_xaxes(tickangle=-45)
            
            st.plotly_chart(fig_dias, use_container_width=True)
            
            # Tabla resumen según el tipo de vista
            if tipo_vista == "Día de la Semana":
                st.markdown("#### 📊 Resumen por Día de la Semana")
                resumen = df.groupby('DIA_SEMANA_NOMBRE').agg({
                    'PROGRAMA': 'nunique',
                    'COORDINADORA RESPONSABLE': 'nunique',
                    'DIAS/FECHAS': 'count'
                }).reset_index()
                resumen.columns = ['Día de la Semana', 'Programas Únicos', 'Coordinadoras', 'Total Clases']
                
                # Ordenar por orden de días
                orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                resumen['Día de la Semana'] = pd.Categorical(
                    resumen['Día de la Semana'], 
                    categories=orden_dias, 
                    ordered=True
                )
                resumen = resumen.sort_values('Día de la Semana')
            else:  # Mes
                st.markdown("#### 📊 Resumen por Mes")
                resumen = df.groupby('MES_ANIO').agg({
                    'PROGRAMA': 'nunique',
                    'COORDINADORA RESPONSABLE': 'nunique',
                    'DIAS/FECHAS': 'count'
                }).reset_index()
                resumen.columns = ['Mes', 'Programas Únicos', 'Coordinadoras', 'Total Clases']
                resumen = resumen.sort_values('Mes')
            
            st.dataframe(resumen, hide_index=True, use_container_width=True)
            
            st.markdown("---")
            
            # --- GRÁFICO DE DÍAS DONDE SE TOPAN LAS COORDINADORAS ---
            st.markdown("### ⚠️ Días donde se Topan las Coordinadoras")
            st.info("Este gráfico muestra los días donde múltiples coordinadoras tienen clases, indicando posibles conflictos de recursos o sobrecarga del sistema.")
            
            # Calcular días donde hay múltiples coordinadoras
            dias_coordinadoras = df.groupby('DIAS/FECHAS')['COORDINADORA RESPONSABLE'].nunique().reset_index()
            dias_coordinadoras.columns = ['Fecha', 'Cantidad_Coordinadoras']
            
            # Identificar días con choques (más de 1 coordinadora)
            dias_choques = dias_coordinadoras[dias_coordinadoras['Cantidad_Coordinadoras'] > 1].copy()
            
            if not dias_choques.empty:
                # Agregar información de fecha formateada
                if pd.api.types.is_datetime64_any_dtype(dias_choques['Fecha']):
                    dias_choques['Fecha_Formato'] = dias_choques['Fecha'].dt.strftime('%d/%m/%Y')
                    dias_choques['Dia_Semana'] = dias_choques['Fecha'].dt.strftime('%A')
                    # Mapear días al español
                    dias_semana_map = {
                        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                    }
                    dias_choques['Dia_Semana'] = dias_choques['Dia_Semana'].map(dias_semana_map)
                    dias_choques = dias_choques.sort_values('Fecha')
                else:
                    dias_choques['Fecha_Formato'] = dias_choques['Fecha'].astype(str)
                    dias_choques['Dia_Semana'] = '-'
                
                # Gráfico de barras mostrando cantidad de coordinadoras por día
                fig_choques = px.bar(
                    dias_choques,
                    x='Fecha_Formato',
                    y='Cantidad_Coordinadoras',
                    color='Cantidad_Coordinadoras',
                    color_continuous_scale='Reds',
                    title="Días con Múltiples Coordinadoras (Choques)",
                    labels={
                        'Fecha_Formato': 'Fecha',
                        'Cantidad_Coordinadoras': 'Cantidad de Coordinadoras',
                        'Dia_Semana': 'Día de la Semana'
                    },
                    text='Cantidad_Coordinadoras',
                    hover_data=['Dia_Semana']
                )
                fig_choques.update_traces(texttemplate='%{text}', textposition='outside')
                fig_choques.update_xaxes(tickangle=-45)
                fig_choques.add_hline(y=1, line_dash="dot", line_color="green", 
                                     annotation_text="Sin choques (1 coordinadora)", 
                                     annotation_position="bottom right")
                st.plotly_chart(fig_choques, use_container_width=True)
                

                
                # Tabla detallada de choques
                st.markdown("#### 📋 Detalle de Días con Choques")
                
                # Agregar información de qué coordinadoras coinciden
                detalle_choques = []
                for fecha in dias_choques['Fecha'].unique():
                    coord_del_dia = sorted(df[df['DIAS/FECHAS'] == fecha]['COORDINADORA RESPONSABLE'].unique())
                    fecha_str = dias_choques[dias_choques['Fecha'] == fecha]['Fecha_Formato'].iloc[0] if pd.api.types.is_datetime64_any_dtype(dias_choques['Fecha']) else str(fecha)
                    dia_sem = dias_choques[dias_choques['Fecha'] == fecha]['Dia_Semana'].iloc[0] if 'Dia_Semana' in dias_choques.columns else '-'
                    cant_coord = len(coord_del_dia)
                    
                    detalle_choques.append({
                        'Fecha': fecha_str,
                        'Día': dia_sem,
                        'Cantidad Coordinadoras': cant_coord,
                        'Coordinadoras': ', '.join(coord_del_dia)
                    })
                
                df_detalle_choques = pd.DataFrame(detalle_choques)
                st.dataframe(df_detalle_choques, hide_index=True, use_container_width=True)
                
                # Métricas resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Días con Choques", len(dias_choques))
                with col2:
                    max_coord = dias_choques['Cantidad_Coordinadoras'].max()
                    st.metric("Máximo Coordinadoras en un Día", max_coord)
                with col3:
                    prom_coord = dias_choques['Cantidad_Coordinadoras'].mean()
                    st.metric("Promedio Coordinadoras por Día", f"{prom_coord:.1f}")
            else:
                st.success("✅ No hay días donde se topen múltiples coordinadoras. Todas las coordinadoras trabajan en días diferentes.")


        # ==============================================================================
        # TAB 4: RESUMEN GENERAL (REDSEÑADO)
        # ==============================================================================
        with tab4:
            st.markdown("## Resumen General de Programas")
            
            # --- PREPARACIÓN DE DATOS ---
            # Copia base para cálculos
            df_kpi = df.copy()
            
            # Calcular Modalidad basado en Sede
            def get_modalidad(sede):
                s = str(sede).upper()
                if 'ONLINE' in s or 'ZOOM' in s: return 'Online'
                if 'HIBRID' in s or 'HÍBRID' in s: return 'Híbrida'
                return 'Presencial'
            
            if 'SEDE' in df_kpi.columns:
                df_kpi['Modalidad_Calc'] = df_kpi['SEDE'].apply(get_modalidad)
            else:
                df_kpi['Modalidad_Calc'] = 'Desconocida'

            # --- FILTROS ---
            st.markdown("### Filtros")
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            # Filtro Año
            with col_f1:
                if pd.api.types.is_datetime64_any_dtype(df_kpi['DIAS/FECHAS']):
                    years = sorted(df_kpi['DIAS/FECHAS'].dt.year.unique())
                    sel_year = st.selectbox("Año", ["Todos"] + list(years), index=0)
                else:
                    sel_year = "Todos"

            # Filtro Coordinadora
            with col_f2:
                coords = sorted(df_kpi['COORDINADORA RESPONSABLE'].unique())
                sel_coord = st.multiselect("Coordinadoras", coords, placeholder="Todas")

            # Filtro Programa (Vinculado a Coordinadora)
            with col_f3:
                if sel_coord:
                    progs = sorted(df_kpi[df_kpi['COORDINADORA RESPONSABLE'].isin(sel_coord)]['PROGRAMA'].unique())
                else:
                    progs = sorted(df_kpi['PROGRAMA'].unique())
                sel_prog = st.multiselect("Programas", progs, placeholder="Todos")

            # Filtro Modalidad
            with col_f4:
                mods = sorted(df_kpi['Modalidad_Calc'].unique())
                sel_mod = st.multiselect("Modalidad", mods, placeholder="Todas")

            # --- APLICAR FILTROS ---
            mask = pd.Series([True] * len(df_kpi))
            
            if sel_year != "Todos" and pd.api.types.is_datetime64_any_dtype(df_kpi['DIAS/FECHAS']):
                mask &= (df_kpi['DIAS/FECHAS'].dt.year == sel_year)
            
            if sel_coord:
                mask &= (df_kpi['COORDINADORA RESPONSABLE'].isin(sel_coord))
            
            if sel_prog:
                mask &= (df_kpi['PROGRAMA'].isin(sel_prog))
                
            if sel_mod:
                mask &= (df_kpi['Modalidad_Calc'].isin(sel_mod))
            
            df_filtered = df_kpi[mask].copy()

            # --- CÁLCULO DE KPIS ---
            if not df_filtered.empty:
                total_programas = df_filtered['PROGRAMA'].nunique()
                total_sesiones = len(df_filtered)
                
                # Cálculo de Avance
                from datetime import datetime
                hoy = datetime.now()
                
                prog_stats = df_filtered.groupby('PROGRAMA').agg({
                    'DIAS/FECHAS': ['min', 'max']
                })
                prog_stats.columns = ['Inicio', 'Fin']
                
                def calc_avance(row):
                    if pd.isna(row['Inicio']) or pd.isna(row['Fin']): return 0
                    total_days = (row['Fin'] - row['Inicio']).days
                    if total_days <= 0: return 100
                    elapsed = (hoy - row['Inicio']).days
                    if elapsed < 0: return 0
                    if elapsed > total_days: return 100
                    return int((elapsed / total_days) * 100)

                prog_stats['Avance'] = prog_stats.apply(calc_avance, axis=1)
                avance_promedio = int(prog_stats['Avance'].mean())
                docs_pendientes = 284 
                
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Programas activos", total_programas, border=True)
                k2.metric("Sesiones totales", f"{total_sesiones:,}".replace(",", "."), border=True)
                k3.metric("Avance del calendario", f"{avance_promedio} %", border=True)
                k4.metric("Documentos pendientes", f"{docs_pendientes} alumnos", border=True)
                
                st.markdown("---")
                
                # --- TABLA DETALLADA ---
                if 'HORARIO' in df_filtered.columns:
                    def calcular_horas(h):
                        import re
                        try:
                            hrs = re.findall(r'(\d{1,2}:\d{2})', str(h))
                            if len(hrs) >= 2:
                                t1 = datetime.strptime(hrs[0], "%H:%M")
                                t2 = datetime.strptime(hrs[1], "%H:%M")
                                return (t2 - t1).total_seconds() / 3600
                            return 0
                        except: return 0
                    df_filtered['Horas_Calc'] = df_filtered['HORARIO'].apply(calcular_horas)
                else:
                    df_filtered['Horas_Calc'] = 0

                # --- CÁLCULO DE SEMANAS CRÍTICAS (GLOBAL) ---
                # Identificar (Coordinadora, Fecha) donde hay > 1 programa
                # Usamos df_kpi (sin filtrar programas) pero respetando el año si se seleccionó
                df_context = df_kpi.copy()
                if sel_year != "Todos" and pd.api.types.is_datetime64_any_dtype(df_context['DIAS/FECHAS']):
                    df_context = df_context[df_context['DIAS/FECHAS'].dt.year == sel_year]
                
                choques = df_context.groupby(['COORDINADORA RESPONSABLE', 'DIAS/FECHAS'])['PROGRAMA'].nunique()
                choques = choques[choques > 1].reset_index()
                # Set de fechas críticas por coordinadora
                # Clave: (Coordinadora, Fecha)
                set_criticos = set(zip(choques['COORDINADORA RESPONSABLE'], choques['DIAS/FECHAS']))

                # --- AGREGACIÓN ---
                # Mapeo de días y meses
                dias_map = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
                meses_map = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}

                def get_dias_str(series):
                    try:
                        if pd.api.types.is_datetime64_any_dtype(series):
                            # Obtener nombres en inglés para asegurar el mapeo
                            # Si falla, intentamos usar el valor directo si ya está en español o mapear con seguridad
                            nombres = series.dt.day_name()
                            # Mapear y eliminar NaNs
                            dias = nombres.map(dias_map).dropna().unique()
                            
                            # Si dias está vacío, quizás los nombres ya estaban en español o en otro idioma?
                            if len(dias) == 0 and not nombres.empty:
                                # Fallback: usar los nombres tal cual
                                dias = nombres.dropna().unique()

                            orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                            # Filtrar solo strings
                            dias = [str(d) for d in dias]
                            dias_ord = sorted(dias, key=lambda x: orden.index(x) if x in orden else 99)
                            return ', '.join(dias_ord)
                    except:
                        return '-'
                    return '-'

                def get_meses_str(series):
                    try:
                        if pd.api.types.is_datetime64_any_dtype(series):
                            meses_nums = series.dt.month.dropna().unique()
                            meses_nums.sort()
                            # Mapear con seguridad
                            meses_ord = [str(meses_map.get(m, m)) for m in meses_nums]
                            return ', '.join(meses_ord)
                    except:
                        return '-'
                    return '-'

                def get_semanas_criticas(sub_df):
                    try:
                        if sub_df.empty: return "0"
                        # sub_df son las filas de UN programa
                        coord = sub_df['COORDINADORA RESPONSABLE'].iloc[0]
                        fechas = sub_df['DIAS/FECHAS']
                        
                        semanas = set()
                        for f in fechas:
                            # Asegurar que f es timestamp válido
                            if pd.isna(f): continue
                            if (coord, f) in set_criticos:
                                semanas.add(f.isocalendar()[1])
                        
                        if not semanas:
                            return "0"
                        return ', '.join(map(str, sorted(semanas)))
                    except:
                        return "Error"

                try:
                    def get_fecha_str(val):
                        if pd.isna(val): return '-'
                        return val.strftime('%d/%m/%Y')

                    def get_horario_str(series):
                        try:
                            # Intentar obtener la moda (horario más frecuente)
                            if not series.mode().empty:
                                return str(series.mode()[0])
                            # Si no, tomar el primero
                            return str(series.iloc[0]) if not series.empty else '-'
                        except: return '-'

                    tabla_resumen = df_filtered.groupby('PROGRAMA').apply(lambda x: pd.Series({
                        'Sesiones': len(x),
                        'Horas': x['Horas_Calc'].sum(),
                        'Modalidad': x['Modalidad_Calc'].mode()[0] if not x['Modalidad_Calc'].mode().empty else 'N/A',
                        'Coordinador(a)': ', '.join(sorted(x['COORDINADORA RESPONSABLE'].dropna().unique())),
                        'Sede': ', '.join(sorted(x['SEDE'].astype(str).unique())),
                        'Fecha Inicio': get_fecha_str(x['DIAS/FECHAS'].min()),
                        'Fecha Término': get_fecha_str(x['DIAS/FECHAS'].max()),
                        'Horario': get_horario_str(x['HORARIO']) if 'HORARIO' in x.columns else '-',
                        'Días': get_dias_str(x['DIAS/FECHAS']),
                        'Meses': get_meses_str(x['DIAS/FECHAS']),
                        'Semanas críticas': get_semanas_criticas(x)
                    })).reset_index()
                except Exception as e:
                    st.error(f"Error al generar la tabla resumen: {e}")
                    tabla_resumen = pd.DataFrame()

                # Unir con avance
                if 'Avance' in prog_stats.columns:
                    tabla_resumen = tabla_resumen.merge(prog_stats[['Avance']], left_on='PROGRAMA', right_index=True, how='left')
                    tabla_resumen['Avance'] = tabla_resumen['Avance'].fillna(0).astype(int)
                else:
                    tabla_resumen['Avance'] = 0
                
                # Renombrar columna para coincidir con cols_order
                tabla_resumen = tabla_resumen.rename(columns={'PROGRAMA': 'Programa'})

                # Ordenar columnas
                cols_order = [
                    'Programa', 'Sesiones', 'Horas', 'Modalidad', 'Sede',
                    'Coordinador(a)', 'Fecha Inicio', 'Fecha Término', 'Horario', 
                    'Días', 'Meses', '% Avance', 'Semanas críticas'
                ]
                
                # Renombrar avance para display y asegurar tipo numérico
                tabla_resumen['% Avance'] = tabla_resumen['Avance']
                
                # Ajustes finales
                tabla_resumen['Horas'] = tabla_resumen['Horas'].fillna(0).astype(int)
                
                # --- ESTILOS ---
                def highlight_rows(row):
                    # Estilo por defecto
                    styles = [''] * len(row)
                    
                    # Verificar si hay semanas críticas (topes)
                    if str(row['Semanas críticas']) != "0":
                        # Definir estilo de alerta
                        alert_style = 'color: #FF0000; font-weight: bold'
                        
                        # Aplicar a columna 'Días'
                        if 'Días' in row.index:
                            idx = row.index.get_loc('Días')
                            styles[idx] = alert_style
                        
                        # Aplicar a columna 'Horario'
                        if 'Horario' in row.index:
                            idx = row.index.get_loc('Horario')
                            styles[idx] = alert_style
                            
                        # Aplicar a columna 'Semanas críticas'
                        if 'Semanas críticas' in row.index:
                            idx = row.index.get_loc('Semanas críticas')
                            styles[idx] = alert_style
                            
                    return styles

                # Aplicar estilos
                styled_df = tabla_resumen[cols_order].style.apply(highlight_rows, axis=1)

                st.dataframe(
                    styled_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "% Avance": st.column_config.ProgressColumn(
                            "% Avance",
                            format="%d %%",
                            min_value=0,
                            max_value=100,
                        ),
                    }
                )

            else:
                st.warning("No hay datos que coincidan con los filtros seleccionados.")


else:
    st.info("👆 Sube el archivo CSV para comenzar.")
