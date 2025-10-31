"""
Menu de Auditoria - Visualização de logs e relatórios de auditoria
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import os
from ..utils.audit_logger import audit_logger

def menu_auditoria():
    """Menu principal de auditoria"""
    st.markdown("#### 📊 Auditoria e Logs do Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Logs de Ações", 
        "🔒 Logs de Segurança", 
        "⚙️ Logs de Operações",
        "📈 Relatórios"
    ])
    
    with tab1:
        _exibir_logs_acoes()
    
    with tab2:
        _exibir_logs_seguranca()
    
    with tab3:
        _exibir_logs_operacoes()
    
    with tab4:
        _exibir_relatorios()

def _exibir_logs_acoes():
    """Exibe logs de ações dos usuários"""
    st.markdown("##### Logs de Ações dos Usuários")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_inicio = st.date_input("Data Início", value=date.today() - timedelta(days=7))
    
    with col2:
        data_fim = st.date_input("Data Fim", value=date.today())
    
    with col3:
        limite = st.selectbox("Limite de Registros", [50, 100, 500, 1000], index=1)
    
    # Ler logs de auditoria
    logs_df = _ler_logs_arquivo('logs/audit.log', data_inicio, data_fim, limite)
    
    if not logs_df.empty:
        # Filtros adicionais
        col1, col2 = st.columns(2)
        
        with col1:
            usuarios = ['Todos'] + list(logs_df['user_id'].dropna().unique())
            user_filter = st.selectbox("Filtrar por Usuário", usuarios)
        
        with col2:
            acoes = ['Todas'] + list(logs_df['action'].dropna().unique())
            action_filter = st.selectbox("Filtrar por Ação", acoes)
        
        # Aplicar filtros
        df_filtrado = logs_df.copy()
        
        if user_filter != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['user_id'] == user_filter]
        
        if action_filter != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['action'] == action_filter]
        
        # Exibir logs
        st.dataframe(
            df_filtrado[['timestamp', 'user_id', 'action', 'details']],
            column_config={
                'timestamp': 'Data/Hora',
                'user_id': 'Usuário ID',
                'action': 'Ação',
                'details': 'Detalhes'
            },
            use_container_width=True
        )
        
        st.caption(f"Exibindo {len(df_filtrado)} de {len(logs_df)} registros")
    else:
        st.info("Nenhum log de ação encontrado no período selecionado")

def _exibir_logs_seguranca():
    """Exibe logs de segurança"""
    st.markdown("##### Logs de Segurança")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input("Data Início", value=date.today() - timedelta(days=7), key="sec_start")
    
    with col2:
        data_fim = st.date_input("Data Fim", value=date.today(), key="sec_end")
    
    # Ler logs de segurança
    logs_df = _ler_logs_arquivo('logs/security.log', data_inicio, data_fim, 500)
    
    if not logs_df.empty:
        # Métricas de segurança
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_eventos = len(logs_df)
            st.metric("Total de Eventos", total_eventos)
        
        with col2:
            eventos_criticos = len(logs_df[logs_df['severity'] == 'CRITICAL'])
            st.metric("Eventos Críticos", eventos_criticos, delta=eventos_criticos if eventos_criticos > 0 else None)
        
        with col3:
            logins_falharam = len(logs_df[logs_df['event_type'] == 'LOGIN_FAILED'])
            st.metric("Logins Falharam", logins_falharam)
        
        with col4:
            logins_sucesso = len(logs_df[logs_df['event_type'] == 'LOGIN_SUCCESS'])
            st.metric("Logins Sucesso", logins_sucesso)
        
        # Filtro por severidade
        severidades = ['Todas'] + list(logs_df['severity'].dropna().unique())
        severity_filter = st.selectbox("Filtrar por Severidade", severidades)
        
        df_filtrado = logs_df.copy()
        if severity_filter != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['severity'] == severity_filter]
        
        # Exibir logs com cores por severidade
        for _, row in df_filtrado.iterrows():
            severity = row.get('severity', 'INFO')
            
            if severity == 'CRITICAL':
                st.error(f"🚨 **{row['timestamp']}** - {row['event_type']} - {row.get('details', {})}")
            elif severity == 'ERROR':
                st.warning(f"⚠️ **{row['timestamp']}** - {row['event_type']} - {row.get('details', {})}")
            else:
                st.info(f"ℹ️ **{row['timestamp']}** - {row['event_type']} - {row.get('details', {})}")
    else:
        st.info("Nenhum log de segurança encontrado no período selecionado")

def _exibir_logs_operacoes():
    """Exibe logs de operações do sistema"""
    st.markdown("##### Logs de Operações do Sistema")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_inicio = st.date_input("Data Início", value=date.today() - timedelta(days=1), key="ops_start")
    
    with col2:
        data_fim = st.date_input("Data Fim", value=date.today(), key="ops_end")
    
    with col3:
        status_filter = st.selectbox("Status", ['Todos', 'SUCCESS', 'ERROR'])
    
    # Ler logs de operações
    logs_df = _ler_logs_arquivo('logs/operations.log', data_inicio, data_fim, 1000)
    
    if not logs_df.empty:
        # Métricas de performance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_ops = len(logs_df)
            st.metric("Total Operações", total_ops)
        
        with col2:
            ops_sucesso = len(logs_df[logs_df['status'] == 'SUCCESS'])
            taxa_sucesso = (ops_sucesso / total_ops * 100) if total_ops > 0 else 0
            st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
        
        with col3:
            ops_erro = len(logs_df[logs_df['status'] == 'ERROR'])
            st.metric("Operações com Erro", ops_erro)
        
        with col4:
            tempo_medio = logs_df['duration_ms'].mean() if 'duration_ms' in logs_df.columns else 0
            st.metric("Tempo Médio (ms)", f"{tempo_medio:.1f}")
        
        # Aplicar filtro de status
        df_filtrado = logs_df.copy()
        if status_filter != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['status'] == status_filter]
        
        # Gráfico de operações por hora
        if 'timestamp' in df_filtrado.columns:
            df_filtrado['hora'] = pd.to_datetime(df_filtrado['timestamp']).dt.hour
            ops_por_hora = df_filtrado.groupby('hora').size()
            
            st.markdown("##### Operações por Hora")
            st.bar_chart(ops_por_hora)
        
        # Tabela de operações
        st.dataframe(
            df_filtrado[['timestamp', 'operation', 'status', 'duration_ms']],
            column_config={
                'timestamp': 'Data/Hora',
                'operation': 'Operação',
                'status': 'Status',
                'duration_ms': 'Duração (ms)'
            },
            use_container_width=True
        )
    else:
        st.info("Nenhum log de operação encontrado no período selecionado")

def _exibir_relatorios():
    """Exibe relatórios de auditoria"""
    st.markdown("##### Relatórios de Auditoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Resumo Geral**")
        
        # Estatísticas gerais
        stats = _obter_estatisticas_gerais()
        
        st.metric("Total de Logs de Auditoria", stats.get('total_audit', 0))
        st.metric("Total de Logs de Segurança", stats.get('total_security', 0))
        st.metric("Total de Logs de Operações", stats.get('total_operations', 0))
        
        # Usuários mais ativos
        st.markdown("**👥 Usuários Mais Ativos (Últimos 7 dias)**")
        usuarios_ativos = _obter_usuarios_mais_ativos()
        
        if not usuarios_ativos.empty:
            st.dataframe(
                usuarios_ativos,
                column_config={
                    'user_id': 'Usuário ID',
                    'total_acoes': 'Total de Ações'
                },
                use_container_width=True
            )
    
    with col2:
        st.markdown("**🔍 Análise de Segurança**")
        
        # Eventos de segurança recentes
        eventos_seguranca = _obter_eventos_seguranca_recentes()
        
        if not eventos_seguranca.empty:
            st.markdown("**Eventos de Segurança (Últimas 24h)**")
            
            for _, evento in eventos_seguranca.iterrows():
                severity = evento.get('severity', 'INFO')
                
                if severity == 'CRITICAL':
                    st.error(f"🚨 {evento['event_type']}")
                elif severity == 'ERROR':
                    st.warning(f"⚠️ {evento['event_type']}")
                else:
                    st.info(f"ℹ️ {evento['event_type']}")
        else:
            st.success("✅ Nenhum evento de segurança crítico nas últimas 24h")
        
        # Botão para exportar relatório
        if st.button("📥 Exportar Relatório Completo"):
            _exportar_relatorio_completo()

def _ler_logs_arquivo(arquivo, data_inicio, data_fim, limite):
    """Lê logs de um arquivo específico"""
    try:
        if not os.path.exists(arquivo):
            return pd.DataFrame()
        
        logs = []
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                try:
                    # Extrair timestamp do início da linha
                    if ' - ' in linha:
                        timestamp_str = linha.split(' - ')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        
                        # Filtrar por data
                        if data_inicio <= timestamp.date() <= data_fim:
                            # Tentar extrair JSON da linha
                            if '{' in linha and '}' in linha:
                                json_start = linha.find('{')
                                json_str = linha[json_start:]
                                
                                try:
                                    log_data = json.loads(json_str)
                                    log_data['timestamp'] = timestamp_str
                                    logs.append(log_data)
                                except json.JSONDecodeError:
                                    # Se não for JSON válido, criar entrada simples
                                    logs.append({
                                        'timestamp': timestamp_str,
                                        'message': linha.strip()
                                    })
                            
                            if len(logs) >= limite:
                                break
                                
                except Exception:
                    continue
        
        return pd.DataFrame(logs)
        
    except Exception as e:
        st.error(f"Erro ao ler arquivo de log {arquivo}: {str(e)}")
        return pd.DataFrame()

def _obter_estatisticas_gerais():
    """Obtém estatísticas gerais dos logs"""
    stats = {}
    
    arquivos = [
        ('total_audit', 'logs/audit.log'),
        ('total_security', 'logs/security.log'),
        ('total_operations', 'logs/operations.log')
    ]
    
    for key, arquivo in arquivos:
        try:
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    stats[key] = sum(1 for _ in f)
            else:
                stats[key] = 0
        except Exception:
            stats[key] = 0
    
    return stats

def _obter_usuarios_mais_ativos():
    """Obtém usuários mais ativos dos últimos 7 dias"""
    data_inicio = date.today() - timedelta(days=7)
    data_fim = date.today()
    
    logs_df = _ler_logs_arquivo('logs/audit.log', data_inicio, data_fim, 10000)
    
    if not logs_df.empty and 'user_id' in logs_df.columns:
        usuarios_ativos = logs_df.groupby('user_id').size().reset_index()
        usuarios_ativos.columns = ['user_id', 'total_acoes']
        usuarios_ativos = usuarios_ativos.sort_values('total_acoes', ascending=False).head(10)
        return usuarios_ativos
    
    return pd.DataFrame()

def _obter_eventos_seguranca_recentes():
    """Obtém eventos de segurança das últimas 24h"""
    data_inicio = date.today() - timedelta(days=1)
    data_fim = date.today()
    
    logs_df = _ler_logs_arquivo('logs/security.log', data_inicio, data_fim, 100)
    
    if not logs_df.empty:
        # Filtrar apenas eventos críticos e de erro
        eventos_importantes = logs_df[
            logs_df['severity'].isin(['CRITICAL', 'ERROR'])
        ] if 'severity' in logs_df.columns else logs_df
        
        return eventos_importantes.head(10)
    
    return pd.DataFrame()

def _exportar_relatorio_completo():
    """Exporta relatório completo de auditoria"""
    try:
        data_inicio = date.today() - timedelta(days=30)
        data_fim = date.today()
        
        # Coletar todos os logs
        audit_logs = _ler_logs_arquivo('logs/audit.log', data_inicio, data_fim, 10000)
        security_logs = _ler_logs_arquivo('logs/security.log', data_inicio, data_fim, 10000)
        operations_logs = _ler_logs_arquivo('logs/operations.log', data_inicio, data_fim, 10000)
        
        # Criar arquivo de relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_auditoria_{timestamp}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if not audit_logs.empty:
                audit_logs.to_excel(writer, sheet_name='Logs_Auditoria', index=False)
            
            if not security_logs.empty:
                security_logs.to_excel(writer, sheet_name='Logs_Seguranca', index=False)
            
            if not operations_logs.empty:
                operations_logs.to_excel(writer, sheet_name='Logs_Operacoes', index=False)
        
        st.success(f"✅ Relatório exportado: {filename}")
        
        # Oferecer download
        with open(filename, 'rb') as f:
            st.download_button(
                label="📥 Baixar Relatório",
                data=f.read(),
                file_name=filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        st.error(f"Erro ao exportar relatório: {str(e)}")