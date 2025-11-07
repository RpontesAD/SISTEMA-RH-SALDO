import streamlit as st
from ..utils.constants import SETORES, FUNCOES

def menu_colaborador():
    """Menu para colaboradores - área pessoal com edição"""
    user = st.session_state.user
    
    # Abas do colaborador
    tab1, tab2 = st.tabs(["Minha Área", "Editar Dados"])
    
    with tab1:
        _mostrar_area_pessoal(user)
    
    with tab2:
        _mostrar_edicao_dados(user)

def _mostrar_area_pessoal(user):
    """Mostra área pessoal do colaborador"""
    st.markdown("### Minha Área")
    st.markdown(f"**Colaborador:** {user['nome']}")
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
    
    st.markdown("---")
    
    # Seção de Avisos
    st.markdown("##### Avisos")
    
    try:
        avisos = st.session_state.users_db.get_avisos_usuario(user['id'])
        
        if not avisos:
            st.info("Nenhum aviso disponível no momento.")
        else:
            for aviso in avisos:
                with st.container():
                    col_aviso, col_status = st.columns([4, 1])
                    
                    with col_aviso:
                        # Título simples
                        if not aviso['lido']:
                            st.markdown(f"**{aviso['titulo']}** (novo)")
                        else:
                            st.markdown(f"**{aviso['titulo']}**")
                        
                        # Conteúdo
                        st.write(aviso['conteudo'])
                        
                        # Informações de publicação
                        data_criacao = aviso['data_criacao'].strftime("%d/%m/%Y")
                        st.caption(f"Por {aviso['autor_nome']} em {data_criacao}")
                    
                    with col_status:
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if not aviso['lido']:
                                if st.button("Marcar como Lido", key=f"lido_{aviso['id']}", type="secondary"):
                                    sucesso = st.session_state.users_db.marcar_aviso_lido(aviso['id'], user['id'])
                                    if sucesso:
                                        st.rerun()
                            else:
                                st.success("Lido")
                                if aviso['data_leitura']:
                                    data_leitura = aviso['data_leitura'].strftime("%d/%m/%Y")
                                    st.caption(f"em {data_leitura}")
                        
                        with col_btn2:
                            if st.button("Ocultar", key=f"remover_{aviso['id']}", help="Ocultar aviso", type="secondary"):
                                sucesso = st.session_state.users_db.remover_aviso_usuario(aviso['id'], user['id'])
                                if sucesso:
                                    st.rerun()
                    
                    st.markdown("---")
    
    except Exception as e:
        st.error("Erro ao carregar avisos")
def _mostrar_edicao_dados(user):
    """Mostra formulário de edição de dados pessoais"""
    st.markdown("### Editar Meus Dados")
    
    with st.form("form_edicao_colaborador"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Nome", value=user['nome'], disabled=True, help="Nome não pode ser alterado")
            email = st.text_input("Email", value=user['email'])
        
        with col2:
            
            nova_senha = st.text_input("🔒 Nova Senha (deixe vazio para manter)", type="password")
            confirmar_senha = st.text_input("🔒 Confirmar Nova Senha", type="password")
        
        if st.form_submit_button(" Salvar Alterações", type="primary", use_container_width=True):
            # Validar senhas se fornecidas
            if nova_senha or confirmar_senha:
                if nova_senha != confirmar_senha:
                    st.error("❌ Senhas não coincidem")
                    return
                if len(nova_senha) < 6:
                    st.error("❌ Senha deve ter pelo menos 6 caracteres")
                    return
            
            try:
                from ..services.colaboradores_service import ColaboradoresService
                service = ColaboradoresService(st.session_state.users_db)
                
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