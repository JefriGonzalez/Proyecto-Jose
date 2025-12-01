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
    Conversión garantizada de fechas, incluyendo DIAS/FECHAS.
    """
    try:
        name = file.name.lower()

        # Detectar formato
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(file, dtype=str)
        elif name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8", dtype=str)
        else:
            st.error("❌ Formato de archivo no reconocido. Debe ser CSV o Excel.")
            return None

        # Convertir a DataFrame tipado
        df = df.convert_dtypes()

        # ------------------------------------------------------
        # CONVERSIÓN FIJA DE LA COLUMNA CRÍTICA: DIAS/FECHAS
        # ------------------------------------------------------
        fecha_cols = [c for c in df.columns if "fecha" in c.lower() or "dia" in c.lower()]

        for col in fecha_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

            # Si hay fechas invalidas avisamos (solo una vez)
            if df[col].isna().sum() > 0:
                st.warning(
                    f"⚠️ {df[col].isna().sum()} valores en la columna '{col}' no pudieron convertirse a fecha."
                )

        # Asegurar que DIAS/FECHAS exista como datetime si está presente
        if "DIAS/FECHAS" in df.columns:
            df["DIAS/FECHAS"] = pd.to_datetime(df["DIAS/FECHAS"], errors="coerce", dayfirst=True)

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

        # Quitar espacios extra en los nombres de columna
        df.columns = [c.strip() for c in df.columns]

        return df

    except Exception as e:
        st.error(f"❌ Error cargando archivo: {e}")
        return None


# ==========================================================
# EXPORTAR REPORTE A EXCEL
# ==========================================================

def generate_excel_report(df):
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]
