import streamlit as st


def apply_custom_css():
    st.markdown(
        """
    <style>
    .stApp {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    .main {
        background-color: #1a1a1a !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2a2a2a, #252525);
        border: 1px solid #404040;
        padding: 1.2rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.6rem 0;
        color: #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    .info-card {
        background: linear-gradient(135deg, #2a2a2a, #252525);
        border: 1px solid #404040;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #e0e0e0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    .success-card {
        background: linear-gradient(135deg, #2a3a2a, #253525);
        border: 1px solid #405040;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #e0f0e0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #3a3a2a, #353525);
        border: 1px solid #505040;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #f0f0e0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    .error-card {
        background: linear-gradient(135deg, #3a2a2a, #352525);
        border: 1px solid #504040;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #f0e0e0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f0f0f0 !important;
    }
    
    .stMarkdown {
        color: #e0e0e0;
    }
    
    .stDataFrame {
        background-color: #2a2a2a;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #222222 !important;
    }
    
    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #1e1e1e !important;
    }
    
    .stSelectbox > div > div {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #606060 !important;
        box-shadow: 0 0 0 2px rgba(96,96,96,0.2) !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #606060 !important;
        box-shadow: 0 0 0 2px rgba(96,96,96,0.2) !important;
    }
    
    .stDateInput > div > div > input {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #606060 !important;
        box-shadow: 0 0 0 2px rgba(96,96,96,0.2) !important;
    }
    
    /* Botões com gradiente e animações suaves */
    button {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }

    button:hover {
        background: linear-gradient(135deg, #505050, #454545) !important;
        color: #f0f0f0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #505050, #454545) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stFormSubmitButton button:hover {
        background: linear-gradient(135deg, #505050, #454545) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #2a2a2a !important;
    }
    
    .sidebar {
        background-color: #1a1a1a !important;
    }
    
    /* Cores suavizadas para todos os elementos */
    * {
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 1px solid #303030 !important;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }
    
    .stApp > div[data-testid="stDecoration"] {
        background-image: none !important;
    }
    
    /* Navegação com transições suaves */
    .stTabs [data-baseweb="tab"] {
        background: none !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        color: #d0d0d0 !important;
        padding: 10px 18px !important;
        transition: all 0.2s ease !important;
        border-radius: 4px 4px 0 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #707070 !important;
        color: #f0f0f0 !important;
        background: rgba(112,112,112,0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-bottom: 2px solid #606060 !important;
        color: #f0f0f0 !important;
        background: rgba(96,96,96,0.1) !important;
    }
    
    /* Botões com estilos unificados */
    button[kind="primary"],
    button[kind="secondary"],
    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primaryFormSubmit"],
    [data-testid="baseButton-secondaryFormSubmit"] {
        background: linear-gradient(135deg, #404040, #353535) !important;
        color: #e0e0e0 !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    [data-testid="baseButton-primary"]:hover,
    [data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #505050, #454545) !important;
        color: #f0f0f0 !important;
        border: 1px solid #666666 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Melhorias gerais de espaçamento */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2a2a2a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #505050;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #606060;
    } 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #505050;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #606060;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
