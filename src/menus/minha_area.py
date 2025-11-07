import streamlit as st
from datetime import datetime

def menu_minha_area():
    """Menu Minha Área para todos os usuários"""
    st.markdown("#### Minha Área")
    
    user = st.session_state.user
    
    # Informações pessoais
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Minhas Informações")
        st.write(f"**Nome:** {user['nome']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Setor:** {user['setor']}")
        st.write(f"**Função:** {user['funcao']}")
    
    with col2:
        st.markdown("##### Saldo de Férias")
        st.metric("Dias Disponíveis", f"{user['saldo_ferias']} dias")
    
    st.markdown("---")
    
    # Avisos
    st.markdown("##### Avisos")
    
    try:
        avisos = st.session_state.users_db.get_avisos_usuario(user['id'])
        
        if not avisos:
            st.info("Nenhum aviso disponível no momento.")
        else:
            for aviso in avisos:
                # Container para cada aviso
                with st.container():
                    col_aviso, col_status = st.columns([4, 1])
                    
                    with col_aviso:
                        # Título com indicador de não lido
                        if not aviso['lido']:
                            st.markdown(f"{aviso['titulo']}")
                        else:
                            st.markdown(f"{aviso['titulo']}")
                        
                        # Conteúdo
                        st.write(aviso['conteudo'])
                        
                        # Informações do aviso
                        data_criacao = aviso['data_criacao'].strftime("%d/%m/%Y às %H:%M")
                        st.caption(f"Por: {aviso['autor_nome']} • {data_criacao}")
                    
                    with col_status:
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
                    
                    st.markdown("---")
    
    except Exception as e:
        st.error("Erro ao carregar avisos")