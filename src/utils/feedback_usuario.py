"""
Feedback para usuário 
"""

import streamlit as st

def mostrar_saldo_atual_vs_pendente(user_data, ferias_pendentes_dias=0):
    """
    Mostra comparação entre saldo atual e saldo considerando férias pendentes
    
    Args:
        user_data: Dados do usuário
        ferias_pendentes_dias: Dias de férias pendentes
    """
    saldo_atual = user_data.get('saldo_ferias', 0)
    saldo_pendente = max(0, saldo_atual - ferias_pendentes_dias)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Saldo Atual", f"{saldo_atual} dias")
    
    with col2:
        if ferias_pendentes_dias > 0:
            st.metric("Saldo após Pendentes", f"{saldo_pendente} dias", 
                     delta=f"-{ferias_pendentes_dias}")
        else:
            st.metric("Saldo após Pendentes", f"{saldo_pendente} dias")

def mostrar_feedback_operacao(sucesso, mensagem, tipo="info"):
    """
    Mostra feedback de operação
    
    Args:
        sucesso: Se a operação foi bem-sucedida
        mensagem: Mensagem a ser exibida
        tipo: Tipo do feedback
    """
    if sucesso:
        st.success(mensagem)
    else:
        st.error(mensagem)