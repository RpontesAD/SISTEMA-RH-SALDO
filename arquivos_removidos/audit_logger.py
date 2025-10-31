"""
Sistema de Auditoria e Logging Completo
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import os

class AuditLogger:
    """Sistema centralizado de auditoria e logging"""
    
    def __init__(self):
        self.setup_loggers()
    
    def setup_loggers(self):
        """Configura loggers especializados"""
        # Logger de auditoria
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Logger de segurança
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.WARNING)
        
        # Logger de operações
        self.operations_logger = logging.getLogger('operations')
        self.operations_logger.setLevel(logging.INFO)
        
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
        
        # Handlers para auditoria
        audit_handler = logging.FileHandler('logs/audit.log', encoding='utf-8')
        audit_handler.setFormatter(logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        ))
        self.audit_logger.addHandler(audit_handler)
        
        # Handlers para segurança
        security_handler = logging.FileHandler('logs/security.log', encoding='utf-8')
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        ))
        self.security_logger.addHandler(security_handler)
        
        # Handlers para operações
        ops_handler = logging.FileHandler('logs/operations.log', encoding='utf-8')
        ops_handler.setFormatter(logging.Formatter(
            '%(asctime)s - OPS - %(levelname)s - %(message)s'
        ))
        self.operations_logger.addHandler(ops_handler)
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None, 
                       ip_address: str = None, user_agent: str = None):
        """Log de ações do usuário"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        self.audit_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_data_change(self, user_id: int, table: str, record_id: Any, 
                       old_values: Dict = None, new_values: Dict = None, 
                       operation: str = 'UPDATE'):
        """Log de alterações de dados"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'operation': operation,
            'table': table,
            'record_id': record_id,
            'old_values': old_values or {},
            'new_values': new_values or {}
        }
        self.audit_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_security_event(self, event_type: str, user_id: int = None, 
                          details: Dict[str, Any] = None, severity: str = 'WARNING'):
        """Log de eventos de segurança"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'severity': severity,
            'details': details or {}
        }
        
        if severity == 'CRITICAL':
            self.security_logger.critical(json.dumps(log_data, ensure_ascii=False))
        elif severity == 'ERROR':
            self.security_logger.error(json.dumps(log_data, ensure_ascii=False))
        else:
            self.security_logger.warning(json.dumps(log_data, ensure_ascii=False))
    
    def log_system_operation(self, operation: str, status: str, duration: float = None,
                           details: Dict[str, Any] = None):
        """Log de operações do sistema"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'status': status,
            'duration_ms': duration,
            'details': details or {}
        }
        self.operations_logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_business_rule_violation(self, rule_name: str, user_id: int = None,
                                  context: Dict[str, Any] = None):
        """Log de violações de regras de negócio"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'rule_name': rule_name,
            'user_id': user_id,
            'context': context or {}
        }
        self.audit_logger.warning(json.dumps(log_data, ensure_ascii=False))

# Instância global
audit_logger = AuditLogger()

def audit_action(action_name: str, log_params: bool = True):
    """Decorator para auditoria automática de ações"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                # Log de sucesso
                duration = (datetime.now() - start_time).total_seconds() * 1000
                details = {}
                
                if log_params:
                    details['args'] = str(args)[:200]  # Limitar tamanho
                    details['kwargs'] = {k: str(v)[:100] for k, v in kwargs.items()}
                
                audit_logger.log_system_operation(
                    operation=f"{func.__module__}.{func.__name__}",
                    status='SUCCESS',
                    duration=duration,
                    details=details
                )
                
                return result
                
            except Exception as e:
                # Log de erro
                duration = (datetime.now() - start_time).total_seconds() * 1000
                audit_logger.log_system_operation(
                    operation=f"{func.__module__}.{func.__name__}",
                    status='ERROR',
                    duration=duration,
                    details={'error': str(e)}
                )
                raise
                
        return wrapper
    return decorator

def audit_data_change(table_name: str):
    """Decorator para auditoria de alterações de dados"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Capturar user_id se disponível
            user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
            
            try:
                result = func(*args, **kwargs)
                
                # Log da alteração
                audit_logger.log_data_change(
                    user_id=user_id,
                    table=table_name,
                    record_id=kwargs.get('record_id', 'unknown'),
                    operation=func.__name__.upper()
                )
                
                return result
                
            except Exception as e:
                # Log do erro
                audit_logger.log_security_event(
                    event_type='DATA_OPERATION_FAILED',
                    user_id=user_id,
                    details={
                        'table': table_name,
                        'operation': func.__name__,
                        'error': str(e)
                    }
                )
                raise
                
        return wrapper
    return decorator

class ComplianceLogger:
    """Logger específico para compliance e regulamentações"""
    
    @staticmethod
    def log_gdpr_access(user_id: int, data_accessed: str, purpose: str):
        """Log de acesso a dados pessoais (GDPR)"""
        audit_logger.log_user_action(
            user_id=user_id,
            action='GDPR_DATA_ACCESS',
            details={
                'data_accessed': data_accessed,
                'purpose': purpose,
                'compliance': 'GDPR'
            }
        )
    
    @staticmethod
    def log_data_retention(table: str, records_deleted: int, retention_policy: str):
        """Log de retenção de dados"""
        audit_logger.log_system_operation(
            operation='DATA_RETENTION',
            status='COMPLETED',
            details={
                'table': table,
                'records_deleted': records_deleted,
                'retention_policy': retention_policy
            }
        )
    
    @staticmethod
    def log_backup_operation(backup_type: str, status: str, file_path: str = None):
        """Log de operações de backup"""
        audit_logger.log_system_operation(
            operation='BACKUP',
            status=status,
            details={
                'backup_type': backup_type,
                'file_path': file_path
            }
        )

class SecurityAudit:
    """Auditoria específica de segurança"""
    
    @staticmethod
    def log_login_attempt(email: str, success: bool, ip_address: str = None):
        """Log de tentativas de login"""
        event_type = 'LOGIN_SUCCESS' if success else 'LOGIN_FAILED'
        severity = 'INFO' if success else 'WARNING'
        
        audit_logger.log_security_event(
            event_type=event_type,
            details={
                'email': email,
                'ip_address': ip_address
            },
            severity=severity
        )
    
    @staticmethod
    def log_permission_violation(user_id: int, attempted_action: str, resource: str):
        """Log de violações de permissão"""
        audit_logger.log_security_event(
            event_type='PERMISSION_VIOLATION',
            user_id=user_id,
            details={
                'attempted_action': attempted_action,
                'resource': resource
            },
            severity='ERROR'
        )
    
    @staticmethod
    def log_suspicious_activity(user_id: int, activity_type: str, details: Dict):
        """Log de atividades suspeitas"""
        audit_logger.log_security_event(
            event_type='SUSPICIOUS_ACTIVITY',
            user_id=user_id,
            details={
                'activity_type': activity_type,
                **details
            },
            severity='CRITICAL'
        )