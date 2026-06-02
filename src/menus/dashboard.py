import streamlit as st
import pandas as pd

def mostrar_alertas_sistema():
    """Função vazia para manter compatibilidade"""
    pass

def mostrar_painel_alertas():
    """Função vazia para manter compatibilidade"""
    pass

def menu_dashboard():
    """Relatórios principal com métricas e alertas"""
    st.markdown("#### Relatórios")
    
    # Mostrar alertas do sistema
    mostrar_alertas_sistema()
    
    # Métricas gerais
    _mostrar_metricas_gerais()
    
    # Painel de alertas para RH
    user_nivel = st.session_state.get('user', {}).get('nivel_acesso', '')
    if user_nivel == 'master':
        st.markdown("---")
        mostrar_painel_alertas()

def _mostrar_metricas_gerais():
    """Mostra métricas gerais do sistema"""
    try:
        users_list = st.session_state.users_db.get_users()
        
        # Verificar se retornou None ou lista válida
        if users_list is None:
            st.error("Erro ao carregar dados dos colaboradores") 
            return
        
        # Converter lista para DataFrame se necessário
        if isinstance(users_list, list):
            if not users_list:
                st.info("Nenhum dado disponível")
                return
            users_df = pd.DataFrame(users_list)
        else:
            users_df = users_list
            if users_df.empty:
                st.info("Nenhum dado disponível")
                return
        
        # Filtro por setor - usar constantes como base
        from ..utils.constants import SETORES
        setores_banco = users_df['setor'].unique().tolist()
        setores_disponiveis = ['Todos'] + SETORES
        setor_selecionado = st.selectbox("Filtrar por Setor:", setores_disponiveis)
        
        # Aplicar filtro
        if setor_selecionado != 'Todos':
            users_filtered = users_df[users_df['setor'] == setor_selecionado]
        else:
            users_filtered = users_df
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_colaboradores = len(users_filtered)
            st.metric("Total de Colaboradores", total_colaboradores)
        
        with col2:
            saldo_medio = users_filtered['saldo_ferias'].mean()
            st.metric("Saldo Médio", f"{saldo_medio:.1f} dias")
    
        with col3:
            saldo_total = users_filtered['saldo_ferias'].sum()
            st.metric("Saldo Total", f"{saldo_total} dias")
        
        # Gráficos por setor
        if setor_selecionado == 'Todos':
            st.markdown("----")
                        
            setor_stats_df = pd.DataFrame(setor_data)
            
            st.dataframe(setor_stats_df, use_container_width=True, hide_index=True)

            st.markdown("##### Distribuição por Setor")

            colunas_detalhadas = [
                'nivel_acesso',
                'setor',
                'nome',
                'funcao',
                'saldo_ferias',
                'data_admissao'
            ]

            colunas_existentes = [col for col in colunas_detalhadas if col in users_df.columns]

            relatorio_hierarquia = users_df[colunas_existentes].copy()

            if 'data_admissao' in relatorio_hierarquia.columns:
                relatorio_hierarquia['data_admissao'] = relatorio_hierarquia['data_admissao'].apply(
                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
                )

            relatorio_hierarquia = relatorio_hierarquia.rename(columns={
                'nivel_acesso': 'Hierarquia',
                'setor': 'Setor',
                'nome': 'Colaborador',
                'funcao': 'Função',
                'saldo_ferias': 'Saldo de Férias',
                'data_admissao': 'Admissão'
            })

            st.dataframe(
                relatorio_hierarquia.sort_values(by=['Hierarquia', 'Setor', 'Colaborador']),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.markdown(f"##### Detalhes do Setor: {setor_selecionado}")
            
            if users_filtered.empty:
                st.info(f"Nenhum colaborador cadastrado no setor {setor_selecionado}")
            else:
                # Mostrar colaboradores do setor com data formatada
                users_display = users_filtered[['nome', 'funcao', 'saldo_ferias', 'data_admissao']].copy()
                users_display['data_admissao'] = users_display['data_admissao'].apply(
                    lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
                )
                st.dataframe(users_display, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {str(e)}")