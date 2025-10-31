"""
Painel de Debug - Interface visual para monitoramento em tempo real
"""
import streamlit as st
import os
import sys
from datetime import datetime
from .debug_system import logger
from .debug_config import DEBUG_SETTINGS, get_debug_setting

def show_debug_panel(context="main"):
    """Exibe painel de debug na sidebar"""
    if not get_debug_setting("ENABLE_DEBUG", False):
        return
    
    with st.sidebar.expander("🔧 Debug Panel", expanded=False):
        st.markdown("**Sistema de Debug**")
        
        # Status geral
        st.markdown(f"**Status:** {'🟢 Ativo' if get_debug_setting('ENABLE_DEBUG') else '🔴 Inativo'}")
        st.markdown(f"**Nível:** {get_debug_setting('LOG_LEVEL', 'INFO')}")
        
        # Informações do sistema
        st.markdown("---")
        st.markdown("**Sistema:**")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"PID: {os.getpid()}")
        st.text(f"Diretório: {os.getcwd()}")
        
        # Session State
        if st.checkbox("Mostrar Session State", key=f"debug_show_session_state_{context}"):
            show_session_state_debug()
        
        # Logs recentes
        if st.checkbox("Logs Recentes", key=f"debug_show_recent_logs_{context}"):
            show_recent_logs()
        
        # Controles de debug
        st.markdown("---")
        st.markdown("**Controles:**")
        
        if st.button("Limpar Logs", key=f"debug_clear_logs_{context}"):
            clear_logs()
            st.success("Logs limpos!")
        
        if st.button("Exportar Debug", key=f"debug_export_info_{context}"):
            export_debug_info()
            st.success("Debug exportado!")

def show_session_state_debug():
    """Mostra estado da sessão Streamlit"""
    st.markdown("**Session State:**")
    
    if hasattr(st, 'session_state'):
        for key, value in st.session_state.items():
            if key.startswith('_'):  # Pular chaves internas
                continue
            
            value_type = type(value).__name__
            value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            
            st.text(f"{key}: {value_type}")
            if st.checkbox(f"Detalhes de {key}", key=f"debug_{key}"):
                st.code(value_str)
    else:
        st.text("Session state não disponível")

def show_recent_logs():
    """Mostra logs recentes"""
    log_file = get_debug_setting("LOG_FILE_PATH", "logs/debug_sistema.log")
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-20:]  # Últimas 20 linhas
                
            st.text_area("Logs Recentes:", "\n".join(recent_lines), height=200)
        except Exception as e:
            st.error(f"Erro ao ler logs: {e}")
    else:
        st.text("Arquivo de log não encontrado")

def clear_logs():
    """Limpa arquivos de log"""
    log_file = get_debug_setting("LOG_FILE_PATH", "logs/debug_sistema.log")
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write(f"# Log limpo em {datetime.now()}\n")
            logger.info("Logs limpos pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao limpar logs: {e}")

def export_debug_info():
    """Exporta informações de debug"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "pid": os.getpid(),
            "cwd": os.getcwd(),
        },
        "debug_settings": DEBUG_SETTINGS,
        "session_state": {}
    }
    
    # Adicionar session state (sem dados sensíveis)
    if hasattr(st, 'session_state'):
        for key, value in st.session_state.items():
            if not key.startswith('_'):
                debug_info["session_state"][key] = type(value).__name__
    
    # Salvar em arquivo
    export_file = f"debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        import json
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Debug exportado para: {export_file}")
    except Exception as e:
        logger.error(f"Erro ao exportar debug: {e}")

def log_performance_metrics():
    """Registra métricas de performance"""
    if not get_debug_setting("LOG_EXECUTION_TIME", False):
        return
    
    try:
        import psutil
        process = psutil.Process()
        
        metrics = {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
        }
        
        logger.debug(f"Performance: {metrics}")
    except ImportError:
        pass  # psutil não disponível
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {e}")

def debug_database_queries():
    """Debug específico para queries de banco"""
    if not get_debug_setting("DEBUG_DATABASE", False):
        return
    
    # Implementar monitoramento de queries
    pass

def show_debug_metrics():
    """Exibe métricas de debug na interface"""
    if not get_debug_setting("ENABLE_DEBUG", False):
        return
    
    # Mostrar métricas em tempo real
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Debug Status", "🟢 Ativo" if get_debug_setting("ENABLE_DEBUG") else "🔴 Inativo")
    
    with col2:
        log_level = get_debug_setting("LOG_LEVEL", "INFO")
        st.metric("Log Level", log_level)
    
    with col3:
        # Contar logs recentes
        log_count = count_recent_logs()
        st.metric("Logs Hoje", log_count)

def count_recent_logs():
    """Conta logs do dia atual"""
    log_file = get_debug_setting("LOG_FILE_PATH", "logs/debug_sistema.log")
    
    if not os.path.exists(log_file):
        return 0
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        count = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if today in line:
                    count += 1
        
        return count
    except Exception:
        return 0

# Função para adicionar debug em qualquer página
def add_debug_to_page(page_name: str):
    """Adiciona debug a uma página específica"""
    if get_debug_setting("ENABLE_DEBUG", False):
        logger.info(f"Renderizando página: {page_name}")
        
        # Adicionar métricas se habilitado
        if get_debug_setting("LOG_EXECUTION_TIME", False):
            log_performance_metrics()
        
        # Mostrar painel se solicitado
        if get_debug_setting("DEBUG_STREAMLIT", False):
            show_debug_panel(page_name)