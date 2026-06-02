"""Banco SQLite de compatibilidade para testes e uso local."""
import os
import sqlite3
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import pandas as pd

from utils.constants import DIAS_FERIAS_PADRAO
from utils.calculos import calcular_dias_uteis

_SQLITE_CONNECTIONS = {}


def _get_sqlite_connection(path: str):
    global _SQLITE_CONNECTIONS

    if path in (":memory", ":memory:"):
        conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    if path in _SQLITE_CONNECTIONS:
        conn = _SQLITE_CONNECTIONS[path]
        try:
            conn.execute("SELECT 1")
            return conn
        except sqlite3.ProgrammingError:
            # Recreate closed connections
            del _SQLITE_CONNECTIONS[path]

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _SQLITE_CONNECTIONS[path] = conn
    return conn


class SQLiteDatabase:
    """Compatibilidade com um banco SQLite simplificado."""

    def __init__(self, path: str = ":memory:"):
        self.path = path
        self.conn = _get_sqlite_connection(path)
        self.init_database()

    def init_database(self):
        """Inicializa as tabelas principais do banco."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                senha TEXT,
                setor TEXT NOT NULL,
                funcao TEXT NOT NULL,
                nivel_acesso TEXT DEFAULT 'colaborador',
                saldo_ferias INTEGER DEFAULT 12,
                ativo INTEGER DEFAULT 1,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_admissao DATE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                dias_utilizados INTEGER NOT NULL,
                status TEXT DEFAULT 'Pendente',
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avisos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                autor_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY (autor_id) REFERENCES usuarios (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avisos_destinatarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aviso_id INTEGER,
                usuario_id INTEGER,
                lido INTEGER DEFAULT 0,
                data_leitura TIMESTAMP,
                oculto INTEGER DEFAULT 0,
                FOREIGN KEY (aviso_id) REFERENCES avisos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS renovacao_saldo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ano INTEGER UNIQUE NOT NULL,
                saldo_padrao INTEGER NOT NULL,
                data_aplicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_responsavel_id INTEGER,
                FOREIGN KEY (usuario_responsavel_id) REFERENCES usuarios (id)
            )
        """)

        self.conn.commit()
        self._create_admin_user()
        return True

    def _translate_query(self, query: str) -> str:
        return query.replace("%s", "?")

    def _execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None, fetch: bool = False):
        try:
            sql = self._translate_query(query)
            cursor = self.conn.cursor()
            cursor.execute(sql, params or ())
            if fetch:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            self.conn.commit()
            return True
        except Exception:
            if fetch:
                return []
            return False

    def _create_admin_user(self):
        existing = self._execute_query(
            "SELECT COUNT(*) as count FROM usuarios WHERE email = %s",
            ('admin@rpontes.com',),
            fetch=True
        )

        if existing and existing[0].get('count', 0) == 0:
            senha_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self._execute_query(
                "INSERT INTO usuarios (nome, email, senha_hash, senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                ('Administrador', 'admin@rpontes.com', senha_hash, senha_hash, 'GESTÃO DE PESSOAS', 'Gerente', 'master', DIAS_FERIAS_PADRAO, date.today())
            )

    def get_connection(self):
        return self.conn

    def authenticate_user(self, email: str, senha: str):
        users = self._execute_query(
            "SELECT * FROM usuarios WHERE email = %s AND ativo = 1",
            (email,),
            fetch=True
        )
        if users:
            user = users[0]
            if bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
                return {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'setor': user['setor'],
                    'funcao': user['funcao'],
                    'nivel_acesso': user['nivel_acesso'],
                    'saldo_ferias': user['saldo_ferias'],
                    'ativo': bool(user.get('ativo', 1))
                }
        return None

    def get_users(self, setor: Optional[str] = None, incluir_inativos: bool = False):
        if incluir_inativos:
            if setor:
                users = self._execute_query("SELECT * FROM usuarios WHERE setor = %s ORDER BY nome", (setor,), fetch=True)
            else:
                users = self._execute_query("SELECT * FROM usuarios ORDER BY nome", fetch=True)
        else:
            if setor:
                users = self._execute_query("SELECT * FROM usuarios WHERE setor = %s AND ativo = 1 ORDER BY nome", (setor,), fetch=True)
            else:
                users = self._execute_query("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY nome", fetch=True)

        return pd.DataFrame(users)

    def get_all_users(self):
        users = self.get_users()
        if hasattr(users, 'to_dict'):
            return users.to_dict(orient='records')
        return users

    def create_user(self, nome: str, email: str, senha: str, setor: str, funcao: str, nivel_acesso: str = "colaborador", saldo_ferias: int = DIAS_FERIAS_PADRAO, data_admissao: Optional[date] = None):
        existing = self._execute_query(
            "SELECT COUNT(*) as count FROM usuarios WHERE email = %s",
            (email,),
            fetch=True
        )

        if existing and existing[0].get('count', 0) > 0:
            return False

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return self._execute_query(
            "INSERT INTO usuarios (nome, email, senha_hash, senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nome, email, senha_hash, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao or date.today())
        )

    def update_user(self, user_id: int, nome: str, email: str, setor: str, funcao: str, nivel_acesso: str, saldo_ferias: int, data_admissao: Optional[date] = None):
        return self._execute_query(
            "UPDATE usuarios SET nome=%s, email=%s, setor=%s, funcao=%s, nivel_acesso=%s, saldo_ferias=%s, data_admissao=%s WHERE id=%s",
            (nome, email, setor, funcao, nivel_acesso, saldo_ferias, data_admissao, user_id)
        )

    def inativar_usuario(self, user_id: int):
        return self._execute_query("UPDATE usuarios SET ativo = 0 WHERE id = %s", (user_id,))

    def ativar_usuario(self, user_id: int):
        return self._execute_query("UPDATE usuarios SET ativo = 1 WHERE id = %s", (user_id,))

    def delete_user(self, user_id: int):
        return self._execute_query("DELETE FROM usuarios WHERE id = %s", (user_id,))

    def update_saldo_ferias(self, user_id: int, novo_saldo: int, usuario_responsavel_id: Optional[int] = None, usuario_responsavel_nome: Optional[str] = None, motivo: str = "Ajuste manual"):
        return self._execute_query("UPDATE usuarios SET saldo_ferias=%s WHERE id=%s", (novo_saldo, user_id))

    def update_password(self, user_id: int, nova_senha: str):
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return self._execute_query("UPDATE usuarios SET senha_hash=%s WHERE id=%s", (senha_hash, user_id))

    def add_ferias(self, usuario_id: int, data_inicio: date, data_fim: date, status: str = "Pendente", usuario_nivel: str = "colaborador"):
        dias_utilizados = calcular_dias_uteis(data_inicio, data_fim)
        success = self._execute_query(
            "INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status) VALUES (%s, %s, %s, %s, %s)",
            (usuario_id, data_inicio, data_fim, dias_utilizados, status)
        )

        if not success:
            return False

        if status.lower() in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_utilizados, usuario_id))
        return True

    def get_ferias_usuario(self, usuario_id: int):
        ferias = self._execute_query("SELECT * FROM ferias WHERE usuario_id = %s ORDER BY data_inicio DESC", (usuario_id,), fetch=True)
        return pd.DataFrame(ferias)

    def get_all_ferias(self, status: Optional[str] = None, data_inicio: Optional[date] = None, data_fim: Optional[date] = None):
        return pd.DataFrame(self._execute_query(
            "SELECT f.*, u.nome as nome_usuario FROM ferias f JOIN usuarios u ON f.usuario_id = u.id ORDER BY f.data_inicio DESC",
            fetch=True
        ))

    def update_ferias(self, ferias_id: int, data_inicio: date, data_fim: date, status: str = "Pendente"):
        ferias_list = self._execute_query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = %s", (ferias_id,), fetch=True)
        if not ferias_list:
            return False

        ferias = ferias_list[0]
        usuario_id = ferias['usuario_id']
        dias_antigos = ferias['dias_utilizados']
        status_antigo = ferias['status']
        dias_novos = calcular_dias_uteis(data_inicio, data_fim)

        success = self._execute_query(
            "UPDATE ferias SET data_inicio=%s, data_fim=%s, dias_utilizados=%s, status=%s WHERE id=%s",
            (data_inicio, data_fim, dias_novos, status, ferias_id)
        )

        if not success:
            return False

        status_antigo_lower = status_antigo.lower() if status_antigo else ""
        status_novo_lower = status.lower() if status else ""

        if status_antigo_lower in ["aprovado", "aprovada"] and status_novo_lower not in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_antigos, usuario_id))
        elif status_antigo_lower not in ["aprovado", "aprovada"] and status_novo_lower in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_novos, usuario_id))
        return True

    def update_ferias_status(self, ferias_id: int, novo_status: str, usuario_responsavel_id: Optional[int] = None):
        ferias_list = self._execute_query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = %s", (ferias_id,), fetch=True)
        if not ferias_list:
            return False

        ferias = ferias_list[0]
        usuario_id = ferias['usuario_id']
        dias_utilizados = ferias['dias_utilizados']
        status_atual = ferias['status']

        success = self._execute_query("UPDATE ferias SET status = %s WHERE id = %s", (novo_status, ferias_id))
        if not success:
            return False

        status_atual_lower = status_atual.lower() if status_atual else ""
        novo_status_lower = novo_status.lower() if novo_status else ""

        if status_atual_lower not in ["aprovado", "aprovada"] and novo_status_lower in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_utilizados, usuario_id))
        elif status_atual_lower in ["aprovado", "aprovada"] and novo_status_lower not in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
        return True

    def delete_ferias(self, ferias_id: int, usuario_responsavel_id: Optional[int] = None):
        ferias_list = self._execute_query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = %s", (ferias_id,), fetch=True)
        if not ferias_list:
            return False

        ferias = ferias_list[0]
        usuario_id = ferias['usuario_id']
        dias_utilizados = ferias['dias_utilizados']
        status = ferias['status']

        success = self._execute_query("DELETE FROM ferias WHERE id = %s", (ferias_id,))
        if not success:
            return False

        if status.lower() in ["aprovado", "aprovada"]:
            self._execute_query("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
        return True

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
