APP_STYLE = """
<style>
    /* ===== RESET SEGURO ===== */
    * {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* ===== TARJETAS CON TÍTULOS DE ALTO CONTRASTE ===== */
    div.card {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    /* ===== TÍTULOS DE SECCIONES EN TARJETAS ===== */
    /* Títulos principales dentro de cards (h3, h4) - FONDO OSCURO, TEXTO CLARO */
    div.card h3 {
        background-color: #1e3a8a !important;  /* Azul oscuro profesional */
        color: white !important;
        padding: 12px 16px !important;
        margin: -20px -20px 20px -20px !important;
        border-radius: 12px 12px 0 0 !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        border-bottom: 3px solid #3b82f6 !important;
    }
    
    div.card h4 {
        background-color: #2563eb !important;  /* Azul más claro */
        color: white !important;
        padding: 10px 14px !important;
        margin: 0 0 15px 0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Subtítulos (h5, h6) - menos prominentes pero visibles */
    div.card h5 {
        color: #1e40af !important;
        border-left: 4px solid #3b82f6 !important;
        padding-left: 12px !important;
        margin: 15px 0 10px 0 !important;
        font-weight: 600 !important;
    }
    
    div.card h6 {
        color: #374151 !important;
        font-weight: 600 !important;
        margin: 10px 0 !important;
    }
    
    /* ===== TÍTULOS DE GRÁFICOS PLOTLY ===== */
    /* Título principal del gráfico */
    .gtitle {
        fill: #1e3a8a !important;  /* Mismo azul oscuro que los títulos de tarjetas */
        color: #1e3a8a !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }
    
    /* Títulos de ejes */
    .xtitle, .ytitle {
        fill: #4b5563 !important;
        color: #4b5563 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Leyendas */
    .legendtext {
        fill: #374151 !important;
        color: #374151 !important;
        font-weight: 500 !important;
    }
    
    /* ===== FILTROS CON MEJOR CONTRASTE ===== */
    /* Etiquetas de filtros (Año, Mes, Coordinadora, etc.) */
    .stMultiSelect > label,
    .stSelectbox > label,
    .stSlider > label {
        color: #1e3a8a !important;  /* Azul oscuro para mejor contraste */
        font-weight: 700 !important;
        font-size: 15px !important;
        margin-bottom: 10px !important;
        display: block !important;
        background-color: #f8fafc !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* ===== TÍTULOS PRINCIPALES DE PÁGINA ===== */
    /* Títulos h1 y h2 principales */
    h1 {
        color: #1e3a8a !important;
        border-bottom: 3px solid #3b82f6 !important;
        padding-bottom: 10px !important;
        margin-bottom: 25px !important;
        font-weight: 800 !important;
    }
    
    h2 {
        color: #2563eb !important;
        border-left: 5px solid #60a5fa !important;
        padding-left: 15px !important;
        margin: 25px 0 15px 0 !important;
        font-weight: 700 !important;
    }
    
    /* ===== TÍTULOS EN TABS ===== */
    /* Para los títulos dentro de cada tab */
    section[data-testid="stTabPanel"] h2 {
        background-color: #f0f9ff !important;
        color: #0369a1 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        border: 1px solid #bae6fd !important;
    }
    
    section[data-testid="stTabPanel"] h3 {
        color: #1e40af !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #dbeafe !important;
        margin-bottom: 20px !important;
    }
    
    /* ===== ESPECÍFICO PARA "VISIÓN GLOBAL" ===== */
    /* El título "Visión Global" y su contenido */
    div[data-testid="stVerticalBlock"]:has(> div > h2:contains("Visión Global")) {
        background-color: #f8fafc !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* El gráfico de Visión Global */
    div:has(> div > div > .plotly-graph-div:has(~ div:contains("Evolución de Clases"))) {
        background-color: white !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    /* ===== MEJORAR CONTRASTE EN TODOS LOS TEXTOS ===== */
    /* Texto normal dentro de tarjetas */
    div.card p,
    div.card span,
    div.card div {
        color: #374151 !important;
        line-height: 1.5 !important;
    }
    
    /* ===== OVERRIDE ESPECÍFICO PARA TÍTULOS OSCUROS ===== */
    /* Si algún título sigue siendo oscuro, forzar blanco */
    h1, h2, h3, h4, h5, h6 {
        text-shadow: 0 1px 1px rgba(255,255,255,0.8) !important;
    }
    
    /* ===== TEXTO EN GRÁFICOS ===== */
    /* Asegurar que todo texto en gráficos sea visible */
    .main-svg text {
        fill: #374151 !important;
        font-weight: 500 !important;
    }
    
    /* ===== COLORES DE SERIES EN GRÁFICOS ===== */
    /* Mejorar visibilidad de leyendas y series */
    .traces:not(.pie) .legendtoggle {
        fill: #3b82f6 !important;
    }
    
    /* ===== BOTONES CON MEJOR CONTRASTE ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2) !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a, #2563eb) !important;
        box-shadow: 0 4px 8px rgba(30, 64, 175, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ===== INPUTS VISIBLES ===== */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 2px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    
    /* Placeholder visible */
    div[data-baseweb="select"] > div > div[aria-live="polite"] {
        color: #6b7280 !important;
        font-style: italic !important;
    }
    
    /* ===== SCROLLBAR ESTILIZADA ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #94a3b8;
        border-radius: 5px;
        border: 2px solid #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
</style>
"""
