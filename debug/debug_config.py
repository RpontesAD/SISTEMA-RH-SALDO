"""
Configuração de Debug - Controle centralizado do sistema de debug
"""

# Configurações de debug
DEBUG_SETTINGS = {
    # Nível geral de debug
    "ENABLE_DEBUG": True,
    "LOG_LEVEL": "DEBUG",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Componentes específicos
    "DEBUG_DATABASE": True,
    "DEBUG_AUTH": True,
    "DEBUG_STREAMLIT": True,
    "DEBUG_BUSINESS_LOGIC": True,
    "DEBUG_API_CALLS": True,
    
    # Detalhamento
    "LOG_FUNCTION_ARGS": False,  # Pode expor dados sensíveis
    "LOG_FUNCTION_RESULTS": False,  # Pode expor dados sensíveis
    "LOG_SQL_QUERIES": True,
    "LOG_USER_ACTIONS": True,
    "LOG_SESSION_STATE": True,
    
    # Performance
    "LOG_EXECUTION_TIME": True,
    "LOG_MEMORY_USAGE": False,
    
    # Arquivos de log
    "LOG_TO_FILE": True,
    "LOG_TO_CONSOLE": True,
    "LOG_FILE_PATH": "logs/debug_sistema.log",
    "MAX_LOG_SIZE_MB": 50,
    "BACKUP_COUNT": 5,
}

def get_debug_setting(key: str, default=None):
    """Obtém configuração de debug"""
    return DEBUG_SETTINGS.get(key, default)

def is_debug_enabled(component: str = None) -> bool:
    """Verifica se debug está habilitado para um componente"""
    if not DEBUG_SETTINGS.get("ENABLE_DEBUG", False):
        return False
    
    if component:
        component_key = f"DEBUG_{component.upper()}"
        return DEBUG_SETTINGS.get(component_key, True)
    
    return True

def set_debug_setting(key: str, value):
    """Define configuração de debug"""
    DEBUG_SETTINGS[key] = value

# Configurações específicas por ambiente
ENVIRONMENT_CONFIGS = {
    "development": {
        "ENABLE_DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "LOG_FUNCTION_ARGS": True,
        "LOG_FUNCTION_RESULTS": True,
    },
    "testing": {
        "ENABLE_DEBUG": True,
        "LOG_LEVEL": "INFO",
        "LOG_FUNCTION_ARGS": False,
        "LOG_FUNCTION_RESULTS": False,
    },
    "production": {
        "ENABLE_DEBUG": False,
        "LOG_LEVEL": "WARNING",
        "LOG_FUNCTION_ARGS": False,
        "LOG_FUNCTION_RESULTS": False,
        "LOG_SQL_QUERIES": False,
    }
}

def apply_environment_config(env: str):
    """Aplica configuração específica do ambiente"""
    if env in ENVIRONMENT_CONFIGS:
        DEBUG_SETTINGS.update(ENVIRONMENT_CONFIGS[env])
        print(f"Configuração de debug aplicada para ambiente: {env}")
    else:
        print(f"Ambiente desconhecido: {env}")

# Aplicar configuração baseada em variável de ambiente
import os
current_env = os.getenv("ENVIRONMENT", "development")
apply_environment_config(current_env)