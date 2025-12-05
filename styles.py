# styles.py - Versión corregida completamente

APP_STYLE = """
<style>
    /* ===== RESET SEGURO ===== */
    /* NO tocar elementos base de Streamlit */
    
    /* ===== TARJETAS PERSONALIZADAS ===== */
    /* Solo aplica a elementos con clase .card */
    div.card {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    /* ===== TEXTOS DENTRO DE TARJETAS ===== */
    div.card h1,
    div.card h2,
    div.card h3,
    div.card h4,
    div.card h5,
    div.card h6,
    div.card p,
    div.card span,
    div.card div {
        color: #000000 !important;
    }
    
    /* ===== INPUTS VISIBLES ===== */
    /* Selectbox legible */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        color: #262730 !important;
        font-weight: 500 !important;
    }
    
    /* Texto dentro del selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Texto seleccionado visible */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* Dropdown menu visible */
    div[role="listbox"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Opciones del dropdown */
    li[role="option"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    li[role="option"]:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* ===== TÍTULOS DE GRÁFICOS PLOTLY ===== */
    /* Asegurar que los títulos de Plotly sean visibles */
    .gtitle, .xtitle, .ytitle {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* ===== TABS VISIBLES ===== */
    /* Tabs principales */
    button[data-baseweb="tab"] {
        color: #495057 !important;
        font-weight: 500 !important;
    }
    
    /* Tab activo */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0d6efd !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #0d6efd !important;
    }
    
    /* ===== METRICS VISIBLES ===== */
    [data-testid="stMetricValue"] {
        color: #0d6efd !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #495057 !important;
        font-size: 1rem !important;
    }
    
    /* ===== TEXT INPUTS ===== */
    input[type="text"],
    input[type="password"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* ===== DATA FRAME ===== */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    
    /* ===== BOTONES ===== */
    .stButton > button {
        background-color: #0d6efd !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }
    
    /* ===== ETIQUETAS DE FILTROS ===== */
    /* Esto es CRÍTICO - asegura que las etiquetas "Año", "Coordinadora", etc sean visibles */
    .stMultiSelect label,
    .stSelectbox label,
    .stSlider label,
    .stRadio label,
    .stCheckbox label {
        color: #262730 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    /* ===== PLACEHOLDER VISIBLE ===== */
    /* Texto "Seleccione una opción", "Todos", etc */
    div[data-baseweb="select"] div[aria-live="polite"] {
        color: #666666 !important;
    }
    
    /* ===== TAGS EN MULTISELECT ===== */
    /* Los tags seleccionados */
    [data-baseweb="tag"] {
        background-color: #0d6efd !important;
        color: white !important;
    }
    
    /* ===== SCROLLBAR SUAVE ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
"""

def card_start():
    """Inicia una tarjeta con buen contraste"""
    return '<div class="card">'

def card_end():
    """Cierra una tarjeta"""
    return '</div>'

CUSTOM_LOADER = """
<div style="
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 150px;
    width: 100%;
    margin: 20px 0;
">
    <div style="
        width: 48px;
        height: 48px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #0d6efd;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    "></div>
    <div style="
        margin-top: 15px;
        font-family: Arial, sans-serif;
        font-size: 16px;
        color: #262730;
        font-weight: 600;
    ">Procesando datos...</div>
</div>
<style>
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
"""
