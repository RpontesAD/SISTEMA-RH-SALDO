"""
Estilos personalizados para botões
"""
import streamlit as st

def apply_button_styles():
    """Aplica estilos personalizados aos botões - cor dourada"""
    st.markdown("""
    <style>
    /* Botões primários (amarelos) com texto preto */
    div[data-testid="stButton"] > button[kind="primary"],
    .stButton > button[kind="primary"],
    button[kind="primary"] {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Forçar cor preta em botões com fundo dourado */
    button[style*="background-color: rgb(255, 215, 0)"],
    button[style*="background-color: #ffd700"] {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)