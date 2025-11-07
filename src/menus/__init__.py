import streamlit as st
from .cadastro_colaborador import menu_cadastro_colaborador
from .gerenciar_ferias import menu_gerenciar_ferias
from .gerenciar_colaboradores import menu_gerenciar_colaboradores
from .dashboard import menu_dashboard
from .avisos import menu_avisos
from .renovacao_saldo import menu_renovacao_saldo

from .menu_colaborador import menu_colaborador
from .menu_diretoria import menu_diretoria
from .menu_coordenador import menu_coordenador
# Alertas removidos

def menu_rh():
    """Menu principal para RH (Master)"""
    st.markdown("### Painel Gestão de Pessoas - Acesso Master")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Cadastrar Colaborador",
        "Gerenciar Férias", 
        "Gerenciar Colaboradores",
        "Avisos",
        "Renovação Saldo",
        "Relatórios"
    ])

    with tab1:
        menu_cadastro_colaborador()

    with tab2:
        menu_gerenciar_ferias()

    with tab3:
        menu_gerenciar_colaboradores()

    with tab4:
        menu_avisos()

    with tab5:
        menu_renovacao_saldo()
    
    with tab6:
        menu_dashboard()

# Funções movidas para arquivos separados

__all__ = [
    'menu_cadastro_colaborador',
    'menu_gerenciar_ferias', 
    'menu_gerenciar_colaboradores',

    'menu_dashboard',
    'menu_rh',
    'menu_colaborador',
    'menu_diretoria',
    'menu_coordenador'
]