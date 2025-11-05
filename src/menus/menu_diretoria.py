import streamlit as st
from .dashboard import menu_dashboard

def menu_diretoria():
    """Menu para diretoria com abas"""
    st.markdown("### Painel Diretoria")
    
    # Abas como no master
    tab1, tab2 = st.tabs(["Minha Área", "Relatórios"])
    
    with tab1:
        _menu_minha_area_diretoria()
    
    with tab2:
        menu_dashboard()

def _menu_minha_area_diretoria():
    """Área pessoal do diretor"""
    user = st.session_state.user
    
    st.markdown("#### Minha Área")
    st.markdown(f"**Diretor:** {user['nome']}")
    st.markdown(f"**Setor:** {user['setor']}")
    st.markdown(f"**Email:** {user['email']}")
    
    st.markdown("---")
    
    # Saldo atual
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Meu Saldo Atual", f"{user['saldo_ferias']} dias")
    
    with col2:
        st.metric("Função", user['funcao'])
    
    st.markdown("---")
    
    # Informações pessoais de férias
    user_id = user["id"]
    
    try:
        ferias_list = st.session_state.ferias_db.get_ferias_usuario(user_id)
        
        # Converter lista para DataFrame se necessário
        if isinstance(ferias_list, list):
            if not ferias_list:
                st.info("Nenhuma férias cadastrada")
                return
            import pandas as pd
            ferias_df = pd.DataFrame(ferias_list)
        else:
            ferias_df = ferias_list
            if ferias_df is None or ferias_df.empty:
                st.info("Nenhuma férias cadastrada")
                return
        
        st.markdown("##### Minhas Férias")
        
        # Formatar datas
        ferias_display = ferias_df.copy()
        ferias_display['data_inicio'] = ferias_df['data_inicio'].apply(
            lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
        )
        ferias_display['data_fim'] = ferias_df['data_fim'].apply(
            lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
        )
        
        st.dataframe(
            ferias_display[['data_inicio', 'data_fim', 'dias_utilizados', 'status']],
            column_config={
                'data_inicio': 'Data Início',
                'data_fim': 'Data Fim', 
                'dias_utilizados': 'Dias',
                'status': 'Status'
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas das férias
        dias_aprovados = ferias_df[ferias_df['status'] == 'Aprovado']['dias_utilizados'].sum()
        st.info(f"Total de dias utilizados: {dias_aprovados} dias")
                
    except Exception as e:
        st.error(f"Erro ao carregar informações pessoais: {str(e)}")
        st.info("Verifique se você possui férias cadastradas no sistema")