"""
Menu de Cadastro de Colaborador 

Este módulo contém apenas componentes de interface,
delegando toda a lógica de negócio para a camada de serviços.
"""

import streamlit as st
from datetime import date
from ..services.colaboradores_service import ColaboradoresService
from ..utils.constants import SETORES, FUNCOES
from ..utils.input_validation import safe_text_input, safe_selectbox, validate_form_data
from ..utils.error_handler import safe_execute, log_operation


def menu_cadastro_colaborador():
    """
    Menu para cadastro de colaboradores - Interface pura.
    
    Responsabilidades:
    - Renderizar formulário
    - Capturar dados do usuário
    - Delegar validação e cadastro para serviço
    - Exibir resultados
    """
    st.markdown("#### Cadastrar Novo Colaborador")
    
    # Inicializar serviço
    service = ColaboradoresService(st.session_state.users_db)
    
    # Limpar formulário se foi solicitado
    if st.session_state.get('clear_form', False):
        for key in ['nome_cadastro', 'email_cadastro', 'senha_cadastro', 'confirmar_senha_cadastro', 'setor_cadastro', 'funcao_cadastro', 'nivel_cadastro', 'saldo_cadastro', 'data_cadastro']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.clear_form = False
    
    # Formulário de cadastro (não limpa em caso de erro)
    with st.form("form_cadastro", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*", max_chars=100, key="nome_cadastro")
            email = st.text_input("Email*", max_chars=100, key="email_cadastro")
            setor = st.selectbox("Setor*", SETORES, key="setor_cadastro")
            saldo_ferias = st.number_input("Saldo Inicial de Férias", min_value=0, max_value=30, value=12, help="Padrão: 12 dias", key="saldo_cadastro")
            
        with col2:
            senha = st.text_input("Senha*", type="password", help="Mínimo 6 caracteres", max_chars=50, key="senha_cadastro")
            confirmar_senha = st.text_input("Confirmar Senha*", type="password", help="Digite a senha novamente", max_chars=50, key="confirmar_senha_cadastro")
            funcao = st.selectbox("Função*", FUNCOES, key="funcao_cadastro")
            nivel_acesso = st.selectbox("Nível de Acesso*", ["colaborador", "coordenador", "diretoria", "master"], key="nivel_cadastro")
            data_admissao = st.date_input("Data de Admissão", value=date.today(), format="DD/MM/YYYY", key="data_cadastro")
        
        submitted = st.form_submit_button("Cadastrar Colaborador", type="primary")
        
        if submitted:
            _processar_cadastro(service, nome, email, senha, confirmar_senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao)


def _processar_cadastro(service: ColaboradoresService, nome: str, email: str, senha: str, confirmar_senha: str,
                       setor: str, funcao: str, nivel_acesso: str, saldo_ferias: int, data_admissao: date):
    """
    Processa o cadastro usando o serviço.
    
    Args:
        service: Instância do ColaboradoresService
        nome: Nome do colaborador
        email: Email do colaborador
        senha: Senha do colaborador
        setor: Setor do colaborador
        funcao: Função do colaborador
        saldo_ferias: Saldo inicial
        data_admissao: Data de admissão
    """
    # Validar campos obrigatórios na interface
    if not all([nome, email, senha, confirmar_senha, setor, funcao, nivel_acesso]):
        st.error("❌ Todos os campos obrigatórios devem ser preenchidos")
        return
    
    # Validar confirmação de senha
    if senha != confirmar_senha:
        st.error("❌ As senhas não coincidem")
        return
    
    # Log da operação
    log_operation("cadastro_colaborador_ui", details={
        "nome": nome,
        "email": email,
        "setor": setor,
        "funcao": funcao
    })
    
    # Usar execução segura para cadastrar
    sucesso, resultado, erro = safe_execute(
        service.cadastrar_colaborador,
        nome=nome,
        email=email,
        senha=senha,
        setor=setor,
        funcao=funcao,
        nivel_acesso=nivel_acesso,
        saldo_ferias=saldo_ferias,
        data_admissao=data_admissao
    )
    
    # Exibir resultado
    if sucesso and resultado and resultado.get("sucesso"):
        st.success(f"✅ {resultado['mensagem']}")
        
        # Mostrar saldo usado se foi corrigido
        if "saldo_usado" in resultado and resultado["saldo_usado"] != saldo_ferias:
            st.info(f"ℹ️ Saldo corrigido para {resultado['saldo_usado']} dias (dentro dos limites permitidos)")
        
        # Limpar campos apenas em caso de sucesso
        st.session_state.clear_form = True
        st.rerun()
    elif sucesso and resultado:
        _exibir_erro_cadastro(resultado)
    else:
        st.error(f"❌ Erro interno: {erro or 'Falha no sistema'}")
        st.info("📞 Entre em contato com o administrador do sistema")


def _exibir_erro_cadastro(resultado: dict):
    """
    Exibe erros de cadastro de forma organizada.
    
    Args:
        resultado: Resultado do serviço com erro
    """
    st.error(f"❌ {resultado['erro']}")
    
    # Sugestões específicas por campo
    if resultado["campo"] == "email":
        st.info("💡 Verifique se o email está correto e não está já cadastrado")
    
    elif resultado["campo"] == "senha":
        st.info("💡 A senha deve ter pelo menos 6 caracteres")
    
    elif resultado["campo"] == "saldo_ferias" and "saldo_corrigido" in resultado:
        st.info(f"💡 Saldo sugerido: {resultado['saldo_corrigido']} dias")
    
    elif resultado["campo"] == "nome":
        st.info("💡 O nome deve ter pelo menos 2 caracteres")


def menu_listar_colaboradores():
    """
    Menu para listar colaboradores - Interface pura.
    """
    st.markdown("#### Lista de Colaboradores")
    
    # Inicializar serviço
    service = ColaboradoresService(st.session_state.users_db)
    
    # Filtros
    col1, col2 = st.columns([2, 1])
    
    with col1:
        setor_filtro = st.selectbox("Filtrar por Setor", ["Todos"] + SETORES)
    
    with col2:
        if st.button("🔄 Atualizar Lista"):
            st.rerun()
    
    # Obter colaboradores
    setor_param = None if setor_filtro == "Todos" else setor_filtro
    colaboradores_result = service.obter_colaboradores(setor=setor_param)
    
    if not colaboradores_result["sucesso"]:
        st.error(colaboradores_result["erro"])
        return
    
    if colaboradores_result["vazio"]:
        st.info(colaboradores_result["mensagem"])
        return
    
    # Exibir lista
    colaboradores_df = colaboradores_result["colaboradores"]
    
    st.dataframe(
        colaboradores_df[['nome', 'email', 'setor', 'funcao', 'nivel_acesso', 'saldo_ferias']],
        column_config={
            'nome': 'Nome',
            'email': 'Email',
            'setor': 'Setor',
            'funcao': 'Função',
            'nivel_acesso': 'Nível',
            'saldo_ferias': 'Saldo (dias)'
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Total: {colaboradores_result['total']} colaborador(es)")


def menu_editar_colaborador():
    """
    Menu para editar colaboradores - Interface pura.
    """
    st.markdown("#### Editar Colaborador")
    
    # Inicializar serviço
    service = ColaboradoresService(st.session_state.users_db)
    
    # Obter colaboradores para seleção
    colaboradores_result = service.obter_colaboradores()
    
    if not colaboradores_result["sucesso"]:
        st.error(colaboradores_result["erro"])
        return
    
    if colaboradores_result["vazio"]:
        st.info("Nenhum colaborador cadastrado para editar")
        return
    
    # Seleção de colaborador
    colaboradores_df = colaboradores_result["colaboradores"]
    opcoes = {f"{row['nome']} ({row['email']})": row['id'] 
             for _, row in colaboradores_df.iterrows()}
    
    selected_colaborador = st.selectbox("Selecionar Colaborador", list(opcoes.keys()))
    
    if selected_colaborador:
        user_id = opcoes[selected_colaborador]
        user_data = colaboradores_df[colaboradores_df['id'] == user_id].iloc[0]
        
        _interface_edicao_colaborador(service, user_id, user_data)


def _interface_edicao_colaborador(service: ColaboradoresService, user_id: int, user_data):
    """
    Interface para edição de colaborador.
    
    Args:
        service: Instância do ColaboradoresService
        user_id: ID do colaborador
        user_data: Dados atuais do colaborador
    """
    with st.form("form_edicao"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = safe_text_input("Nome Completo*", value=user_data['nome'], max_chars=100)
            email = safe_text_input("Email*", value=user_data['email'], max_chars=100)
            setor = safe_selectbox("Setor*", SETORES, index=SETORES.index(user_data['setor']) if user_data['setor'] in SETORES else 0)
            
        with col2:
            funcao = safe_selectbox("Função*", FUNCOES, index=FUNCOES.index(user_data['funcao']) if user_data['funcao'] in FUNCOES else 0)
            nivel_acesso = safe_selectbox("Nível de Acesso", 
                                      ["colaborador", "coordenador", "diretoria", "master"],
                                      index=["colaborador", "coordenador", "diretoria", "master"].index(user_data['nivel_acesso']))
            saldo_ferias = st.number_input("Saldo de Férias", min_value=0, max_value=30, value=int(user_data['saldo_ferias']))
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            submitted = st.form_submit_button("Atualizar Colaborador", type="primary")
        
        with col_btn2:
            excluir = st.form_submit_button("Excluir Colaborador", type="secondary")
        
        if submitted:
            _processar_edicao(service, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias)
        
        if excluir:
            _processar_exclusao(service, user_id, user_data['nome'])


def _processar_edicao(service: ColaboradoresService, user_id: int, nome: str, email: str,
                     setor: str, funcao: str, nivel_acesso: str, saldo_ferias: int):
    """
    Processa edição usando o serviço.
    """
    resultado = service.atualizar_colaborador(user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias)
    
    if resultado["sucesso"]:
        st.success(f"✅ {resultado['mensagem']}")
        st.rerun()
    else:
        st.error(f"❌ {resultado['erro']}")
        
        if "saldo_corrigido" in resultado:
            st.info(f"💡 Saldo sugerido: {resultado['saldo_corrigido']} dias")


def _processar_exclusao(service: ColaboradoresService, user_id: int, nome_colaborador: str):
    """
    Processa exclusão usando o serviço.
    """
    # Confirmação de segurança
    st.warning(f"⚠️ **Atenção:** Você está prestes a excluir o colaborador **{nome_colaborador}**")
    st.warning("Esta ação não pode ser desfeita e removerá todos os dados relacionados.")
    
    if st.checkbox("Confirmo que desejo excluir este colaborador", key="confirm_delete"):
        resultado = service.excluir_colaborador(user_id, nome_colaborador)
        
        if resultado["sucesso"]:
            st.success(f"✅ {resultado['mensagem']}")
            st.rerun()
        else:
            st.error(f"❌ {resultado['erro']}")