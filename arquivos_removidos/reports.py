import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from .config import SETORES, DIAS_FERIAS_PADRAO


def relatorios_gerais():
    st.markdown("#### Relatórios Gerais")

    users_df = st.session_state.users_db.get_users()

    # Verificar se retornou None ou DataFrame válido
    if users_df is None:
        st.error("Erro ao carregar dados dos colaboradores")
        return
        
    if users_df.empty:
        st.info("Nenhum dado disponível para relatórios.")
        return

    # Verificar se usuário é RH para mostrar auditoria
    user_nivel = st.session_state.get('user', {}).get('nivel_acesso', '')
    
    if user_nivel == 'master':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Dashboard Geral", "Relatório por Setor", "Relatório de Férias", "Auditoria", "Alertas"]
        )
    else:
        tab1, tab2, tab3 = st.tabs(
            ["Dashboard Geral", "Relatório por Setor", "Relatório de Férias"]
        )

    with tab1:
        dashboard_geral(users_df)

    with tab2:
        relatorio_por_setor(users_df)

    with tab3:
        relatorio_ferias(users_df)
    
    if user_nivel == 'master':
        with tab4:
            relatorio_auditoria()
        
        with tab5:
            from .utils.alertas_ui import mostrar_painel_alertas
            mostrar_painel_alertas()


def dashboard_geral(users_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_colaboradores = len(users_df)
        st.metric("Total Colaboradores", total_colaboradores)

    with col2:
        saldo_medio = users_df["saldo_ferias"].mean()
        st.metric("Saldo Médio", f"{saldo_medio:.1f} dias")

    with col3:
        total_saldo = users_df["saldo_ferias"].sum()
        st.metric("Total Saldo", f"{total_saldo} dias")

    with col4:
        saldo_utilizado = (DIAS_FERIAS_PADRAO * len(users_df)) - total_saldo
        st.metric("Total Utilizado", f"{saldo_utilizado} dias")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Distribuição por Setor")
        setor_counts = users_df["setor"].value_counts()
        fig_setor = px.pie(
            values=setor_counts.values,
            names=setor_counts.index,
            title="Colaboradores por Setor",
        )
        st.plotly_chart(fig_setor, use_container_width=True)

    with col2:
        st.markdown("##### Saldo de Férias por Setor")
        saldo_por_setor = users_df.groupby("setor")["saldo_ferias"].mean().reset_index()
        fig_saldo = px.bar(
            saldo_por_setor, x="setor", y="saldo_ferias", title="Saldo Médio por Setor"
        )
        fig_saldo.update_xaxes(tickangle=45)
        st.plotly_chart(fig_saldo, use_container_width=True)


def relatorio_por_setor(users_df):
    setor_selecionado = st.selectbox("Selecionar Setor", ["Todos"] + SETORES)

    if setor_selecionado != "Todos":
        df_filtrado = users_df[users_df["setor"] == setor_selecionado]
    else:
        df_filtrado = users_df

    if df_filtrado.empty:
        st.info("Nenhum colaborador encontrado para o setor selecionado.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Colaboradores", len(df_filtrado))

    with col2:
        saldo_medio_setor = df_filtrado["saldo_ferias"].mean()
        st.metric("Saldo Médio", f"{saldo_medio_setor:.1f} dias")

    with col3:
        total_saldo_setor = df_filtrado["saldo_ferias"].sum()
        st.metric("Total Saldo", f"{total_saldo_setor} dias")

    st.markdown("##### Detalhes dos Colaboradores")
    df_exibicao = df_filtrado[["nome", "funcao", "setor", "saldo_ferias"]].rename(
        columns={
            "nome": "Nome",
            "funcao": "Função",
            "setor": "Setor",
            "saldo_ferias": "Saldo Atual",
        }
    )
    st.dataframe(df_exibicao, use_container_width=True)


def relatorio_ferias(users_df):
    st.markdown("##### Relatório de Férias por Período")

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", value=date(date.today().year, 1, 1))
    with col2:
        data_fim = st.date_input("Data Fim", value=date.today())

    if st.button("Gerar Relatório"):
        ferias_data = []

        for _, user in users_df.iterrows():
            ferias_df = st.session_state.ferias_db.get_ferias_usuario(user["id"])
            if not ferias_df.empty:
                ferias_periodo = ferias_df[
                    (
                        pd.to_datetime(ferias_df["data_inicio"])
                        >= pd.to_datetime(data_inicio)
                    )
                    & (
                        pd.to_datetime(ferias_df["data_fim"])
                        <= pd.to_datetime(data_fim)
                    )
                ]

                for _, ferias in ferias_periodo.iterrows():
                    ferias_data.append(
                        {
                            "Nome": user["nome"],
                            "Setor": user["setor"],
                            "Data Início": ferias["data_inicio"],
                            "Data Fim": ferias["data_fim"],
                            "Dias": ferias["dias_utilizados"],
                            "Status": ferias["status"],
                        }
                    )

        if ferias_data:
            df_ferias = pd.DataFrame(ferias_data)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Períodos", len(df_ferias))
            with col2:
                total_dias = df_ferias[df_ferias["Status"] == "Aprovada"]["Dias"].sum()
                st.metric("Total Dias Aprovados", total_dias)
            with col3:
                pendentes = len(df_ferias[df_ferias["Status"] == "Pendente"])
                st.metric("Pendentes", pendentes)

            st.dataframe(df_ferias, use_container_width=True)

            if len(df_ferias) > 0:
                fig_status = px.pie(
                    df_ferias, names="Status", title="Distribuição por Status"
                )
                st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Nenhum período de férias encontrado no intervalo selecionado.")


def relatorio_auditoria():
    """Relatório de auditoria - Apenas para RH"""
    st.markdown("##### Logs de Auditoria de Saldo")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por usuário
        users_df = st.session_state.users_db.get_users()
        user_options = {"Todos": None}
        
        if users_df is not None and not users_df.empty:
            user_options.update({
                f"{row['nome']} - {row['email']}": row['id']
                for _, row in users_df.iterrows()
            })
        selected_user = st.selectbox("Filtrar por Usuário", list(user_options.keys()))
        usuario_id = user_options[selected_user]
    
    with col2:
        data_inicio = st.date_input("Data Início", value=None)
    
    with col3:
        data_fim = st.date_input("Data Fim", value=None)
    
    col4, col5 = st.columns(2)
    
    with col4:
        tipo_operacao = st.selectbox("Tipo de Operação", [
            "Todos", "aprovacao_ferias", "cancelamento_ferias", 
            "exclusao_ferias", "edicao_manual", "correcao_automatica"
        ])
        tipo_operacao = None if tipo_operacao == "Todos" else tipo_operacao
    
    with col5:
        limit = st.number_input("Limite de Registros", min_value=10, max_value=5000, value=100)
    
    if st.button("Buscar Logs"):
        try:
            # logs_df = st.session_state.db.obter_logs_auditoria(
            #     usuario_id=usuario_id,
            #     data_inicio=data_inicio,
            #     data_fim=data_fim,
            #     tipo_operacao=tipo_operacao,
            #     limit=limit
            # )
            logs_df = pd.DataFrame()  # Temporariamente desabilitado
        except AttributeError as e:
            st.error(f"Método de auditoria não encontrado: {str(e)}")
            logs_df = pd.DataFrame()
        except Exception as e:
            st.error(f"Erro ao obter logs: {str(e)}")
            logs_df = pd.DataFrame()
        
        if not logs_df.empty:
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Registros", len(logs_df))
            
            with col2:
                tipos_unicos = logs_df['tipo_operacao'].nunique()
                st.metric("Tipos de Operação", tipos_unicos)
            
            with col3:
                usuarios_unicos = logs_df['usuario_id'].nunique()
                st.metric("Usuários Afetados", usuarios_unicos)
            
            with col4:
                if not logs_df.empty:
                    data_mais_recente = pd.to_datetime(logs_df['data_hora']).max().strftime('%d/%m/%Y')
                    st.metric("Último Registro", data_mais_recente)
            
            # Tabela de logs
            st.markdown("##### Detalhes dos Logs")
            
            # Formatar dados para exibição
            logs_display = logs_df.copy()
            logs_display['data_hora'] = pd.to_datetime(logs_display['data_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Renomear colunas
            logs_display = logs_display.rename(columns={
                'data_hora': 'Data/Hora',
                'nome_usuario': 'Usuário',
                'usuario_responsavel_nome': 'Responsável',
                'motivo': 'Motivo',
                'valor_anterior': 'Saldo Anterior',
                'valor_novo': 'Saldo Novo',
                'tipo_operacao': 'Tipo Operação',
                'detalhes_adicionais': 'Detalhes'
            })
            
            # Selecionar colunas para exibição
            colunas_exibir = [
                'Data/Hora', 'Usuário', 'Responsável', 'Motivo',
                'Saldo Anterior', 'Saldo Novo', 'Tipo Operação', 'Detalhes'
            ]
            
            # Filtrar colunas que existem
            colunas_existentes = [col for col in colunas_exibir if col in logs_display.columns]
            
            st.dataframe(logs_display[colunas_existentes], use_container_width=True)
            
            # Gráfico de distribuição por tipo
            if len(logs_df) > 0:
                st.markdown("##### Distribuição por Tipo de Operação")
                tipo_counts = logs_df['tipo_operacao'].value_counts()
                fig_tipos = px.pie(
                    values=tipo_counts.values,
                    names=tipo_counts.index,
                    title="Operações por Tipo"
                )
                st.plotly_chart(fig_tipos, use_container_width=True)
        
        else:
            st.info("Nenhum log encontrado com os filtros aplicados.")
    
    # Estatísticas gerais
    st.markdown("---")
    st.markdown("##### Estatísticas Gerais de Auditoria")
    
    try:
        # stats = st.session_state.db.obter_estatisticas_auditoria()
        stats = None  # Temporariamente desabilitado
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Registros", stats['total_registros'])
            
            with col2:
                st.metric("Últimos 30 Dias", stats['ultimos_30_dias'])
            
            with col3:
                if stats['por_tipo_operacao']:
                    tipo_mais_comum = stats['por_tipo_operacao'][0][0]
                    st.metric("Operação Mais Comum", tipo_mais_comum)
                else:
                    st.metric("Operação Mais Comum", "N/A")
        else:
            st.info("Nenhuma estatística de auditoria disponível")
    except AttributeError as e:
        st.error(f"Método de auditoria não encontrado: {str(e)}")
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {str(e)}")
