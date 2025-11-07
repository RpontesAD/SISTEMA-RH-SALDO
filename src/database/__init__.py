from .database_manager import DatabaseManager

# Usar nova estrutura modular como padrão
Database = DatabaseManager

# Manter compatibilidade
SimplePsycopg2Database = DatabaseManager
SimplePsycopg2 = DatabaseManager