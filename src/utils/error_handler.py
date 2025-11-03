"""
Tratamento de Erros
"""
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, List
from datetime import datetime

# Configurar logging
import os
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sistema_rh.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemError(Exception):
    """Erro base do sistema"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or "SYSTEM_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class DatabaseError(SystemError):
    """Erro de banco de dados"""
    def __init__(self, message: str, query: str = None, params: Any = None):
        super().__init__(message, "DB_ERROR", {"query": query, "params": params})

class ValidationError(SystemError):
    """Erro de validação"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})

class AuthenticationError(SystemError):
    """Erro de autenticação"""
    def __init__(self, message: str, user_email: str = None):
        super().__init__(message, "AUTH_ERROR", {"user_email": user_email})

def handle_critical_operation(operation_name: str, log_errors: bool = True):
    """
    Decorator para tratamento de operações críticas.
    
    Args:
        operation_name: Nome da operação
        log_errors: Se deve logar erros
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
            try:
                logger.info(f"Iniciando operação crítica: {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Operação {operation_name} concluída com sucesso")
                return True, result, None
                
            except ValidationError as e:
                error_msg = f"Erro de validação em {operation_name}: {e.message}"
                if log_errors:
                    logger.error(error_msg, extra={"details": e.details})
                return False, None, e.message
                
            except DatabaseError as e:
                error_msg = f"Erro de banco em {operation_name}: {e.message}"
                if log_errors:
                    logger.error(error_msg, extra={"details": e.details})
                return False, None, "Erro interno do sistema. Tente novamente."
                
            except AuthenticationError as e:
                error_msg = f"Erro de autenticação em {operation_name}: {e.message}"
                if log_errors:
                    logger.warning(error_msg, extra={"details": e.details})
                return False, None, e.message
                
            except Exception as e:
                error_msg = f"Erro inesperado em {operation_name}: {str(e)}"
                if log_errors:
                    logger.critical(error_msg, extra={
                        "traceback": traceback.format_exc(),
                        "args": args,
                        "kwargs": kwargs
                    })
                return False, None, "Erro interno do sistema. Contate o administrador."
                
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Executa função de forma segura com tratamento de erro.
    
    Args:
        func: Função a ser executada
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Tupla (sucesso, resultado, mensagem_erro)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except SystemError as e:
        logger.error(f"Erro do sistema: {e.message}", extra={"details": e.details})
        return False, None, e.message
    except Exception as e:
        logger.critical(f"Erro inesperado: {str(e)}", extra={"traceback": traceback.format_exc()})
        return False, None, "Erro interno do sistema"

def validate_required_fields(data: Dict, required_fields: list) -> None:
    """
    Valida campos obrigatórios.
    
    Args:
        data: Dados a validar
        required_fields: Lista de campos obrigatórios
        
    Raises:
        ValidationError: Se algum campo obrigatório estiver ausente
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
            field=missing_fields[0]
        )

def log_operation(operation: str, user_id: int = None, details: Dict = None):
    """
    Registra operação no log.
    
    Args:
        operation: Nome da operação
        user_id: ID do usuário
        details: Detalhes adicionais
    """
    logger.info(f"Operação: {operation}", extra={
        "user_id": user_id,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    })

class BusinessRuleError(SystemError):
    """Erro de regra de negócio"""
    def __init__(self, message: str, rule_name: str = None, context: Dict = None):
        super().__init__(message, "BUSINESS_RULE_ERROR", {"rule": rule_name, "context": context})

class ResourceError(SystemError):
    """Erro de recurso (conexão, arquivo, etc.)"""
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None):
        super().__init__(message, "RESOURCE_ERROR", {"type": resource_type, "id": resource_id})

def handle_database_operation(operation_name: str):
    """Decorator específico para operações de banco"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
            try:
                logger.info(f"Iniciando operação de banco: {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Operação {operation_name} concluída")
                return True, result, None
                
            except DatabaseError as e:
                logger.error(f"Erro de banco em {operation_name}: {e.message}", extra={"details": e.details})
                return False, None, "Erro de banco de dados. Tente novamente."
                
            except ValidationError as e:
                logger.warning(f"Erro de validação em {operation_name}: {e.message}")
                return False, None, e.message
                
            except Exception as e:
                logger.critical(f"Erro crítico em {operation_name}: {str(e)}", extra={"traceback": traceback.format_exc()})
                return False, None, "Erro interno do sistema"
                
        return wrapper
    return decorator

def handle_business_operation(operation_name: str, user_friendly: bool = True):
    """Decorator para operações de negócio com mensagens amigáveis"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
            try:
                result = func(*args, **kwargs)
                return True, result, None
                
            except BusinessRuleError as e:
                logger.warning(f"Regra de negócio violada em {operation_name}: {e.message}")
                return False, None, e.message if user_friendly else "Operação não permitida"
                
            except ValidationError as e:
                logger.info(f"Validação falhou em {operation_name}: {e.message}")
                return False, None, e.message
                
            except Exception as e:
                logger.error(f"Erro em operação de negócio {operation_name}: {str(e)}")
                return False, None, "Erro interno" if not user_friendly else "Operação não pôde ser concluída"
                
        return wrapper
    return decorator

class ErrorRecovery:
    """Classe para recuperação de erros"""
    
    @staticmethod
    def retry_operation(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Tuple[bool, Any, Optional[str]]:
        """
        Tenta executar operação com retry.
        
        Args:
            func: Função a executar
            max_attempts: Máximo de tentativas
            delay: Delay entre tentativas
            
        Returns:
            Tupla (sucesso, resultado, erro)
        """
        import time
        
        for attempt in range(max_attempts):
            try:
                result = func()
                return True, result, None
            except Exception as e:
                if attempt == max_attempts - 1:
                    logger.error(f"Falha após {max_attempts} tentativas: {str(e)}")
                    return False, None, str(e)
                else:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Tentando novamente...")
                    time.sleep(delay)
        
        return False, None, "Máximo de tentativas excedido"
    
    @staticmethod
    def safe_database_operation(operation: Callable, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Executa operação de banco com tratamento robusto"""
        try:
            result = operation(*args, **kwargs)
            return True, result, None
        except DatabaseError as e:
            logger.error(f"Erro de banco: {e.message}", extra={"details": e.details})
            return False, None, "Erro de banco de dados"
        except Exception as e:
            logger.critical(f"Erro crítico em operação de banco: {str(e)}")
            return False, None, "Erro interno do sistema"
    
    @staticmethod
    def validate_and_execute(validation_func: Callable, operation_func: Callable, 
                           *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Valida dados antes de executar operação"""
        try:
            # Executar validação
            validation_result = validation_func(*args, **kwargs)
            if not validation_result.get("valido", False):
                return False, None, validation_result.get("erro", "Dados inválidos")
            
            # Executar operação
            result = operation_func(*args, **kwargs)
            return True, result, None
            
        except ValidationError as e:
            return False, None, e.message
        except Exception as e:
            logger.error(f"Erro em validação e execução: {str(e)}")
            return False, None, "Erro interno"

class CriticalOperationManager:
    """Gerenciador para operações críticas do sistema"""
    
    @staticmethod
    def execute_with_rollback(operations: List[Callable], rollback_operations: List[Callable] = None) -> Tuple[bool, Any, Optional[str]]:
        """Executa operações com rollback automático em caso de erro"""
        executed_operations = []
        
        try:
            results = []
            for i, operation in enumerate(operations):
                result = operation()
                results.append(result)
                executed_operations.append(i)
            
            return True, results, None
            
        except Exception as e:
            logger.error(f"Erro em operação crítica: {str(e)}")
            
            # Executar rollback
            if rollback_operations:
                for i in reversed(executed_operations):
                    if i < len(rollback_operations) and rollback_operations[i]:
                        try:
                            rollback_operations[i]()
                        except Exception as rollback_error:
                            logger.critical(f"Erro no rollback: {str(rollback_error)}")
            
            return False, None, "Operação crítica falhou"
    
    @staticmethod
    def monitor_resource_usage(func: Callable) -> Callable:
        """Decorator para monitorar uso de recursos"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                memory_after = process.memory_info().rss
                memory_diff = memory_after - memory_before
                
                if memory_diff > 50 * 1024 * 1024:  # 50MB
                    logger.warning(f"Alto uso de memória em {func.__name__}: {memory_diff / 1024 / 1024:.2f}MB")
        
        return wrapper