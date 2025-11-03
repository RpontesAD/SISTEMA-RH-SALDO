"""
SQLite Database - Interface compatível com MySQL
"""
import sqlite3
import pandas as pd
import bcrypt
from datetime import date, datetime
import os

class SQLiteDatabase:
    """Classe SQLite compatível com MySQLDatabase"""
    
    def __init__(self, db_path="data/rpontes_rh.db"):
        self.db_path = db_path
        self.connection = self
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicializar banco
        self.init_database()
    
    def get_connection(self):
        """Retorna conexão SQLite"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Cria tabelas se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                setor TEXT NOT NULL,
                funcao TEXT NOT NULL,
                nivel_acesso TEXT DEFAULT 'colaborador',
                saldo_ferias INTEGER DEFAULT 12,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_admissao DATE
            )
        """)
        
        # Tabela ferias
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
        
        conn.commit()
        
        # Criar usuário admin se não existir
        self._create_admin_user(cursor, conn)
        conn.close()
    
    def _create_admin_user(self, cursor, conn):
        """Cria usuário admin padrão"""
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", ("admin@rpontes.com",))
        if cursor.fetchone()[0] == 0:
            senha_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, data_admissao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("Administrador", "admin@rpontes.com", senha_hash, "RH", "RH", "master", date.today()))
            conn.commit()
    
    # Métodos de usuários
    def authenticate_user(self, email, senha):
        """Autentica usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            try:
                # Tentar verificar hash bcrypt
                if bcrypt.checkpw(senha.encode('utf-8'), user[3].encode('utf-8')):
                    return {
                        'id': user[0], 'nome': user[1], 'email': user[2], 
                        'setor': user[4], 'funcao': user[5], 'nivel_acesso': user[6],
                        'saldo_ferias': user[7]
                    }
            except:
                pass
        return None
    
    def get_users(self, setor=None):
        """Obtém usuários"""
        conn = self.get_connection()
        
        if setor:
            df = pd.read_sql_query("SELECT * FROM usuarios WHERE setor = ?", conn, params=(setor,))
        else:
            df = pd.read_sql_query("SELECT * FROM usuarios", conn)
        
        conn.close()
        return df
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        """Cria usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao or date.today()))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usuarios SET nome=?, email=?, setor=?, funcao=?, nivel_acesso=?, saldo_ferias=?
                WHERE id=?
            """, (nome, email, setor, funcao, nivel_acesso, saldo_ferias, user_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_user(self, user_id):
        """Exclui usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        """Atualiza saldo de férias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET saldo_ferias=? WHERE id=?", (novo_saldo, user_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    # Métodos de férias
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        """Adiciona férias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            dias_utilizados = (data_fim - data_inicio).days + 1
            
            cursor.execute("""
                INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, data_inicio, data_fim, dias_utilizados, status))
            
            # Se aprovada, descontar do saldo
            if status == "Aprovada":
                cursor.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - ? WHERE id = ?", (dias_utilizados, usuario_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_ferias_usuario(self, usuario_id):
        """Obtém férias do usuário"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM ferias WHERE usuario_id = ? ORDER BY data_inicio DESC", conn, params=(usuario_id,))
        conn.close()
        return df
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        """Obtém todas as férias"""
        conn = self.get_connection()
        
        query = """
            SELECT f.*, u.nome as nome_usuario 
            FROM ferias f 
            JOIN usuarios u ON f.usuario_id = u.id 
            ORDER BY f.data_inicio DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        """Atualiza status das férias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar férias atual
            cursor.execute("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = ?", (ferias_id,))
            ferias = cursor.fetchone()
            
            if ferias:
                usuario_id, dias_utilizados, status_atual = ferias
                
                # Atualizar status
                cursor.execute("UPDATE ferias SET status = ? WHERE id = ?", (novo_status, ferias_id))
                
                # Ajustar saldo conforme mudança de status
                if status_atual != "Aprovada" and novo_status == "Aprovada":
                    # Aprovar: descontar do saldo
                    cursor.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - ? WHERE id = ?", (dias_utilizados, usuario_id))
                elif status_atual == "Aprovada" and novo_status != "Aprovada":
                    # Cancelar aprovação: devolver ao saldo
                    cursor.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + ? WHERE id = ?", (dias_utilizados, usuario_id))
                
                conn.commit()
            
            conn.close()
            return True
        except:
            return False
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        """Exclui férias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar férias para ajustar saldo se necessário
            cursor.execute("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = ?", (ferias_id,))
            ferias = cursor.fetchone()
            
            if ferias:
                usuario_id, dias_utilizados, status = ferias
                
                # Se estava aprovada, devolver ao saldo
                if status == "Aprovada":
                    cursor.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + ? WHERE id = ?", (dias_utilizados, usuario_id))
                
                # Excluir férias
                cursor.execute("DELETE FROM ferias WHERE id = ?", (ferias_id,))
                conn.commit()
            
            conn.close()
            return True
        except:
            return False
    
    def close(self):
        """Fecha conexão (compatibilidade)"""
        pass