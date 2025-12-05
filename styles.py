# Helper para crear tarjetas
def card_start():
    return '<div class="card">'
 
def card_end():
    return '</div>'

APP_STYLE = """
<style>
    /* Global Background - LIGHT THEME */
    .stApp {
        background-color: #F0F2F6;
        color: #262730;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #D6D6D9;
    }
    /* Card Style */
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #E6E6EA;
    }
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0E1117 !important;
        font-family: 'Inter', sans-serif;
    }
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: transparent;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stMetricValue"] {
        color: #009688 !important; /* Teal for good contrast on white */
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #262730 !important; /* Dark grey for readability */
    }
    /* Dataframe */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E6E6EA;
    }
    /* Custom Loader */
    .loader-container {
        display: flex;
        flex-direction: column;
        justify_content: center;
        align-items: center;
        height: 100px;
        width: 100%;
        margin-top: 20px;
    }
    .custom-loader {
        width: 48px;
        height: 48px;
        border: 5px solid #F0F2F6;
        border-bottom-color: #009688; /* Teal */
        border-radius: 50%;
        display: inline-block;
        box-sizing: border-box;
        animation: rotation 1s linear infinite;
    }
    @keyframes rotation {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .loader-text {
        margin-top: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        color: #262730;
        font-weight: 600;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    /* High Contrast Inputs (Maintained as requested) */
    /* Container of the select/multiselect */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #009688 !important; /* Match Teal theme */
        color: #000000 !important;
    }
    /* Text inside the box */
    div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    /* Dropdown menu items */
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 2px solid #009688 !important;
    }
    li[data-baseweb="menu-item"] {
        color: #000000 !important;
    }
    /* Selected tags in multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #009688 !important; /* Teal tags */
        color: #FFFFFF !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }
    /* Standard Text Inputs */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #009688 !important;
    }
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D6D6D9;
    }
</style>
"""
 
CUSTOM_LOADER = """
<div class="loader-container">
<div class="custom-loader"></div>
<div class="loader-text">Procesando datos...</div>
</div>
"""
 
# Helper para crear tarjetas
def card_start():
    return '<div class="card">'
 
def card_end():
    return '</div>'
