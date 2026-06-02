"""Compatibilidade com a antiga API de conexão do banco de dados."""
from .sqlite_database import SQLiteDatabase


def get_connection(path=":memory:"):
    """Retorna uma conexão SQLite para testes legados."""
    return SQLiteDatabase(path).get_connection()


class DatabaseConnection(SQLiteDatabase):
    """Compatibilidade com a antiga classe DatabaseConnection usada em testes."""

    def __init__(self, path=":memory:"):
        super().__init__(path)

    def init_database(self):
        return super().init_database()
