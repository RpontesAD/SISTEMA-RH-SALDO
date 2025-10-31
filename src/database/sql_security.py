"""
Utilitários de Segurança SQL - Prevenção de injeção SQL
"""
import re
from typing import Any, Dict, List, Tuple, Union

class SQLSecurity:
    """Classe para validação e sanitização de queries SQL"""
    
    # Palavras-chave perigosas
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'UNION', 'SCRIPT', 'JAVASCRIPT', 'VBSCRIPT',
        '--', '/*', '*/', 'xp_', 'sp_', 'INFORMATION_SCHEMA', 'SYSOBJECTS'
    ]
    
    # Padrões perigosos
    DANGEROUS_PATTERNS = [
        r';\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE)',
        r'UNION\s+SELECT',
        r'OR\s+1\s*=\s*1',
        r'AND\s+1\s*=\s*1',
        r'\';\s*--',
        r'/\*.*?\*/',
        r'--.*$'
    ]
    
    @staticmethod
    def validate_input(value: Any) -> bool:
        """
        Valida entrada para prevenir injeção SQL.
        
        Args:
            value: Valor a ser validado
            
        Returns:
            True se seguro, False caso contrário
        """
        if not isinstance(value, str):
            return True
        
        # Verificar palavras-chave perigosas
        value_upper = value.upper()
        for keyword in SQLSecurity.DANGEROUS_KEYWORDS:
            if keyword in value_upper:
                return False
        
        # Verificar padrões perigosos
        for pattern in SQLSecurity.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitiza string para uso seguro em SQL.
        
        Args:
            value: String a ser sanitizada
            
        Returns:
            String sanitizada
        """
        if not isinstance(value, str):
            return str(value)
        
        # Escapar aspas simples
        sanitized = value.replace("'", "''")
        
        # Remover caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limitar tamanho
        sanitized = sanitized[:1000]
        
        return sanitized
    
    @staticmethod
    def validate_params(params: Union[List, Tuple, Dict]) -> bool:
        """
        Valida parâmetros de query.
        
        Args:
            params: Parâmetros a serem validados
            
        Returns:
            True se todos os parâmetros são seguros
        """
        if isinstance(params, (list, tuple)):
            return all(SQLSecurity.validate_input(param) for param in params)
        elif isinstance(params, dict):
            return all(SQLSecurity.validate_input(value) for value in params.values())
        else:
            return SQLSecurity.validate_input(params)

class SecureQuery:
    """Classe para construção segura de queries SQL"""
    
    def __init__(self):
        self.query = ""
        self.params = []
    
    def select(self, columns: Union[str, List[str]], table: str) -> 'SecureQuery':
        """Inicia SELECT seguro"""
        if isinstance(columns, list):
            columns = ", ".join(columns)
        
        # Validar nome da tabela
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Nome de tabela inválido: {table}")
        
        self.query = f"SELECT {columns} FROM {table}"
        return self
    
    def where(self, condition: str, *params) -> 'SecureQuery':
        """Adiciona WHERE com parâmetros seguros"""
        # Validar parâmetros
        if not SQLSecurity.validate_params(params):
            raise ValueError("Parâmetros contêm conteúdo perigoso")
        
        self.query += f" WHERE {condition}"
        self.params.extend(params)
        return self
    
    def insert(self, table: str, data: Dict[str, Any]) -> 'SecureQuery':
        """Cria INSERT seguro"""
        # Validar nome da tabela
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Nome de tabela inválido: {table}")
        
        # Validar dados
        if not SQLSecurity.validate_params(data):
            raise ValueError("Dados contêm conteúdo perigoso")
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        
        self.query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.params = list(data.values())
        return self
    
    def update(self, table: str, data: Dict[str, Any]) -> 'SecureQuery':
        """Cria UPDATE seguro"""
        # Validar nome da tabela
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Nome de tabela inválido: {table}")
        
        # Validar dados
        if not SQLSecurity.validate_params(data):
            raise ValueError("Dados contêm conteúdo perigoso")
        
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        
        self.query = f"UPDATE {table} SET {set_clause}"
        self.params = list(data.values())
        return self
    
    def delete(self, table: str) -> 'SecureQuery':
        """Cria DELETE seguro"""
        # Validar nome da tabela
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Nome de tabela inválido: {table}")
        
        self.query = f"DELETE FROM {table}"
        return self
    
    def build(self) -> Tuple[str, List]:
        """Constrói query final com parâmetros"""
        return self.query, self.params

def secure_execute(connection, query: str, params: List = None) -> Any:
    """
    Executa query de forma segura.
    
    Args:
        connection: Conexão com banco
        query: Query SQL
        params: Parâmetros da query
        
    Returns:
        Resultado da execução
    """
    # Validar parâmetros
    if params and not SQLSecurity.validate_params(params):
        raise ValueError("Parâmetros contêm conteúdo perigoso")
    
    # Executar com prepared statement
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall() if query.strip().upper().startswith('SELECT') else cursor.lastrowid
    finally:
        cursor.close()