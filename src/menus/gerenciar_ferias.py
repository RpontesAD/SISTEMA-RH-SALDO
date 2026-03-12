"""
Menu de Gerenciamento de Férias

Este módulo contém apenas componentes de interface,
delegando toda a lógica de negócio para a camada de serviços.
"""

import streamlit as st
import pandas as pd
from datetime import date
from ..services.ferias_service import FeriasService
from ..utils.feedback_usuario import mostrar_saldo_atual_vs_pendente


def menu_gerenciar_ferias():
    """
    Menu principal para gerenciar férias - Interface pura.
    
    Responsabilidades:
    - Renderizar componentes visuais
    - Capturar entrada do usuário
    - Delegar lógica para serviços
    - Exibir resultados
    """
    st.markdown("#### Gerenciar Férias")
    
    # Inicializar serviço
    service = FeriasService(st.session_state.ferias_db, st.session_state.users_db)
    
    # Obter usuários para seleção
    usuarios_result = service.obter_usuarios_para_selecao()
    
    if not usuarios_result["sucesso"]:
        st.warning(usuarios_result["erro"])
        return
    
    # Interface de seleção de colaborador (forçar ordem alfabética)
    usuarios_ordenados = sorted(usuarios_result["opcoes"].keys())
    selected_user = st.selectbox("Selecionar Colaborador", usuarios_ordenados)
    
    if selected_user:
        user_id = usuarios_result["opcoes"][selected_user]
        user_data = usuarios_result["usuarios"][usuarios_result["usuarios"]['id'] == user_id].iloc[0]
        
        # Mostrar informações de saldo
        _exibir_informacoes_saldo(service, user_id)
        
        # Tabs para diferentes operações
        tab1, tab2, tab3 = st.tabs(["Cadastrar Férias", "Histórico", "Gerenciar Status"])
        
        with tab1:
            _interface_cadastrar_ferias(service, user_id, user_data)
        
        with tab2:
            _interface_historico_ferias(service, user_id)
        
        with tab3:
            _interface_gerenciar_status(service, user_id)


def _exibir_informacoes_saldo(service: FeriasService, user_id: int):
    """
    Exibe informações de saldo usando o serviço.
    
    Args:
        service: Instância do FeriasService
        user_id: ID do usuário
    """
    saldo_info = service.obter_informacoes_saldo(user_id)
    
    if not saldo_info["sucesso"]:
        st.error(saldo_info["erro"])
        return
    
    # Exibir métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Saldo Atual", 
            f"{saldo_info['saldo_atual']} dias",
            help="Saldo disponível no momento"
        )
    
    with col2:
        if saldo_info["tem_pendencias"]:
            st.metric(
                "Dias Pendentes de Aprovação", 
                f"{saldo_info['dias_pendentes']} dias",
                help="Dias em férias pendentes de aprovação"
            )
        else:
            st.metric(
                "Dias Pendentes de Aprovação", 
                "0 dias",
                help="Nenhuma férias pendente"
            )
    
    with col3:
        # Calcular dias aprovados apenas das férias aprovadas
        dias_aprovados = service.obter_dias_aprovados(user_id)
        st.metric(
            "Dias Aprovados", 
            f"{dias_aprovados} dias",
            help="Dias de férias aprovadas e utilizadas"
        )
    
    # Alertas baseados no cálculo
    if not saldo_info["saldo_suficiente"]:
        st.warning("⚠️ **Atenção:** Saldo insuficiente para aprovar todas as férias pendentes")


def _interface_cadastrar_ferias(service: FeriasService, user_id: int, user_data):
    """
    Interface para cadastrar férias - Apenas UI.
    
    Args:
        service: Instância do FeriasService
        user_id: ID do usuário
        user_data: Dados do usuário
    """
    # Obter datas já ocupadas (apenas para validação)
    datas_ocupadas = _obter_datas_ocupadas(user_id)
    

    
    with st.form("form_ferias", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input("Data de Início", format="DD/MM/YYYY")
            
        with col2:
            data_fim = st.date_input("Data de Fim", format="DD/MM/YYYY")
        
        # Verificar conflito de datas
        if data_inicio and data_fim and data_inicio <= data_fim:
            conflito = _verificar_conflito_datas(data_inicio, data_fim, datas_ocupadas)
            if conflito:
                st.error(f"❌ {conflito}")
        
        status = "Pendente"  # Sempre cadastrar como pendente
        st.info(" Férias serão cadastradas como 'Pendente' e podem ser aprovadas posteriormente")
        
        submitted = st.form_submit_button("Cadastrar Férias", type="primary")
        
        if submitted:
            # Verificar se as datas são válidas
            if data_inicio > data_fim:
                st.error("❌ Data de início deve ser anterior à data de fim")
                return
            
            # Verificar conflito antes de cadastrar
            conflito = _verificar_conflito_datas(data_inicio, data_fim, datas_ocupadas)
            if conflito:
                st.error(f"❌ {conflito}")
                return
            
            # Obter nível do usuário logado
            user_nivel = st.session_state.get('user', {}).get('nivel_acesso', 'colaborador')
            
            # Verificar saldo antes de cadastrar
            saldo_info = service.obter_informacoes_saldo(user_id)
            if saldo_info["sucesso"]:
                # Calcular dias úteis da nova solicitação
                from ..utils.calculos import calcular_dias_uteis
                dias_solicitados = calcular_dias_uteis(data_inicio, data_fim)
                
                # Verificar se há saldo suficiente
                if dias_solicitados > saldo_info["saldo_atual"]:
                    st.error(f"❌ Saldo insuficiente! Você tem {saldo_info['saldo_atual']} dias disponíveis, mas está solicitando {dias_solicitados} dias.")
                    return
            
            # Usar serviço para cadastrar
            resultado = service.cadastrar_ferias(user_id, data_inicio, data_fim, status, user_nivel)
            
            # Verificar se resultado é um dicionário
            if not isinstance(resultado, dict):
                st.error(f"Erro interno: resultado inválido - {type(resultado)}")
                return
            
            # Exibir resultado
            if resultado.get("sucesso", False):
                st.success(resultado.get("mensagem", "Férias cadastradas"))
                if "dias_uteis" in resultado:
                    st.info(f"Dias úteis calculados: {resultado['dias_uteis']}")
                # Campos serão limpos automaticamente pelo clear_on_submit=True
            else:
                _exibir_erro_cadastro(resultado)


def _exibir_erro_cadastro(resultado: dict):
    """
    Exibe erros de cadastro de forma organizada.
    
    Args:
        resultado: Resultado do serviço com erro
    """
    st.error(f"❌ {resultado['erro']}")
    
    # Detalhes específicos por tipo de erro
    if resultado["tipo"] == "saldo" and "detalhes" in resultado:
        detalhes = resultado["detalhes"]
        st.error(f"Saldo atual: {detalhes['saldo_atual']} dias")
        st.error(f"Dias solicitados: {detalhes['dias_solicitados']} dias")
    
    elif resultado["tipo"] == "antecedencia" and "detalhes" in resultado:
        detalhes = resultado["detalhes"]
        st.error(f"⏰ Antecedência atual: {detalhes['dias_antecedencia']} dias")
        if not detalhes["eh_rh"]:
            st.info("💡 Dica: RH pode cadastrar sem antecedência mínima")


def _interface_historico_ferias(service: FeriasService, user_id: int):
    """
    Interface para exibir histórico - Apenas UI.
    
    Args:
        service: Instância do FeriasService
        user_id: ID do usuário
    """
    historico = service.obter_historico_ferias(user_id)
    
    if not historico["sucesso"]:
        st.error(historico["erro"])
        return
    
    if historico["vazio"]:
        st.info(historico["mensagem"])
        return
    
    # Exibir tabela formatada
    ferias_df = historico["ferias"]
    
    st.dataframe(
        ferias_df[['data_inicio', 'data_fim', 'dias_utilizados', 'status']],
        column_config={
            'data_inicio': 'Data Início',
            'data_fim': 'Data Fim',
            'dias_utilizados': 'Dias Aprovados',
            'status': 'Status'
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Total: {historico['total']} registro(s)")


def _interface_gerenciar_status(service: FeriasService, user_id: int):
    """
    Interface para gerenciar status - Apenas UI.
    
    Args:
        service: Instância do FeriasService
        user_id: ID do usuário
    """
    historico = service.obter_historico_ferias(user_id)
    
    if not historico["sucesso"]:
        st.error(historico["erro"])
        return
    
    if historico["vazio"]:
        st.info("Nenhuma férias para gerenciar")
        return

    
    ferias_df = historico["ferias"]
    
    for _, ferias in ferias_df.iterrows():
        # Definir cor do status
        status_color = {
            'Pendente': '🟡',
            'Aprovado': '🟢', 
            'Rejeitado': '🔴'
        }.get(ferias['status'], '⚪')
        
        with st.expander(f"{status_color} Férias: {ferias['data_inicio']} a {ferias['data_fim']} - {ferias['status']}"):
            col1, col2, col3 = st.columns(3)
            
            # Mostrar informações detalhadas
            st.write(f"**Dias:** {ferias['dias_utilizados']} | **Status atual:** {ferias['status']}")
            
            with col1:
                if st.button("Aprovar", key=f"aprovar_{ferias['id']}", disabled=(ferias['status'] == 'Aprovado')):
                    resultado = service.aprovar_ferias(ferias['id'])
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        # Forçar limpeza de cache e atualização
                        if 'saldo_cache' in st.session_state:
                            del st.session_state['saldo_cache']
                        st.rerun()
                    else:
                        st.error(resultado["erro"])
            
            with col2:
                if st.button("Cancelar", key=f"cancelar_{ferias['id']}", disabled=(ferias['status'] == 'Rejeitado')):
                    resultado = service.cancelar_ferias(ferias['id'])
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        st.rerun()
                    else:
                        st.error(resultado["erro"])
            
            with col3:
                if st.button("Excluir", key=f"excluir_{ferias['id']}", type="secondary"):
                    resultado = service.excluir_ferias(ferias['id'])
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        st.rerun()
                    else:
                        st.error(resultado["erro"])
                        
    # Legenda de cores
    st.markdown("##### Legenda de Status:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟡 **Pendente** - Aguardando aprovação")
    with col2:
        st.markdown("🟢 **Aprovado** - Férias confirmadas")
    with col3:
        st.markdown("🔴 **Rejeitado** - Férias canceladas")


def _obter_datas_ocupadas(user_id):
    """Obtém todas as datas já ocupadas por férias aprovadas"""
    try:
        # Usar o método da nova database
        ferias_list = st.session_state.ferias_db.get_ferias_usuario(user_id)
        
        # Converter lista para DataFrame se necessário
        if isinstance(ferias_list, list):
            if not ferias_list:
                return []
            ferias_df = pd.DataFrame(ferias_list)
        else:
            ferias_df = ferias_list
            if ferias_df.empty:
                return []
        
        # Filtrar apenas férias aprovadas
        ferias_aprovadas = ferias_df[ferias_df['status'] == 'Aprovado']
        
        datas_ocupadas = []
        for _, row in ferias_aprovadas.iterrows():
            inicio = row['data_inicio']
            fim = row['data_fim']
            
            # Converter para date se necessário
            if isinstance(inicio, str):
                inicio = pd.to_datetime(inicio).date()
            elif hasattr(inicio, 'date'):
                inicio = inicio.date()
                
            if isinstance(fim, str):
                fim = pd.to_datetime(fim).date()
            elif hasattr(fim, 'date'):
                fim = fim.date()
                
            datas_ocupadas.append((inicio, fim))
        
        return datas_ocupadas
    except Exception as e:
        st.error(f"Erro ao obter datas ocupadas: {e}")
        return []


def _verificar_conflito_datas(nova_inicio, nova_fim, datas_ocupadas):
    """Verifica se as novas datas conflitam com datas já ocupadas"""
    if not datas_ocupadas:
        return None
    
    for inicio_ocupada, fim_ocupada in datas_ocupadas:
        # Verificar sobreposição
        if (nova_inicio <= fim_ocupada and nova_fim >= inicio_ocupada):
            inicio_br = inicio_ocupada.strftime('%d/%m/%Y') if hasattr(inicio_ocupada, 'strftime') else str(inicio_ocupada)
            fim_br = fim_ocupada.strftime('%d/%m/%Y') if hasattr(fim_ocupada, 'strftime') else str(fim_ocupada)
            return f"Período conflita com férias já aprovadas de {inicio_br} a {fim_br}"
    
    return None