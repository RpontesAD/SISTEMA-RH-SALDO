import streamlit as st

def menu_coordenador():
    """Menu para coordenadores com abas"""
    st.markdown("### Painel Coordenador")
    
    # Abas como no diretor
    tab1, tab2 = st.tabs(["Minha Área", "Meu Setor"])
    
    with tab1:
        _menu_minha_area_coordenador()
    
    with tab2:
        _menu_setor_coordenador()

def _menu_minha_area_coordenador():
    """Área pessoal do coordenador"""
    user = st.session_state.user
    
    st.markdown("#### Minha Área")
    st.markdown(f"**Coordenador:** {user['nome']}")
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

def _menu_setor_coordenador():
    """Relatórios do setor do coordenador"""
    user = st.session_state.user
    st.markdown(f"#### Colaboradores do Setor: {user['setor']}")

    users_list = st.session_state.users_db.get_users(setor=user["setor"])
    
    # Converter lista para DataFrame se necessário
    if isinstance(users_list, list):
        if not users_list:
            st.info("Nenhum colaborador encontrado no seu setor.")
            return
        import pandas as pd
        users_df = pd.DataFrame(users_list)
    else:
        users_df = users_list
        if users_df is None or users_df.empty:
            st.info("Nenhum colaborador encontrado no seu setor.")
            return

    if True:  # Sempre verdadeiro agora que verificamos acima
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total no Setor", str(len(users_df)))

        with col2:
            st.metric("Colaboradores Ativos", str(len(users_df)))

        with col3:
            saldo_medio = users_df["saldo_ferias"].mean()
            st.metric("Saldo Médio Setor", f"{saldo_medio:.1f} dias")

        st.dataframe(
            users_df[["nome", "email", "funcao", "saldo_ferias"]].rename(columns={
                "nome": "Nome",
                "email": "Email", 
                "funcao": "Função",
                "saldo_ferias": "Saldo Atual"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum colaborador encontrado no seu setor.") 