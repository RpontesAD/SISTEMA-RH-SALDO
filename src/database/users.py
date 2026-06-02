"""Compatibilidade com a antiga API de usuários usada em testes."""
from .sqlite_database import SQLiteDatabase


class UsersDatabase(SQLiteDatabase):
    """Wrapper compatível com os testes antigos que esperam UsersDatabase."""

    def __init__(self, path=":memory:"):
        super().__init__(path)

    def get_all_users(self):
        users = self.get_users()
        if hasattr(users, 'to_dict'):
            return users.to_dict(orient='records')
        return users
