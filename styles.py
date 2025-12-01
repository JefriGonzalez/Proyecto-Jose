# styles.py

APP_STYLE = """
    <style>
    /* Importar fuente Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
 
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
 
    /* Contenedor principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
 
    /* Tarjetas de métricas (Cards) - Adaptable */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05); /* Sutil en dark mode, invisible en light */
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 700;
    }
 
    /* Títulos y Headers */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
"""
 
 
