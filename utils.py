import pandas as pd
import streamlit as st
from io import BytesIO

def load_data(file):
    try:
        name = file.name.lower()

        # Leer archivo
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(file, dtype=str)
        elif name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8", dtype=str)
        else:
            st.error("❌ Formato no reconocido (solo Excel o CSV)")
            return None

        df = df.convert_dtypes()

        # ------------------------------------------------------
        # NORMALIZAR NOMBRES DE COLUMNAS
        # ------------------------------------------------------
        df.columns = (
            df.columns
            .str.strip()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.replace("/", "_")
        )

        # ASÍ QUEDAN → DIAS_FECHAS, DIA_SEMANA, etc.

        # ------------------------------------------------------
        # Renombrar a los nombres EXACTOS que usa Prueba3.py
        # ------------------------------------------------------
        rename_map = {
            "DIAS_FECHAS": "DIAS/FECHAS",
            "DIA_SEMANA": "Dia_Semana",
        }

        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # ------------------------------------------------------
        # CONVERTIR FECHAS
        # ------------------------------------------------------
        if "DIAS/FECHAS" in df.columns:
            df["DIAS/FECHAS"] = pd.to_datetime(df["DIAS/FECHAS"], errors="coerce", dayfirst=True)
        else:
            st.error("❌ El archivo no contiene la columna 'DIAS/FECHAS'")
            return None

        # ------------------------------------------------------
        # MODALIDAD CALCULADA
        # ------------------------------------------------------
        if "Modalidad_Calc" not in df.columns:
            if "MODALIDAD" in df.columns:
                df["Modalidad_Calc"] = df["MODALIDAD"]
            else:
                df["Modalidad_Calc"] = "Sin dato"

        # ------------------------------------------------------
        # CAMPOS CRÍTICOS SIN NAN
        # ------------------------------------------------------
        criticos = [
            "SEDE",
            "Modalidad_Calc",
            "COORDINADORA_RESPONSABLE",
            "PROGRAMA",
            "Dia_Semana",
            "ASIGNATURA"
        ]

        for c in criticos:
            if c in df.columns:
                df[c] = df[c].fillna("Por definir")

        return df

    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return None


# ==========================================================
# EXPORTAR EXCEL
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

