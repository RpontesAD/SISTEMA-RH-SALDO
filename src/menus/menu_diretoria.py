import streamlit as st
from .dashboard import menu_dashboard

def menu_diretoria():
    """Menu para diretoria com abas"""
    st.markdown("### Painel Diretoria")
    
    # Abas como no master
    tab1, tab2, tab3 = st.tabs(["Minha Área", "Editar Dados", "Relatórios"])
    
    with tab1:
        _menu_minha_area_diretoria()
    
    with tab2:
        _mostrar_edicao_dados_diretoria()
    
    with tab3:
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
def _mostrar_edicao_dados_diretoria():
    """Mostra formulário de edição de dados pessoais para diretor"""
    from ..utils.constants import SETORES, FUNCOES
    
    user = st.session_state.user
    st.markdown("### Editar Meus Dados")
    
    with st.form("form_edicao_diretor"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Nome", value=user['nome'], disabled=True, help="Nome não pode ser alterado")
            email = st.text_input("Email", value=user['email'])
        
        with col2:
            
            nova_senha = st.text_input("🔒 Nova Senha (deixe vazio para manter)", type="password")
            confirmar_senha = st.text_input("🔒 Confirmar Nova Senha", type="password")
        
        if st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True):
            # Validar senhas se fornecidas
            if nova_senha or confirmar_senha:
                if nova_senha != confirmar_senha:
                    st.error("❌ Senhas não coincidem")
                    return
                if len(nova_senha) < 6:
                    st.error("❌ Senha deve ter pelo menos 6 caracteres")
                    return
            
            try:
                # Atualizar apenas email e senha
                user_id = int(user['id'])
                resultado = st.session_state.users_db.update_user(
                    user_id=user_id,
                    nome=user['nome'],  # Nome não alterado
                    email=email.strip().lower(),
                    setor=user['setor'],
                    funcao=user['funcao'],
                    nivel_acesso=user['nivel_acesso'],
                    saldo_ferias=user['saldo_ferias']
                )
                
                if resultado:
                    # Atualizar senha se fornecida
                    if nova_senha:
                        import bcrypt
                        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        resultado_senha = st.session_state.users_db._execute_query(
                            "UPDATE usuarios SET senha_hash=%s WHERE id=%s", 
                            (senha_hash, user_id)
                        )
                        if not resultado_senha:
                            st.error("❌ Erro ao atualizar senha")
                            return
                    
                    # Atualizar sessão
                    st.session_state.user.update({
                        'email': email.strip().lower()
                    })
                    
                    st.success("✅ Dados atualizados com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar dados")
                    
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")