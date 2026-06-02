from .database_manager import DatabaseManager
from .sqlite_database import SQLiteDatabase

# Usar nova estrutura modular como padrão para ambientes locais e testes
Database = SQLiteDatabase

# Manter compatibilidade
SimplePsycopg2Database = DatabaseManager
SimplePsycopg2 = DatabaseManager
SQLiteDatabase = SQLiteDatabase