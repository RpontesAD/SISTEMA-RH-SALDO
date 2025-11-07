import streamlit as st
import pandas as pd
from ..utils.constants import SETORES, FUNCOES

def menu_avisos():
    """Menu para gerenciar avisos"""
    st.markdown("#### Gerenciar Avisos")
    
    # Filtros fora do formulário para manter estado
    st.markdown("##### Destinatários")
    todos_usuarios = st.checkbox("Todos os colaboradores")
    
    if not todos_usuarios:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            setores_selecionados = st.multiselect("Setores", SETORES)
        with col_f2:
            funcoes_selecionadas = st.multiselect("Funções", FUNCOES)
        with col_f3:
            usuarios_especificos = st.multiselect("Usuários específicos", _get_usuarios_opcoes())
    else:
        # Mostrar preview dos destinatários
        try:
            total_usuarios = len(st.session_state.users_db.get_users())
            st.success(f"📢 **Todos os colaboradores serão notificados** ({total_usuarios} pessoas)")
        except:
            st.success("📢 **Todos os colaboradores serão notificados**")
        setores_selecionados = []
        funcoes_selecionadas = []
        usuarios_especificos = []
    
    st.markdown("---")
    
    with st.form("form_aviso", clear_on_submit=True):
        st.markdown("##### Criar Novo Aviso")
        
        titulo = st.text_input("Título do Aviso", placeholder="Digite o título do aviso")
        conteudo = st.text_area("Conteúdo", placeholder="Digite o conteúdo do aviso", height=150)
        
        if st.form_submit_button("Publicar Aviso", type="primary", use_container_width=True):
            if not titulo or not conteudo:
                st.error("Título e conteúdo são obrigatórios!")
                return
            
            # Determinar destinatários
            if todos_usuarios:
                destinatarios = st.session_state.users_db.get_users()
            else:
                destinatarios = _filtrar_destinatarios(setores_selecionados, funcoes_selecionadas, usuarios_especificos)
                
                # Se nenhum filtro foi selecionado, avisar
                if not setores_selecionados and not funcoes_selecionadas and not usuarios_especificos:
                    st.error("Selecione pelo menos um filtro: setor, função ou usuário específico!")
                    return
            
            if not destinatarios:
                st.error("Selecione pelo menos um destinatário!")
                return
            
            # Criar aviso
            destinatarios_ids = [user['id'] for user in destinatarios]
            sucesso = st.session_state.users_db.criar_aviso(
                titulo, conteudo, st.session_state.user['id'], destinatarios_ids
            )
            
            if sucesso:
                st.success(f"Aviso publicado para {len(destinatarios)} colaboradores!")
            else:
                st.error("Erro ao publicar aviso!")
    
    st.markdown("---")
    
    # Seção de matriz de leitura
    st.markdown("##### Status de Leitura por Colaborador")
    
    try:
        matriz_dados = st.session_state.users_db.get_matriz_leitura_avisos()
        
        if not matriz_dados:
            st.info("Nenhum aviso publicado ainda.")
            return
        
        if len(matriz_dados) == 0:
            st.info("Nenhum aviso ativo encontrado.")
            return
        else:
            # Converter para DataFrame
            df_matriz = pd.DataFrame(matriz_dados)
            
            # Adicionar coluna oculto se não existir (para compatibilidade)
            if 'oculto' not in df_matriz.columns:
                df_matriz['oculto'] = False
            
            # Criar tabela pivot: colaboradores x avisos
            pivot_table = df_matriz.pivot_table(
                index=['nome', 'setor', 'funcao'],
                columns='titulo',
                values='lido',
                fill_value=False,
                aggfunc='first'
            )
            
            # Resetar índice
            pivot_table = pivot_table.reset_index()
            
            # Converter para ícones
            for col in pivot_table.columns:
                if col not in ['nome', 'setor', 'funcao']:
                    pivot_table[col] = pivot_table[col].apply(
                        lambda x: '✅' if x else '❌'
                    )
            
            # Verificar se há colunas necessárias
            if 'titulo' not in df_matriz.columns or 'aviso_id' not in df_matriz.columns:
                st.error("Dados de avisos incompletos")
                return
            
            # Seletor de avisos com ações
            avisos_disponiveis = df_matriz[['titulo', 'aviso_id']].drop_duplicates()
            
            if avisos_disponiveis.empty:
                st.info("Nenhum aviso encontrado")
                return
            
            avisos_dict = {str(row['titulo']): int(row['aviso_id']) for _, row in avisos_disponiveis.iterrows()}
            

            
            col_sel, col_edit, col_del = st.columns([3, 1, 1])
            
            with col_sel:
                aviso_selecionado = st.selectbox(
                    "Selecionar aviso para visualizar:",
                    list(avisos_dict.keys())
                )
            
            # Obter ID do aviso selecionado
            aviso_id = avisos_dict.get(aviso_selecionado)
            
            if not aviso_id:
                st.error("ID do aviso não encontrado")
                return
            
            with col_edit:
                if st.button("Editar", key=f"edit_{aviso_id}", use_container_width=True):
                    st.session_state.editando_aviso = aviso_id
                    st.rerun()
            
            with col_del:
                if st.button("Excluir", key=f"del_{aviso_id}", use_container_width=True, type="secondary"):
                    if st.session_state.users_db.excluir_aviso(aviso_id):
                        st.success("Aviso excluído!")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir aviso")
            
            # Mostrar formulário de edição se necessário
            if st.session_state.get('editando_aviso'):
                _mostrar_formulario_edicao(st.session_state.editando_aviso)
                return
            
            # Filtrar dados pelo aviso selecionado
            df_filtrado = df_matriz[df_matriz['titulo'] == aviso_selecionado]
            
            # Criar tabela apenas com o aviso selecionado
            tabela_aviso = df_filtrado[['nome', 'setor', 'funcao', 'lido']].copy()
            
            # Criar status simples
            tabela_aviso['status'] = tabela_aviso['lido'].apply(
                lambda x: '✅ Lido' if x else '❌ Não lido'
            )
            
            st.dataframe(
                tabela_aviso[['nome', 'setor', 'funcao', 'status']],
                column_config={
                    'nome': 'Nome',
                    'setor': 'Setor', 
                    'funcao': 'Função',
                    'status': 'Status'
                },
                use_container_width=True,
                hide_index=True
            )
                
    except Exception as e:
        st.error(f"Erro ao carregar matriz de leitura: {type(e).__name__}: {str(e)}")


def _get_usuarios_opcoes():
    """Retorna lista de usuários para seleção"""
    try:
        usuarios = st.session_state.users_db.get_users()
        return [f"{user['nome']} - {user['setor']}" for user in usuarios]
    except:
        return []

def _filtrar_destinatarios(setores, funcoes, usuarios_especificos):
    """Filtra destinatários baseado nos critérios selecionados"""
    try:
        todos_usuarios = st.session_state.users_db.get_users()
        destinatarios = []
        
        # Filtrar por setores
        if setores:
            destinatarios.extend([user for user in todos_usuarios if user['setor'] in setores])
        
        # Filtrar por funções
        if funcoes:
            destinatarios.extend([user for user in todos_usuarios if user['funcao'] in funcoes])
        
        # Usuários específicos
        if usuarios_especificos:
            nomes_selecionados = [nome.split(' - ')[0] for nome in usuarios_especificos]
            destinatarios.extend([user for user in todos_usuarios if user['nome'] in nomes_selecionados])
        
        # Remover duplicatas
        destinatarios_unicos = []
        ids_vistos = set()
        for user in destinatarios:
            if user['id'] not in ids_vistos:
                destinatarios_unicos.append(user)
                ids_vistos.add(user['id'])
        
        return destinatarios_unicos
    except:
        return []

def _mostrar_detalhes_aviso(aviso_id):
    """Mostra detalhes de leitura de um aviso específico"""
    try:
        status_leitura = st.session_state.users_db.get_status_leitura_aviso(aviso_id)
        
        if not status_leitura:
            st.warning("Nenhum destinatário encontrado para este aviso.")
            return
        
        st.markdown("###### Status de Leitura por Colaborador")
        
        # Converter para DataFrame
        df_status = pd.DataFrame(status_leitura)
        
        # Formatar data de leitura
        df_status['data_leitura_formatada'] = df_status['data_leitura'].apply(
            lambda x: x.strftime('%d/%m/%Y %H:%M') if x else '-'
        )
        
        # Adicionar status visual simples
        df_status['status_visual'] = df_status['lido'].apply(
            lambda x: '✅ Lido' if x else '❌ Não lido'
        )
        
        # Mostrar tabela
        st.dataframe(
            df_status[['nome', 'setor', 'funcao', 'status_visual', 'data_leitura_formatada']],
            column_config={
                'nome': 'Nome',
                'setor': 'Setor',
                'funcao': 'Função',
                'status_visual': 'Status',
                'data_leitura_formatada': 'Data/Hora Leitura'
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas rápidas
        total = len(df_status)
        lidos = len(df_status[df_status['lido'] == True])
        nao_lidos = total - lidos
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Enviado", total)
        with col2:
            st.metric("Lidos", lidos)
        with col3:
            st.metric("Não Lidos", nao_lidos)
            
    except Exception as e:
        st.error("Erro ao carregar detalhes do aviso")

def _mostrar_formulario_edicao(aviso_id):
    """Mostra formulário de edição de aviso"""
    st.markdown("##### Editar Aviso")
    
    # Buscar dados do aviso
    aviso_dados = st.session_state.users_db.get_aviso_detalhes(aviso_id)
    
    if not aviso_dados:
        st.error("Aviso não encontrado ou foi excluído")
        if st.button("Voltar"):
            del st.session_state.editando_aviso
            st.rerun()
        return
    
    with st.form("form_edicao_aviso"):
        titulo = st.text_input("Título", value=aviso_dados['titulo'])
        conteudo = st.text_area("Conteúdo", value=aviso_dados['conteudo'], height=150)
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True):
                if st.session_state.users_db.atualizar_aviso(aviso_id, titulo, conteudo):
                    st.success("Aviso atualizado!")
                    del st.session_state.editando_aviso
                    st.rerun()
                else:
                    st.error("Erro ao atualizar aviso")
        
        with col_cancel:
            if st.form_submit_button("Cancelar", use_container_width=True):
                del st.session_state.editando_aviso
                st.rerun()