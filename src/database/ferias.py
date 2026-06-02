"""Compatibilidade com a antiga API de férias usada em testes."""
from .sqlite_database import SQLiteDatabase


class FeriasDatabase(SQLiteDatabase):
    """Wrapper compatível com os testes antigos que esperam FeriasDatabase."""

    def __init__(self, path=":memory:"):
        super().__init__(path)
