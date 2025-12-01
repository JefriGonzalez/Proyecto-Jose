# utils.py

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
            st.error("❌ Formato no reconocido")
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

        # Correcciones específicas
        if "DIA_SEMANA" in df.columns:
            df = df.rename(columns={"DIA_SEMANA": "Dia_Semana"})
        if "DIAS_FECHAS" in df.columns:
            df = df.rename(columns={"DIAS_FECHAS": "DIAS/FECHAS"})

        # ------------------------------------------------------
        # CONVERTIR FECHAS
        # ------------------------------------------------------
        if "DIAS/FECHAS" in df.columns:
            df["DIAS/FECHAS"] = pd.to_datetime(df["DIAS/FECHAS"], errors="coerce", dayfirst=True)
        else:
            st.error("❌ El archivo no contiene la columna DIAS/FECHAS")
            return None

        # ------------------------------------------------------
        # MODALIDAD CALCULADA (si no existe)
        # ------------------------------------------------------
        if "Modalidad_Calc" not in df.columns:
            if "MODALIDAD" in df.columns:
                df["Modalidad_Calc"] = df["MODALIDAD"]
            else:
                df["Modalidad_Calc"] = "Sin dato"

        # ------------------------------------------------------
        # CAMPOS CRÍTICOS SIN NAN
        # ------------------------------------------------------
        campos = [
            "SEDE", "Modalidad_Calc",
            "COORDINADORA_RESPONSABLE",
            "PROGRAMA", "Dia_Semana",
            "ASIGNATURA"
        ]
        for c in campos:
            if c in df.columns:
                df[c] = df[c].fillna("Por definir")

        return df

    except Exception as e:
        st.error(f"❌ Error cargando archivo: {e}")
        return None
