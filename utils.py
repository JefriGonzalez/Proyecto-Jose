# utils.py

import pandas as pd
import streamlit as st
from io import BytesIO

# ==========================================================
# CARGAR ARCHIVOS (Excel o CSV)
# ==========================================================

def load_data(file):
    """
    Carga archivos Excel o CSV.
    Acepta:
    - UploadedFile de Streamlit
    - FileLike(BytesIO) de URLs
    - Paths locales a archivos
    """

    try:
        name = file.name.lower()

        # Excel
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(file)
        # CSV
        elif name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8")
        else:
            st.error("Formato de archivo no reconocido. Debe ser CSV o Excel.")
            return None

        # Conversión segura de fecha si existe la columna
        for col in df.columns:
            if "fecha" in col.lower() or "dia" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="ignore")
                except:
                    pass

        return df

    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return None


# ==========================================================
# GENERAR REPORTE EXCEL COMPLETO
# ==========================================================

def generate_excel_report(df):
    """
    Genera un archivo Excel en memoria
    para el botón de descarga del sidebar.
    """
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")
        return output.getvalue()
    except Exception as e:
        st.error(f"Error generando Excel: {e}")
        return None


# ==========================================================
# RESET DE FILTROS
# ==========================================================

def reset_filters():
    """
    Limpia el estado de los filtros de Streamlit.
    Funciona reiniciando el estado de sesión.
    """
    keys = list(st.session_state.keys())
    for k in keys:
        del st.session_state[k]
