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
        users_df = st.session_state.users_db.get_users()
        
        # Verificar se retornou None ou DataFrame válido
        if users_df is None:
            st.error("Erro ao carregar dados dos colaboradores") 
            return
            
        if users_df.empty:
            st.info("Nenhum dado disponível")
            return
        
        # Filtro por setor - usar constantes como base
        from ..core.constantes import SETORES
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
            st.markdown("##### Distribuição por Setor")
            
            # Criar estatísticas para todos os setores das constantes
            from ..core.constantes import SETORES
            setor_data = []
            
            for setor in SETORES:
                setor_users = users_df[users_df['setor'] == setor]
                if not setor_users.empty:
                    colaboradores = len(setor_users)
                    saldo_medio = setor_users['saldo_ferias'].mean()
                    saldo_total = setor_users['saldo_ferias'].sum()
                else:
                    colaboradores = 0
                    saldo_medio = 0.0
                    saldo_total = 0
                
                setor_data.append({
                    'Setor': setor,
                    'Colaboradores': colaboradores,
                    'Saldo Médio': round(saldo_medio, 1),
                    'Saldo Total': saldo_total
                })
            
            setor_stats_df = pd.DataFrame(setor_data)
            st.dataframe(setor_stats_df, use_container_width=True, hide_index=True)
            

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