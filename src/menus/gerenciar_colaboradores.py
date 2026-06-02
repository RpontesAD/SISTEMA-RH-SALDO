import streamlit as st
import pandas as pd
from datetime import datetime
from ..config import SETORES, FUNCOES

def menu_gerenciar_colaboradores():
    """Menu para gerenciar colaboradores"""
    st.markdown("#### Gerenciar Colaboradores")
    
    # Filtro por status
    col_status, col_space = st.columns([2, 3])
    with col_status:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Ativos", "Inativos", "Todos"],
            help="Escolha quais colaboradores visualizar"
        )
    
    # Buscar colaboradores baseado no filtro
    if status_filter == "Ativos":
        users_list = st.session_state.users_db.get_users(incluir_inativos=False)
    elif status_filter == "Inativos":
        # Buscar todos e filtrar apenas inativos
        all_users = st.session_state.users_db.get_users(incluir_inativos=True)
        users_list = [user for user in all_users if not user.get('ativo', True)]
    else:  # "Todos"
        users_list = st.session_state.users_db.get_users(incluir_inativos=True)
    
    # Verificar se retornou None ou lista válida
    if users_list is None:
        st.error("Erro ao carregar dados dos colaboradores")
        return
    
    # Converter lista para DataFrame
    if isinstance(users_list, list):
        if not users_list:
            st.warning("Nenhum colaborador cadastrado")
            return
        users_df = pd.DataFrame(users_list)
    else:
        users_df = users_list
        if users_df.empty:
            st.warning("Nenhum colaborador cadastrado")
            return
    
    # Filtros melhorados
    filtro_nome, filtro_setor, filtro_funcao, filtro_saldo = _mostrar_filtros_avancados(users_df)
    
    # Aplicar filtros
    df_filtrado = _aplicar_filtros(users_df, filtro_nome, filtro_setor, filtro_funcao, filtro_saldo)
   
    # Tabela principal com ações
    _mostrar_tabela_colaboradores(df_filtrado)

def _mostrar_filtros_avancados(users_df):
    """Filtros avançados e busca"""
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filtro_nome = st.text_input("Buscar Nome", key="busca_nome")
    
    with col2:
        filtro_setor = st.selectbox("Setor", ["Todos"] + SETORES, key="filtro_setor")
    
    with col3:
        filtro_funcao = st.selectbox("Função", ["Todos"] + FUNCOES, key="filtro_funcao")
    
    with col4:
        filtro_saldo = st.selectbox("Filtrar por Saldo", ["Todos", "Baixo (menor que 3 dias)", "Normal (3-8 dias)", "Alto (maior que 8 dias)"], key="filtro_saldo")
    
    return filtro_nome, filtro_setor, filtro_funcao, filtro_saldo

def _aplicar_filtros(users_df, filtro_nome, filtro_setor, filtro_funcao, filtro_saldo):
    """Aplica filtros selecionados"""
    df = users_df.copy()
    
    if filtro_nome:
        df = df[df['nome'].str.contains(filtro_nome, case=False, na=False)]
    
    if filtro_setor != 'Todos':
        df = df[df['setor'] == filtro_setor]
    
    if filtro_funcao != 'Todos':
        df = df[df['funcao'] == filtro_funcao]
    
    if filtro_saldo != 'Todos':
        if filtro_saldo == "Baixo (<3)":
            df = df[df['saldo_ferias'] < 3]
        elif filtro_saldo == "Normal (3-8)":
            df = df[(df['saldo_ferias'] >= 3) & (df['saldo_ferias'] <= 8)]
        elif filtro_saldo == "Alto (>8)":
            df = df[df['saldo_ferias'] > 8]
    
    return df

def _mostrar_tabela_colaboradores(df_filtrado):
    """Tabela principal com ações claras"""
    # Contar ativos e inativos
    if not df_filtrado.empty:
        ativos = len(df_filtrado[df_filtrado.get('ativo', True) == True])
        inativos = len(df_filtrado[df_filtrado.get('ativo', True) == False])
        status_info = f" ({ativos} ativos, {inativos} inativos)" if inativos > 0 else f" ({ativos} ativos)"
    else:
        status_info = ""
    
    st.markdown(f"##### Colaboradores ({len(df_filtrado)} encontrados){status_info}")
    
    if df_filtrado.empty:
        st.info("Nenhum colaborador encontrado com os filtros aplicados")
        return
    
    # Ordenar por nome
    df_sorted = df_filtrado.sort_values('nome').reset_index(drop=True)
    
    if len(df_sorted) > 0:
        nomes_ordenados = []
        for _, row in df_sorted.iterrows():
            nomes_ordenados.append(f"{row['nome']} - {row['setor']} ({row['saldo_ferias']} dias)")
        selected_index = st.selectbox(
            "Selecionar colaborador",
            options=range(len(nomes_ordenados)),
            format_func=lambda x: nomes_ordenados[x],
            key="selected_user"
        )
    else:
        selected_index = None
    
    if selected_index is not None and len(df_sorted) > 0:
        user_data = df_sorted.iloc[selected_index]
        _mostrar_acoes_colaborador(user_data)

def _mostrar_acoes_colaborador(user_data):
    """Ações claras para o colaborador selecionado"""
    st.markdown("---")
    st.markdown("##### Gerenciar Colaborador:")
    # Informações do colaborador
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Nome:** {user_data['nome']}")
        st.write(f"**Setor:** {user_data['setor']}")
    
    with col2:
        st.write(f"**Email:** {user_data['email']}")
        st.write(f"**Função:** {user_data['funcao']}")
    
    with col3:
        st.write(f"**Nível:** {user_data['nivel_acesso']}")
        st.write(f"**Saldo:** {user_data['saldo_ferias']} dias")
        
        # Mostrar status ativo/inativo
        ativo = user_data.get('ativo', True)
        if ativo:
            st.success("**Status:** Ativo")
        else:
            st.error("**Status:** Inativo")
    
    # Ações disponíveis
    st.markdown("---")
    st.markdown("##### Ações Disponíveis :")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Editar Dados", use_container_width=True):
            st.session_state.acao_colaborador = "editar"
            st.session_state.user_selecionado = user_data
            st.rerun()
    
    with col2:
        if st.button("Ajustar Saldo", use_container_width=True):
            st.session_state.acao_colaborador = "saldo"
            st.session_state.user_selecionado = user_data
            st.rerun()
    
    with col3:
        # Verificar se usuário está ativo
        ativo = user_data.get('ativo', True)
        if ativo:
            if st.button("Inativar", use_container_width=True, help="Inativa colaborador sem excluir dados"):
                st.session_state.acao_colaborador = "inativar"
                st.session_state.user_selecionado = user_data
                st.rerun()
        else:
            if st.button("Reativar", use_container_width=True, help="Reativa colaborador"):
                st.session_state.acao_colaborador = "reativar"
                st.session_state.user_selecionado = user_data
                st.rerun()
    
    with col4:
        if st.button("Excluir", use_container_width=True, type="secondary"):
            st.session_state.acao_colaborador = "excluir"
            st.session_state.user_selecionado = user_data
            st.rerun()
    
    # Executar ação selecionada
    if st.session_state.get('acao_colaborador'):
        _executar_acao(st.session_state.acao_colaborador, st.session_state.user_selecionado)

def _executar_acao(acao, user_data):
    """Executa a ação selecionada"""
    if acao == "editar":
        _formulario_edicao(user_data)
    elif acao == "saldo":
        _formulario_saldo(user_data)
    elif acao == "inativar":
        _confirmacao_inativacao(user_data)
    elif acao == "reativar":
        _confirmacao_reativacao(user_data)
    elif acao == "excluir":
        _confirmacao_exclusao(user_data)

def _formulario_edicao(user_data):
    """Formulário de edição melhorado"""
    st.markdown("---")
    st.markdown("### Editar Colaborador")
    
    with st.form("form_edicao"):
        col1, col2 = st.columns(2)

        # =========================
        # TRATAMENTO DA DATA
        # =========================
        admissao_atual = user_data.get("data_admissao")

        try:
            if isinstance(admissao_atual, str):
                admissao_atual = datetime.strptime(admissao_atual, "%Y-%m-%d").date()
            elif pd.notnull(admissao_atual):
                admissao_atual = pd.to_datetime(admissao_atual).date()
            else:
                admissao_atual = datetime.today().date()
        except:
            admissao_atual = datetime.today().date()

        with col1:
            nome = st.text_input("Nome", value=user_data['nome'])

            email = st.text_input("Email", value=user_data['email'])

            admissao = st.date_input(
                "ADMISSÃO",
                value=admissao_atual,
                format="DD/MM/YYYY"
            )

            try:
                setor_index = SETORES.index(user_data['setor'])
            except ValueError:
                setor_index = 0

            setor = st.selectbox(
                "Setor",
                SETORES,
                index=setor_index
            )

        with col2:
            try:
                funcao_index = FUNCOES.index(user_data['funcao'])
            except ValueError:
                funcao_index = 0

            funcao = st.selectbox(
                "Função",
                FUNCOES,
                index=funcao_index
            )

            niveis = ["colaborador", "coordenador", "diretoria", "master"]

            try:
                nivel_index = niveis.index(user_data['nivel_acesso'])
            except ValueError:
                nivel_index = 0

            nivel_acesso = st.selectbox(
                "Nível de Acesso",
                niveis,
                index=nivel_index
            )

            saldo_ferias = st.number_input(
                "Saldo de Férias",
                min_value=0,
                value=int(user_data['saldo_ferias'])
            )

            nova_senha = st.text_input(
                "🔒 Nova Senha (deixe vazio para manter)",
                type="password"
            )

            confirmar_senha = st.text_input(
                "🔒 Confirmar Nova Senha",
                type="password"
            )

        col_save, col_cancel = st.columns(2)

        with col_save:
            if st.form_submit_button(
                "Salvar Alterações",
                type="primary",
                use_container_width=True
            ):

                # =========================
                # VALIDAR SENHAS
                # =========================
                if nova_senha or confirmar_senha:
                    if nova_senha != confirmar_senha:
                        st.error("❌ Senhas não coincidem")
                        return

                    if len(nova_senha) < 6:
                        st.error("❌ Senha deve ter pelo menos 6 caracteres")
                        return

                try:
                    from ..services.colaboradores_service import ColaboradoresService

                    service = ColaboradoresService(
                        st.session_state.users_db
                    )

                    # =========================
                    # CONVERSÕES
                    # =========================
                    user_id = int(user_data['id'])

                    saldo_ferias_int = int(saldo_ferias)

                    admissao_formatada = admissao.strftime("%Y-%m-%d")

                    # =========================
                    # ATUALIZAR COLABORADOR
                    # =========================
                    resultado = service.atualizar_colaborador(
                        user_id,
                        nome,
                        email,
                        setor,
                        funcao,
                        nivel_acesso,
                        saldo_ferias_int,
                        admissao_formatada
                    )

                    if resultado["sucesso"]:

                        # =========================
                        # ATUALIZAR SENHA
                        # =========================
                        if nova_senha:
                            import bcrypt

                            senha_hash = bcrypt.hashpw(
                                nova_senha.encode('utf-8'),
                                bcrypt.gensalt()
                            ).decode('utf-8')

                            resultado_senha = st.session_state.users_db._execute_query(
                                "UPDATE usuarios SET senha_hash=%s WHERE id=%s",
                                (senha_hash, user_id)
                            )

                            if not resultado_senha:
                                st.error("❌ Erro ao atualizar senha")
                                return

                        st.success(f"✅ {resultado['mensagem']}")

                        _limpar_sessao()

                        st.rerun()

                    else:
                        st.error(f"❌ {resultado['erro']}")

                        if "saldo_corrigido" in resultado:
                            st.info(
                                f"💡 Saldo sugerido: "
                                f"{resultado['saldo_corrigido']} dias"
                            )

                except Exception as e:
                    st.error(
                        f"❌ Erro ao atualizar colaborador: {str(e)}"
                    )

        with col_cancel:
            if st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            ):
                _limpar_sessao()
                st.rerun()

def _formulario_saldo(user_data):
    """Formulário específico para ajuste de saldo"""
    st.markdown("---")
    st.markdown("### Ajustar Saldo de Férias")
    
    with st.form("form_saldo"):
        st.info(f"Colaborador: **{user_data['nome']}**")
        st.info(f"Saldo atual: **{user_data['saldo_ferias']} dias**")
        
        novo_saldo = st.number_input("Novo saldo (dias)", min_value=0, value=int(user_data['saldo_ferias']))
        
        if novo_saldo != user_data['saldo_ferias']:
            diferenca = novo_saldo - user_data['saldo_ferias']
            if diferenca > 0:
                st.success(f"Aumentará {diferenca} dias")
            else:
                st.warning(f"Diminuirá {abs(diferenca)} dias")
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.form_submit_button("Atualizar Saldo", type="primary", use_container_width=True):
                try:
                    from ..services.colaboradores_service import ColaboradoresService
                    service = ColaboradoresService(st.session_state.users_db)
                    
                    # Converter tipos numpy para tipos Python nativos
                    user_id = int(user_data['id'])
                    novo_saldo_int = int(novo_saldo)
                    
                    resultado = service.atualizar_saldo_colaborador(user_id, novo_saldo_int)
                    
                    if resultado["sucesso"]:
                        st.success(f"✅ {resultado['mensagem']}")
                        _limpar_sessao()
                        st.rerun()
                    else:
                        st.error(f"❌ {resultado['erro']}")
                        if "saldo_corrigido" in resultado:
                            st.info(f"💡 Saldo sugerido: {resultado['saldo_corrigido']} dias")
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar saldo: {str(e)}")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                _limpar_sessao()
                st.rerun()

def _confirmacao_exclusao(user_data):
    """Confirmação de exclusão melhorada"""
    st.markdown("---")
    st.markdown("### Confirmar Exclusão")
    
    st.error(f"⚠️ **ATENÇÃO**: Você está prestes a excluir o colaborador:")
    st.error(f"**Nome:** {user_data['nome']}")
    st.error(f"**Email:** {user_data['email']}")
    st.error(f"**Setor:** {user_data['setor']}")
    
    st.warning("Esta ação é **IRREVERSÍVEL** e excluirá: ")
    st.warning("• Todos os dados do colaborador")
    st.warning("• Histórico de férias")
    st.warning("• Registros relacionados")
    
    # Checkbox fora do formulário para melhor reatividade
    confirmacao = st.checkbox("Confirmo que desejo excluir este colaborador", key=f"confirm_{user_data['id']}")
    
    if confirmacao:
        st.warning("⚠️ Confirmação marcada - botão de exclusão habilitado")
    
    with st.form("form_exclusao"):
        col_delete, col_cancel = st.columns(2)
        
        with col_delete:
            # Remover disabled - sempre habilitado se chegou até aqui
            if st.form_submit_button("EXCLUIR DEFINITIVAMENTE", type="primary", use_container_width=True):
                if not confirmacao:
                    st.error("❌ Você deve marcar a confirmação antes de excluir")
                else:
                    try:
                        from ..services.colaboradores_service import ColaboradoresService
                        service = ColaboradoresService(st.session_state.users_db)
                        
                        # Converter tipos numpy para tipos Python nativos
                        user_id = int(user_data['id'])
                        
                        resultado = service.excluir_colaborador(user_id, user_data['nome'])
                        
                        if resultado["sucesso"]:
                            st.success(f"✅ {resultado['mensagem']}")
                            _limpar_sessao()
                            st.rerun()
                        else:
                            st.error(f"❌ {resultado['erro']}")
                    except Exception as e:
                        st.error(f"❌ Erro ao excluir colaborador: {str(e)}")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                _limpar_sessao()
                st.rerun()

def _confirmacao_inativacao(user_data):
    """Confirmação para inativar colaborador"""
    st.markdown("---")
    st.markdown("### Inativar Colaborador")
    
    st.warning(f"**Inativar colaborador:** {user_data['nome']}")
    st.info("**Dados preservados:** Todos os dados e histórico serão mantidos")
    st.info("**Efeito:** Colaborador não aparecerá nas listas principais e não poderá fazer login")
    st.success("**Reversível:** Pode ser reativado a qualquer momento")
    
    with st.form("form_inativacao"):
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.form_submit_button("Inativar Colaborador", type="primary", use_container_width=True):
                try:
                    user_id = int(user_data['id'])
                    sucesso = st.session_state.users_db.inativar_usuario(user_id)
                    
                    if sucesso:
                        st.success(f"{user_data['nome']} foi inativado com sucesso!")
                        st.info("Todos os dados foram preservados")
                        _limpar_sessao()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao inativar colaborador")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                _limpar_sessao()
                st.rerun()

def _confirmacao_reativacao(user_data):
    """Confirmação para reativar colaborador"""
    st.markdown("---")
    st.markdown("### Reativar Colaborador")
    
    st.success(f"**Reativar colaborador:** {user_data['nome']}")
    st.info("**Efeito:** Colaborador voltará a aparecer nas listas e poderá fazer login")
    st.info("**Dados preservados:** Todos os dados e histórico foram mantidos")
    
    with st.form("form_reativacao"):
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.form_submit_button("Reativar Colaborador", type="primary", use_container_width=True):
                try:
                    user_id = int(user_data['id'])
                    sucesso = st.session_state.users_db.ativar_usuario(user_id)
                    
                    if sucesso:
                        st.success(f"{user_data['nome']} foi reativado com sucesso!")
                        st.info("Colaborador pode fazer login novamente")
                        _limpar_sessao()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao reativar colaborador")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                _limpar_sessao()
                st.rerun()

def _limpar_sessao():
    """Limpa variáveis de sessão"""
    if 'acao_colaborador' in st.session_state:
        del st.session_state.acao_colaborador
    if 'user_selecionado' in st.session_state:
        del st.session_state.user_selecionado