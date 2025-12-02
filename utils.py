import streamlit as st
import pandas as pd
import io
from datetime import datetime
 
# --- CARGA DE DATOS ---
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
 
        # Limpieza básica
        df.columns = df.columns.str.strip().str.upper()
        
        # Validar columnas mínimas
        req_cols = ['COORDINADORA RESPONSABLE', 'DIAS/FECHAS']
        if not all(col in df.columns for col in req_cols):
            st.error(f"Faltan columnas requeridas: {req_cols}")
            return None
 
        df = df.dropna(subset=req_cols)
        df['DIAS/FECHAS'] = pd.to_datetime(df['DIAS/FECHAS'], errors='coerce')
        df = df.dropna(subset=['DIAS/FECHAS'])
        
        # Normalización
        df['COORDINADORA RESPONSABLE'] = df['COORDINADORA RESPONSABLE'].astype(str).str.upper().str.strip()
        
        if 'PROGRAMA' in df.columns:
            df['PROGRAMA'] = df['PROGRAMA'].fillna('Sin Programa').astype(str).str.upper().str.strip()
        else:
            df['PROGRAMA'] = 'SIN PROGRAMA'
 
        if 'SEDE' in df.columns:
            df['SEDE'] = df['SEDE'].fillna('ONLINE/OTRO').astype(str).str.upper().str.strip()
        else:
            df['SEDE'] = 'ONLINE/OTRO'
            
        # Calcular Modalidad
        def get_modalidad(sede):
            s = str(sede).upper()
            if 'ONLINE' in s or 'ZOOM' in s:
                return 'Online'
            if 'HIBRID' in s or 'HÍBRID' in s:
                return 'Híbrida'
            return 'Presencial'
            
        df['Modalidad_Calc'] = df['SEDE'].apply(get_modalidad)
        
        # Día de la semana
        dias_map = {
            0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
            4: "Viernes", 5: "Sábado", 6: "Domingo"
        }
        df['Dia_Semana'] = df['DIAS/FECHAS'].dt.dayofweek.map(dias_map)
        
        return df
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return None
 
# --- FILTROS ---
def reset_filters():
    # Limpia todas las keys de session_state que empiecen con 't' (t1_, t2_, etc)
    for key in list(st.session_state.keys()):
        if key.startswith(('t1_', 't2_', 't3_', 't4_')):
            del st.session_state[key]
 
def render_filters(df, prefix="t1"):
    """
    Renderiza filtros comunes y retorna el dataframe filtrado.
    """
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Año
        with col1:
            years = sorted(df['DIAS/FECHAS'].dt.year.unique())
            sel_year = st.multiselect("Año", years, default=years, key=f"{prefix}_year")
            
        # Coordinadora
        with col2:
            coords = sorted(df['COORDINADORA RESPONSABLE'].unique())
            sel_coord = st.multiselect("Coordinadora", coords, key=f"{prefix}_coord")
            
        # Programa
        with col3:
            # Filtrar programas según coord seleccionada si aplica
            if sel_coord:
                progs = sorted(df[df['COORDINADORA RESPONSABLE'].isin(sel_coord)]['PROGRAMA'].unique())
            else:
                progs = sorted(df['PROGRAMA'].unique())
            sel_prog = st.multiselect("Programa", progs, key=f"{prefix}_prog")
            
        col4, col5, col6 = st.columns(3)
        
        # Modalidad
        with col4:
            mods = sorted(df['Modalidad_Calc'].unique())
            sel_mod = st.multiselect("Modalidad", mods, key=f"{prefix}_mod")
            
        # Sede
        with col5:
            sedes = sorted(df['SEDE'].unique())
            sel_sede = st.multiselect("Sede", sedes, key=f"{prefix}_sede")
            
        # Día
        with col6:
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            avail_dias = sorted([d for d in dias if d in df['Dia_Semana'].unique()], key=lambda x: dias.index(x))
            sel_dia = st.multiselect("Día", avail_dias, key=f"{prefix}_dia")
        
    # Aplicar filtros
    mask = pd.Series(True, index=df.index)
    if sel_year: mask &= df['DIAS/FECHAS'].dt.year.isin(sel_year)
    if sel_coord: mask &= df['COORDINADORA RESPONSABLE'].isin(sel_coord)
    if sel_prog: mask &= df['PROGRAMA'].isin(sel_prog)
    if sel_mod: mask &= df['Modalidad_Calc'].isin(sel_mod)
    if sel_sede: mask &= df['SEDE'].isin(sel_sede)
    if sel_dia: mask &= df['Dia_Semana'].isin(sel_dia)
    
    return df[mask]
 
# --- EXPORTAR ---
def generate_excel_report(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos_Completos')
        
        # Resumen por coord
        resumen = df.groupby('COORDINADORA RESPONSABLE').size().reset_index(name='Total Clases')
        resumen.to_excel(writer, index=False, sheet_name='Resumen_Coordinadoras')
        
    return output.getvalue()
