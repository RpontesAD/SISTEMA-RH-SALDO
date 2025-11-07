import streamlit as st
import pandas as pd
from datetime import date

def menu_renovacao_saldo():
    """Menu para renovação anual de saldo de férias"""
    st.markdown("#### Renovação Anual de Saldo")
    
    # Verificar se há renovação anterior
    historico = st.session_state.users_db.get_historico_renovacoes()
    ultima_renovacao = historico[0] if historico else None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Nova Renovação")
        
        with st.form("form_renovacao"):
            ano = st.number_input("Ano", min_value=2024, max_value=2030, value=date.today().year + 1)
            saldo_padrao = st.number_input("Saldo Padrão (dias)", min_value=1, max_value=30, value=12)
            
            # Prévia
            if st.form_submit_button("Visualizar Prévia", type="secondary"):
                _mostrar_previa(ano, saldo_padrao)
            
            # Aplicar renovação
            if st.form_submit_button("Aplicar Renovação", type="primary"):
                if st.session_state.users_db.verificar_renovacao_ano(ano):
                    st.error(f"Já existe renovação para o ano {ano}")
                else:
                    sucesso, mensagem = st.session_state.users_db.renovar_saldo_anual(
                        ano, saldo_padrao, st.session_state.user['id']
                    )
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)
    
    with col2:
        st.markdown("##### Reset para Valores Anteriores")
        
        if ultima_renovacao:
            st.info(f"Última renovação: {ultima_renovacao['ano']} - {ultima_renovacao['saldo_padrao']} dias")
            
            if st.button("Resetar para Valores Anteriores", type="secondary"):
                sucesso, mensagem = st.session_state.users_db.desfazer_ultima_renovacao(
                    st.session_state.user['id']
                )
                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)
        else:
            st.info("Nenhuma renovação anterior encontrada")
    
    # Histórico
    st.markdown("---")
    st.markdown("##### Histórico de Renovações")
    
    if historico:
        df_historico = pd.DataFrame(historico)
        df_historico['data_aplicacao'] = df_historico['data_aplicacao'].dt.strftime('%d/%m/%Y %H:%M')
        
        st.dataframe(
            df_historico[['ano', 'saldo_padrao', 'responsavel_nome', 'data_aplicacao']],
            column_config={
                'ano': 'Ano',
                'saldo_padrao': 'Saldo Padrão',
                'responsavel_nome': 'Responsável',
                'data_aplicacao': 'Data/Hora'
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma renovação realizada ainda")

def _mostrar_previa(ano, saldo_padrao):
    """Mostra prévia da renovação"""
    st.markdown("##### Prévia da Renovação")
    
    usuarios = st.session_state.users_db.get_users()
    
    if not usuarios:
        st.info("Nenhum colaborador encontrado")
        return
    
    previa_data = []
    for user in usuarios:
        saldo_atual = user['saldo_ferias']
        novo_saldo = saldo_atual + saldo_padrao
        
        previa_data.append({
            'Nome': user['nome'],
            'Setor': user['setor'],
            'Saldo Atual': f"{saldo_atual} dias",
            'Novo Saldo': f"{novo_saldo} dias",
            'Acréscimo': f"+{saldo_padrao} dias"
        })
    
    df_previa = pd.DataFrame(previa_data)
    
    st.dataframe(
        df_previa,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"📊 Total de colaboradores afetados: {len(usuarios)}")
    st.success(f"✅ Cada colaborador receberá +{saldo_padrao} dias somados ao saldo atual")