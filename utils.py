# utils.py

import pandas as pd
import streamlit as st
from io import BytesIO

# ==========================================================
# CARGA ROBUSTA DE ARCHIVOS (Excel / CSV)
# ==========================================================

def load_data(file):
    """
    Carga archivos Excel o CSV.
    - Acepta archivos subidos (UploadedFile)
    - Acepta archivos descargados desde URL (BytesIO con .name)
    - Acepta paths locales
    Incluye:
    - Conversión automática de fechas
    - Limpieza de NaN en columnas críticas
    """

    try:
        name = file.name.lower()

        # Detectar formato
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(file, dtype=str)   # leer todo como texto inicialmente
        elif name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8", dtype=str)
        else:
            st.error("❌ Formato de archivo no reconocido. Debe ser CSV o Excel.")
            return None

        # Convertir a DataFrame correctamente tipado
        df = df.convert_dtypes()

        # ------------------------------------------------------
        # CONVERSIÓN AUTOMÁTICA DE FECHAS
        # ------------------------------------------------------
        for col in df.columns:
            if "fecha" in col.lower() or "dia" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="ignore", dayfirst=True)
                except:
                    pass

        # ------------------------------------------------------
        # REEMPLAZO AUTOMÁTICO DE NaN EN COLUMNAS CLAVE
        # ------------------------------------------------------
        cols_replace_nan = [
            "SEDE",
            "Modalidad_Calc",
            "COORDINADORA RESPONSABLE",
            "PROGRAMA",
            "Dia_Semana",
            "ASIGNATURA"
        ]

        for col in cols_replace_nan:
            if col in df.columns:
                df[col] = df[col].fillna("Por definir")

        # Eliminación de espacios extra (muy común en Excel)
        df.columns = [c.strip() for c in df.columns]

        return df

    except Exception as e:
        st.error(f"❌ Error cargando archivo: {e}")
        return None


# ==========================================================
# EXPORTAR REPORTE A EXCEL
# ==========================================================

def generate_excel_report(df):
    """
    Genera un archivo Excel para descarga.
    """
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")
        return output.getvalue()

    except Exception as e:
        st.error(f"❌ Error generando Excel: {e}")
        return None


# ==========================================================
# RESET DE FILTROS DE STREAMLIT
# ==========================================================

def reset_filters():
    """
    Limpia los filtros almacenados en session_state.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]


