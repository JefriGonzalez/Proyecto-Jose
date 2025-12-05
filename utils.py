import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CARGA DE DATOS ---
import re
import numpy as np

# --- CONSTANTES ---
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12,
}

MESES_NOMBRE = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

DIAS_SEMANA_MAP = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
}

# --- FUNCIONES AUXILIARES ---
def quitar_acentos(texto: str) -> str:
    reemplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    t = str(texto)
    for orig, repl in reemplazos:
        t = t.replace(orig, repl)
    return t

def convertir_fecha_uai(texto):
    if pd.isna(texto): return np.nan
    if isinstance(texto, datetime): return texto
    t = str(texto).strip().lower()
    if not t: return np.nan
    try: return pd.to_datetime(texto, dayfirst=True)
    except: pass
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+(\d{4})", t)
    if not m: return np.nan
    try:
        dia = int(m.group(1))
        mes_txt = quitar_acentos(m.group(2))
        anio = int(m.group(3))
        mes = MESES.get(mes_txt, None)
        if mes is None: return np.nan
        return datetime(anio, mes, dia)
    except: return np.nan

# --- CARGA DE DATOS ---
# @st.cache_data (Removed to avoid hashing issues with file objects)
def load_data(file):
    try:
        # 1. Leer archivo crudo
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df_raw = pd.read_excel(file, header=None)
        else:
            df_raw = pd.read_csv(file, header=None)

        # 2. Buscar fila de encabezados
        keywords_header = ["DIAS/FECHAS", "FECHA", "DIA", "DATE"]
        header_idx = None
        # Optimization: Only search first 50 rows
        df_scan = df_raw.head(50)
        for keyword in keywords_header:
            mask = df_scan.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False)).any(axis=1)
            if mask.any():
                header_idx = df_scan[mask].index[0]
                break
        
        if header_idx is None:
            # Fallback: intentar leer normal si no encuentra header complejo
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
        else:
            # Procesar desde el header encontrado
            df = df_raw.loc[header_idx:].reset_index(drop=True)
            df.columns = df.iloc[0].astype(str).str.strip().str.upper()
            df = df[1:].reset_index(drop=True)

        # 3. Normalizar columnas
        df.columns = df.columns.str.strip().str.upper()
        cols = list(df.columns)

        def find_col(options):
            for opt in options:
                for c in cols:
                    if opt in c: return c
            return None

        col_fecha = find_col(["DIAS/FECHAS", "FECHA", "DIA"])
        col_coord = find_col(["COORDINADORA", "COORD"])
        col_prog = find_col(["PROGRAMA", "CARRERA"])
        col_sede = find_col(["SEDE", "UBICACION"])
        col_prof = find_col(["PROFESOR", "DOCENTE", "RELATOR"])
        
        # Validar mínima
        if not col_fecha:
            st.error("No se encontró columna de Fecha.")
            return None
            
        # Renombrar para estandarizar
        rename_map = {col_fecha: "DIAS/FECHAS"}
        if col_coord: rename_map[col_coord] = "COORDINADORA RESPONSABLE"
        if col_prog: rename_map[col_prog] = "PROGRAMA"
        if col_sede: rename_map[col_sede] = "SEDE"
        if col_prof: rename_map[col_prof] = "PROFESOR"
        
        df = df.rename(columns=rename_map)
        
        # Si falta Coordinadora, avisar (es crítico para T_1)
        if "COORDINADORA RESPONSABLE" not in df.columns:
            # Si no existe, creamos una dummy o avisamos? T_1 depende de esto.
            # Intentamos ser flexibles:
            df["COORDINADORA RESPONSABLE"] = "SIN ASIGNAR"

        # 4. Procesar Fechas
        df["DIAS/FECHAS"] = df["DIAS/FECHAS"].apply(convertir_fecha_uai)
        df = df.dropna(subset=["DIAS/FECHAS"])
        
        # 5. Columnas Calculadas
        df['Dia_Semana'] = df['DIAS/FECHAS'].dt.day_name().map(DIAS_SEMANA_MAP)
        df['Mes'] = df['DIAS/FECHAS'].dt.month.map(MESES_NOMBRE)
        
        # Normalizar textos
        for col in ["COORDINADORA RESPONSABLE", "PROGRAMA", "SEDE", "PROFESOR"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper().str.strip()
            else:
                df[col] = "SIN " + col

        # Modalidad
        def get_modalidad(sede):
            s = str(sede).upper()
            if 'ONLINE' in s or 'ZOOM' in s: return 'Online'
            if 'HIBRID' in s or 'HÍBRID' in s: return 'Híbrida'
            return 'Presencial'
        
        df['Modalidad_Calc'] = df['SEDE'].apply(get_modalidad)
        
        # Intentar extraer horas si existen (para validaciones)
        # Buscamos columnas de hora por posición relativa a fecha o por nombre
        col_h_inicio = find_col(["HORA INICIO", "INICIO", "DESDE"])
        col_h_fin = find_col(["HORA FIN", "FIN", "HASTA"])
        
        if col_h_inicio and col_h_fin:
             # Convertir a string para evitar ArrowTypeError en Streamlit
             df["HORA_INICIO"] = pd.to_datetime(df[col_h_inicio].astype(str), errors='coerce').dt.time.astype(str)
             df["HORA_FIN"] = pd.to_datetime(df[col_h_fin].astype(str), errors='coerce').dt.time.astype(str)
             
             # Crear columna HORARIO si no existe, como string
             if "HORARIO" not in df.columns:
                 df["HORARIO"] = df["HORA_INICIO"] + " - " + df["HORA_FIN"]
        else:
            # Intentar por posición (asumiendo Fecha + 1 y Fecha + 2 como en app.extr.py)
            try:
                idx_fecha = df.columns.get_loc("DIAS/FECHAS")
                if idx_fecha + 2 < len(df.columns):
                    df["HORA_INICIO"] = pd.to_datetime(df.iloc[:, idx_fecha+1].astype(str), errors='coerce').dt.time.astype(str)
                    df["HORA_FIN"] = pd.to_datetime(df.iloc[:, idx_fecha+2].astype(str), errors='coerce').dt.time.astype(str)
                    if "HORARIO" not in df.columns:
                         df["HORARIO"] = df["HORA_INICIO"] + " - " + df["HORA_FIN"]
            except:
                pass
        
        # Asegurar que HORARIO sea string si existe
        if "HORARIO" in df.columns:
            df["HORARIO"] = df["HORARIO"].astype(str)

        # 6. Calcular Duración en Horas
        # Necesitamos objetos datetime/timedelta para restar
        try:
            # Convertir a datetime completo (usando fecha dummy) para poder restar
            # Asumimos que HORA_INICIO y FIN están en formato HH:MM o HH:MM:SS
            def to_td(h_str):
                try:
                    return pd.to_datetime(str(h_str), format="%H:%M:%S").time()
                except:
                    try: 
                        return pd.to_datetime(str(h_str), format="%H:%M").time()
                    except:
                        return None

            # Vectorizado es más rápido, pero con formatos mixtos es difícil.
            # Usaremos pd.to_datetime con errors='coerce' sobre strings limpios
            
            # Asegurar formato HH:MM:SS para facilitar
            s_ini = pd.to_datetime(df["HORA_INICIO"], format='%H:%M:%S', errors='coerce')
            s_fin = pd.to_datetime(df["HORA_FIN"], format='%H:%M:%S', errors='coerce')
            
            # Si falló, intentar inferir
            if s_ini.isna().all():
                 s_ini = pd.to_datetime(df["HORA_INICIO"], errors='coerce')
            if s_fin.isna().all():
                 s_fin = pd.to_datetime(df["HORA_FIN"], errors='coerce')

            df["Duracion_Horas"] = (s_fin - s_ini).dt.total_seconds() / 3600.0
            
            # Limpiar negativos o nulos
            df["Duracion_Horas"] = df["Duracion_Horas"].fillna(0)
            df.loc[df["Duracion_Horas"] < 0, "Duracion_Horas"] = 0
            
        except Exception as e:
            # Si falla el cálculo, dejar en 0 para no romper
            df["Duracion_Horas"] = 0.0
            print(f"Warning: No se pudo calcular duración: {e}")

        return df
    except Exception as e:
        # Re-lanzar la excepción para que sea manejada por la app principal
        raise Exception(f"Error en utils.load_data: {str(e)}")

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
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos_Completos')
        
        # Resumen por coord
        resumen = df.groupby('COORDINADORA RESPONSABLE').size().reset_index(name='Total Clases')
        resumen.to_excel(writer, index=False, sheet_name='Resumen_Coordinadoras')
        
    return output.getvalue()
