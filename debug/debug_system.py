"""
Sistema de Debug Abrangente - Logging detalhado para toda aplicação
"""
import logging
import os
import sys
import traceback
from datetime import datetime
from functools import wraps
import streamlit as st

# Configurar diretório de logs
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar formatação de logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

# Configurar handler para arquivo
file_handler = logging.FileHandler(f'{LOG_DIR}/debug_sistema.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configurar handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))

# Configurar logger principal
logger = logging.getLogger('RPONTES_RH')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class DebugManager:
    """Gerenciador central de debug"""
    
    @staticmethod
    def log_function_entry(func_name: str, args=None, kwargs=None):
        """Log de entrada em função"""
        logger.debug(f"ENTRADA: {func_name}")
        if args:
            logger.debug(f"  Args: {args}")
        if kwargs:
            logger.debug(f"  Kwargs: {kwargs}")
    
    @staticmethod
    def log_function_exit(func_name: str, result=None):
        """Log de saída de função"""
        logger.debug(f"SAÍDA: {func_name}")
        if result is not None:
            logger.debug(f"  Resultado: {type(result).__name__}")
    
    @staticmethod
    def log_error(func_name: str, error: Exception):
        """Log de erro detalhado"""
        logger.error(f"ERRO em {func_name}: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    @staticmethod
    def log_database_operation(operation: str, query: str = None, params=None):
        """Log de operações de banco"""
        logger.info(f"DB_OP: {operation}")
        if query:
            logger.debug(f"  Query: {query}")
        if params:
            logger.debug(f"  Params: {params}")
    
    @staticmethod
    def log_user_action(user_id: int, action: str, details=None):
        """Log de ações do usuário"""
        logger.info(f"USER_ACTION: User {user_id} - {action}")
        if details:
            logger.debug(f"  Detalhes: {details}")
    
    @staticmethod
    def log_streamlit_state(component: str):
        """Log do estado do Streamlit"""
        logger.debug(f"STREAMLIT_STATE: {component}")
        if hasattr(st, 'session_state'):
            keys = list(st.session_state.keys())
            logger.debug(f"  Session keys: {keys}")

def debug_decorator(log_args=True, log_result=True):
    """Decorator para debug automático de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Log entrada
            if log_args:
                DebugManager.log_function_entry(func_name, args, kwargs)
            else:
                DebugManager.log_function_entry(func_name)
            
            try:
                # Executar função
                result = func(*args, **kwargs)
                
                # Log saída
                if log_result:
                    DebugManager.log_function_exit(func_name, result)
                else:
                    DebugManager.log_function_exit(func_name)
                
                return result
                
            except Exception as e:
                # Log erro
                DebugManager.log_error(func_name, e)
                raise
        
        return wrapper
    return decorator

def debug_streamlit_component(component_name: str):
    """Debug específico para componentes Streamlit"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"STREAMLIT: Renderizando {component_name}")
            DebugManager.log_streamlit_state(component_name)
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"STREAMLIT: {component_name} renderizado com sucesso")
                return result
            except Exception as e:
                logger.error(f"STREAMLIT: Erro em {component_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator

class DatabaseDebugger:
    """Debug específico para operações de banco"""
    
    @staticmethod
    def log_connection(db_type: str, status: str):
        """Log de conexão com banco"""
        logger.info(f"DB_CONNECTION: {db_type} - {status}")
    
    @staticmethod
    def log_query_execution(query: str, params=None, execution_time=None):
        """Log de execução de query"""
        logger.debug(f"DB_QUERY: {query}")
        if params:
            logger.debug(f"DB_PARAMS: {params}")
        if execution_time:
            logger.debug(f"DB_TIME: {execution_time}ms")
    
    @staticmethod
    def log_transaction(operation: str, status: str):
        """Log de transações"""
        logger.info(f"DB_TRANSACTION: {operation} - {status}")

class AuthDebugger:
    """Debug específico para autenticação"""
    
    @staticmethod
    def log_login_attempt(email: str, success: bool):
        """Log de tentativa de login"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUTH_LOGIN: {email} - {status}")
    
    @staticmethod
    def log_session_creation(user_id: int):
        """Log de criação de sessão"""
        logger.info(f"AUTH_SESSION: Criada para user {user_id}")
    
    @staticmethod
    def log_permission_check(user_id: int, resource: str, allowed: bool):
        """Log de verificação de permissão"""
        status = "ALLOWED" if allowed else "DENIED"
        logger.info(f"AUTH_PERMISSION: User {user_id} - {resource} - {status}")

class BusinessLogicDebugger:
    """Debug específico para regras de negócio"""
    
    @staticmethod
    def log_validation(rule_name: str, data, result: bool):
        """Log de validação de regras"""
        status = "VALID" if result else "INVALID"
        logger.info(f"BUSINESS_RULE: {rule_name} - {status}")
        logger.debug(f"  Data: {data}")
    
    @staticmethod
    def log_calculation(calc_type: str, input_data, result):
        """Log de cálculos"""
        logger.info(f"CALCULATION: {calc_type}")
        logger.debug(f"  Input: {input_data}")
        logger.debug(f"  Result: {result}")

def setup_debug_mode():
    """Configura modo debug para toda aplicação"""
    logger.info("=" * 50)
    logger.info("SISTEMA DE DEBUG ATIVADO")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Python Version: {sys.version}")
    logger.info("=" * 50)

def log_system_info():
    """Log informações do sistema"""
    import platform
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Working Directory: {os.getcwd()}")

def debug_session_state():
    """Debug do estado da sessão Streamlit"""
    if hasattr(st, 'session_state'):
        logger.debug("SESSION_STATE:")
        for key, value in st.session_state.items():
            logger.debug(f"  {key}: {type(value).__name__}")

# Configurar debug no import
setup_debug_mode()
log_system_info()