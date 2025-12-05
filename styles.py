# styles.py - Versión corregida
APP_STYLE = """
<style>
    /* Fondo principal más claro */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Mejorar visibilidad de textos */
    .stMarkdown, .stText, .stDataFrame {
        color: #262730 !important;
    }
    
    /* Cards con buen contraste */
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Sidebar más claro */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    
    /* Mejorar inputs */
    .stSelectbox > div > div, 
    .stMultiSelect > div > div {
        background-color: white !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Texto negro en inputs */
    .stSelectbox span, 
    .stMultiSelect span {
        color: #212529 !important;
    }
    
    /* Mejorar tabs */
    button[data-baseweb="tab"] {
        color: #495057 !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0d6efd !important;
        font-weight: 600;
    }
    
    /* Metrics visibles */
    [data-testid="stMetricValue"] {
        color: #0d6efd !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #495057 !important;
    }
</style>
"""

# Helper para tarjetas - mantener igual
def card_start():
    return '<div class="card">'
 
def card_end():
    return '</div>'

CUSTOM_LOADER = """
<div class="loader-container">
<div class="custom-loader"></div>
<div class="loader-text">Procesando datos...</div>
</div>
"""
