"""
Componentes de Interface - Elementos reutilizáveis da UI

Este módulo contém componentes visuais reutilizáveis,
separados da lógica de negócio.
"""

import streamlit as st
import os
from .security import sanitize_html, safe_format_html


def create_header(empresa: str, sistema: str, logo_path: str = None):
    """
    Cria cabeçalho padrão da aplicação.
    
    Args:
        empresa: Nome da empresa
        sistema: Nome do sistema
        logo_path: Caminho para o logo (opcional)
    """
    try:
        st.markdown(
            f'<div style="text-align: center; margin-bottom: 30px;"><h1>{empresa}</h1><h3 style="color: #666;">{sistema}</h3></div>',
            unsafe_allow_html=True
        )
        
    except Exception as e:
        safe_html = safe_format_html("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>{empresa}</h1>
            <h3 style="color: #666;">{sistema}</h3>
        </div>
        """, empresa=empresa, sistema=sistema)
        st.markdown(safe_html, unsafe_allow_html=True)


def create_metric_card(titulo: str, valor: str, delta: str = None, help_text: str = None):
    """
    Cria card de métrica personalizado.
    
    Args:
        titulo: Título da métrica
        valor: Valor principal
        delta: Variação (opcional)
        help_text: Texto de ajuda (opcional)
    """
    st.metric(
        label=titulo,
        value=valor,
        delta=delta,
        help=help_text
    )


def create_info_card(titulo: str, conteudo: str, tipo: str = "info"):
    """
    Cria card informativo.
    
    Args:
        titulo: Título do card
        conteudo: Conteúdo do card
        tipo: Tipo do card (info, success, warning, error)
    """
    if tipo == "success":
        st.success(f"**{titulo}**\n\n{conteudo}")
    elif tipo == "warning":
        st.warning(f"**{titulo}**\n\n{conteudo}")
    elif tipo == "error":
        st.error(f"**{titulo}**\n\n{conteudo}")
    else:
        st.info(f"**{titulo}**\n\n{conteudo}")


def create_status_badge(status: str) -> str:
    """
    Cria badge visual para status.
    
    Args:
        status: Status a ser exibido
        
    Returns:
        HTML do badge
    """
    colors = {
        "Aprovada": "#28a745",
        "Pendente": "#ffc107", 
        "Cancelada": "#6c757d",
        "Rejeitada": "#dc3545"
    }
    
    color = colors.get(status, "#6c757d")
    
    return safe_format_html("""
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    ">{status}</span>
    """, color=color, status=status)


def show_loading_spinner(texto: str = "Carregando..."):
    """
    Mostra spinner de carregamento.
    
    Args:
        texto: Texto a ser exibido
    """
    with st.spinner(texto):
        pass


def create_confirmation_dialog(titulo: str, mensagem: str, key: str) -> bool:
    """
    Cria diálogo de confirmação.
    
    Args:
        titulo: Título do diálogo
        mensagem: Mensagem de confirmação
        key: Chave única para o componente
        
    Returns:
        True se confirmado, False caso contrário
    """
    st.warning(f"**{titulo}**")
    st.write(mensagem)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Confirmar", key=f"confirm_{key}", type="primary"):
            return True
    
    with col2:
        if st.button("Cancelar", key=f"cancel_{key}"):
            return False
    
    return False