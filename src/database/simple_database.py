"""
Database final - Usando engine direto para writes
"""
import streamlit as st
import pandas as pd
import bcrypt
from datetime import date, datetime
from sqlalchemy import text

class SimpleDatabase:
    """Database usando engine direto para writes"""
    
    def __init__(self):
        self.connection = self
        self.conn = st.connection("postgresql", type="sql")
        self.init_database()
    
    def init_database(self):
        """Cria tabelas se não existirem"""
        try:
            # Verificar se tabela usuarios existe
            try:
                self.conn.query("SELECT 1 FROM usuarios LIMIT 1")
            except:
                # Criar tabela usuarios
                engine = self.conn._instance
                with engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE usuarios (
                            id SERIAL PRIMARY KEY,
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
                    """))
                    conn.commit()
            
            # Verificar se tabela ferias existe
            try:
                self.conn.query("SELECT 1 FROM ferias LIMIT 1")
            except:
                # Criar tabela ferias
                engine = self.conn._instance
                with engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE ferias (
                            id SERIAL PRIMARY KEY,
                            usuario_id INTEGER REFERENCES usuarios(id),
                            data_inicio DATE NOT NULL,
                            data_fim DATE NOT NULL,
                            dias_utilizados INTEGER NOT NULL,
                            status TEXT DEFAULT 'Pendente',
                            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()
            
            # Criar admin se não existir
            self._create_admin_user()
        except Exception as e:
            st.error(f"Erro ao inicializar banco: {e}")
    
    def _create_admin_user(self):
        """Cria admin se não existir"""
        try:
            existing = self.conn.query("SELECT COUNT(*) as count FROM usuarios WHERE email = 'admin@rpontes.com'")
            
            if existing.iloc[0]['count'] == 0:
                # Criar admin
                senha_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                engine = self.conn._instance
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) 
                        VALUES (:nome, :email, :senha_hash, :setor, :funcao, :nivel_acesso, :saldo_ferias, :data_admissao)
                    """), {
                        "nome": "Administrador", "email": "admin@rpontes.com", "senha_hash": senha_hash,
                        "setor": "RH", "funcao": "RH", "nivel_acesso": "master",
                        "saldo_ferias": 12, "data_admissao": date.today()
                    })
                    conn.commit()
                
        except Exception as e:
            # Ignorar erros na inicialização
            pass
    
    def get_connection(self):
        return self
    
    def authenticate_user(self, email, senha):
        """Autentica usuário"""
        try:
            user_df = self.conn.query("SELECT * FROM usuarios WHERE email = :email", params={"email": email})
            
            if not user_df.empty:
                user = user_df.iloc[0]
                if bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
                    return {
                        'id': user['id'],
                        'nome': user['nome'],
                        'email': user['email'],
                        'setor': user['setor'],
                        'funcao': user['funcao'],
                        'nivel_acesso': user['nivel_acesso'],
                        'saldo_ferias': user['saldo_ferias']
                    }
            return None
        except Exception as e:
            st.error(f"Erro na autenticação: {e}")
            return None
    
    def get_users(self, setor=None):
        """Obtém usuários"""
        if setor:
            return self.conn.query("SELECT * FROM usuarios WHERE setor = :setor", params={"setor": setor})
        return self.conn.query("SELECT * FROM usuarios")
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        """Cria usuário usando psycopg2 direto"""
        try:
            # Verificar se email já existe
            existing = self.conn.query("SELECT COUNT(*) as count FROM usuarios WHERE email = :email", params={"email": email})
            if existing.iloc[0]['count'] > 0:
                return False  # Email já existe
            
            # Criar usuário usando psycopg2 direto
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Usar raw connection do psycopg2
            import psycopg2
            conn_str = st.secrets["connections"]["postgresql"]["url"]
            
            with psycopg2.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao or date.today()
                    ))
                    conn.commit()
            return True
            
        except Exception as e:
            if "duplicate key" in str(e) or "UNIQUE constraint" in str(e):
                return False
            st.error(f"Erro create_user: {e}")
            return False
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        try:
            engine = self.conn._instance
            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE usuarios SET nome=:nome, email=:email, setor=:setor, funcao=:funcao, 
                    nivel_acesso=:nivel_acesso, saldo_ferias=:saldo_ferias WHERE id=:user_id
                """), {
                    "nome": nome, "email": email, "setor": setor, "funcao": funcao,
                    "nivel_acesso": nivel_acesso, "saldo_ferias": saldo_ferias, "user_id": user_id
                })
                conn.commit()
            return True
        except:
            return False
    
    def delete_user(self, user_id):
        """Exclui usuário"""
        try:
            engine = self.conn._instance
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM usuarios WHERE id=:user_id"), {"user_id": user_id})
                conn.commit()
            return True
        except:
            return False
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        """Atualiza saldo"""
        try:
            engine = self.conn._instance
            with engine.connect() as conn:
                conn.execute(text("UPDATE usuarios SET saldo_ferias=:saldo WHERE id=:user_id"), {"saldo": novo_saldo, "user_id": user_id})
                conn.commit()
            return True
        except:
            return False
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        """Adiciona férias"""
        try:
            dias_utilizados = (data_fim - data_inicio).days + 1
            
            engine = self.conn._instance
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status) 
                    VALUES (:usuario_id, :data_inicio, :data_fim, :dias_utilizados, :status)
                """), {
                    "usuario_id": usuario_id, "data_inicio": data_inicio, "data_fim": data_fim,
                    "dias_utilizados": dias_utilizados, "status": status
                })
                
                if status == "Aprovada":
                    conn.execute(text("""
                        UPDATE usuarios SET saldo_ferias = saldo_ferias - :dias WHERE id = :user_id
                    """), {"dias": dias_utilizados, "user_id": usuario_id})
                
                conn.commit()
            return True
        except:
            return False
    
    def get_ferias_usuario(self, usuario_id):
        """Obtém férias do usuário"""
        return self.conn.query("SELECT * FROM ferias WHERE usuario_id = :usuario_id ORDER BY data_inicio DESC", params={"usuario_id": usuario_id})
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        """Obtém todas as férias"""
        return self.conn.query("""
            SELECT f.*, u.nome as nome_usuario 
            FROM ferias f 
            JOIN usuarios u ON f.usuario_id = u.id 
            ORDER BY f.data_inicio DESC
        """)
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        """Atualiza status das férias"""
        try:
            # Buscar férias atual
            ferias_df = self.conn.query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = :ferias_id", params={"ferias_id": ferias_id})
            
            if not ferias_df.empty:
                ferias = ferias_df.iloc[0]
                usuario_id = ferias['usuario_id']
                dias_utilizados = ferias['dias_utilizados']
                status_atual = ferias['status']
                
                engine = self.conn._instance
                with engine.connect() as conn:
                    # Atualizar status
                    conn.execute(text("UPDATE ferias SET status = :status WHERE id = :ferias_id"), 
                               {"status": novo_status, "ferias_id": ferias_id})
                    
                    # Ajustar saldo
                    if status_atual != "Aprovada" and novo_status == "Aprovada":
                        conn.execute(text("UPDATE usuarios SET saldo_ferias = saldo_ferias - :dias WHERE id = :user_id"),
                                   {"dias": dias_utilizados, "user_id": usuario_id})
                    elif status_atual == "Aprovada" and novo_status != "Aprovada":
                        conn.execute(text("UPDATE usuarios SET saldo_ferias = saldo_ferias + :dias WHERE id = :user_id"),
                                   {"dias": dias_utilizados, "user_id": usuario_id})
                    
                    conn.commit()
                return True
            return False
        except:
            return False
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        """Exclui férias"""
        try:
            # Buscar férias antes de excluir
            ferias_df = self.conn.query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = :ferias_id", 
                                       params={"ferias_id": ferias_id})
            
            if not ferias_df.empty:
                ferias = ferias_df.iloc[0]
                usuario_id = ferias['usuario_id']
                dias_utilizados = ferias['dias_utilizados']
                status = ferias['status']
                
                engine = self.conn._instance
                with engine.connect() as conn:
                    # Excluir férias
                    conn.execute(text("DELETE FROM ferias WHERE id = :ferias_id"), {"ferias_id": ferias_id})
                    
                    # Se estava aprovada, devolver ao saldo
                    if status == "Aprovada":
                        conn.execute(text("UPDATE usuarios SET saldo_ferias = saldo_ferias + :dias WHERE id = :user_id"),
                                   {"dias": dias_utilizados, "user_id": usuario_id})
                    
                    conn.commit()
                return True
            return False
        except:
            return False
    
    def close(self):
        pass