"""
Database simples usando st.connection
"""
import streamlit as st
import pandas as pd
import bcrypt
from datetime import date, datetime
from sqlalchemy import text

class SimpleDatabase:
    """Database usando st.connection - SUPER FÁCIL"""
    
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
                self.conn.query(text("""
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
                """), ttl=0)
            
            # Verificar se tabela ferias existe
            try:
                self.conn.query("SELECT 1 FROM ferias LIMIT 1")
            except:
                # Criar tabela ferias
                self.conn.query(text("""
                    CREATE TABLE ferias (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER REFERENCES usuarios(id),
                        data_inicio DATE NOT NULL,
                        data_fim DATE NOT NULL,
                        dias_utilizados INTEGER NOT NULL,
                        status TEXT DEFAULT 'Pendente',
                        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """), ttl=0)
            
            # Criar admin se não existir
            self._create_admin_user()
        except Exception as e:
            st.error(f"Erro ao inicializar banco: {e}")
    
    def _create_admin_user(self):
        """Cria admin se não existir"""
        try:
            # Verificar se admin existe sem usar query extra
            # Tentar fazer login direto - se funcionar, admin existe
            test_user = self.authenticate_user("admin@rpontes.com", "admin123")
            
            if not test_user:
                # Admin não existe ou senha incorreta, criar/atualizar
                existing = self.conn.query("SELECT COUNT(*) as count FROM usuarios WHERE email = 'admin@rpontes.com'")
                
                if existing.iloc[0]['count'] == 0:
                    # Criar novo admin
                    self.create_user(
                        nome="Administrador",
                        email="admin@rpontes.com",
                        senha="admin123",
                        setor="RH",
                        funcao="RH",
                        nivel_acesso="master",
                        data_admissao=date.today()
                    )
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
        """Cria usuário"""
        try:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Usar query direta sem session
            self.conn.query(
                "INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) VALUES (:nome, :email, :senha_hash, :setor, :funcao, :nivel_acesso, :saldo_ferias, :data_admissao)",
                params={
                    "nome": nome, "email": email, "senha_hash": senha_hash, "setor": setor,
                    "funcao": funcao, "nivel_acesso": nivel_acesso, "saldo_ferias": saldo_ferias,
                    "data_admissao": data_admissao or date.today()
                },
                ttl=0
            )
            return True
        except Exception as e:
            # Se for erro de duplicata, ignorar
            if "duplicate key" in str(e):
                return True
            st.error(f"Erro create_user: {e}")
            return False
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        try:
            self.conn.query(
                "UPDATE usuarios SET nome=:nome, email=:email, setor=:setor, funcao=:funcao, nivel_acesso=:nivel_acesso, saldo_ferias=:saldo_ferias WHERE id=:user_id",
                params={
                    "nome": nome, "email": email, "setor": setor, "funcao": funcao,
                    "nivel_acesso": nivel_acesso, "saldo_ferias": saldo_ferias, "user_id": user_id
                },
                ttl=0
            )
            return True
        except:
            return False
    
    def delete_user(self, user_id):
        """Exclui usuário"""
        try:
            self.conn.query("DELETE FROM usuarios WHERE id=:user_id", params={"user_id": user_id}, ttl=0)
            return True
        except:
            return False
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        """Atualiza saldo"""
        try:
            self.conn.query("UPDATE usuarios SET saldo_ferias=:saldo WHERE id=:user_id", params={"saldo": novo_saldo, "user_id": user_id}, ttl=0)
            return True
        except:
            return False
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        """Adiciona férias"""
        try:
            dias_utilizados = (data_fim - data_inicio).days + 1
            self.conn.query(
                "INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status) VALUES (:usuario_id, :data_inicio, :data_fim, :dias_utilizados, :status)",
                params={
                    "usuario_id": usuario_id, "data_inicio": data_inicio, "data_fim": data_fim,
                    "dias_utilizados": dias_utilizados, "status": status
                },
                ttl=0
            )
            
            if status == "Aprovada":
                self.conn.query(
                    "UPDATE usuarios SET saldo_ferias = saldo_ferias - :dias WHERE id = :user_id",
                    params={"dias": dias_utilizados, "user_id": usuario_id},
                    ttl=0
                )
            
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
                
                # Atualizar status
                self.conn.query(
                    "UPDATE ferias SET status = :status WHERE id = :ferias_id",
                    params={"status": novo_status, "ferias_id": ferias_id},
                    ttl=0
                )
                
                # Ajustar saldo baseado na mudança de status
                if status_atual != "Aprovada" and novo_status == "Aprovada":
                    # Descontar do saldo
                    self.conn.query(
                        "UPDATE usuarios SET saldo_ferias = saldo_ferias - :dias WHERE id = :user_id",
                        params={"dias": dias_utilizados, "user_id": usuario_id},
                        ttl=0
                    )
                elif status_atual == "Aprovada" and novo_status != "Aprovada":
                    # Devolver ao saldo
                    self.conn.query(
                        "UPDATE usuarios SET saldo_ferias = saldo_ferias + :dias WHERE id = :user_id",
                        params={"dias": dias_utilizados, "user_id": usuario_id},
                        ttl=0
                    )
                
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
                
                # Excluir férias
                self.conn.query("DELETE FROM ferias WHERE id = :ferias_id", params={"ferias_id": ferias_id}, ttl=0)
                
                # Se estava aprovada, devolver ao saldo
                if status == "Aprovada":
                    self.conn.query(
                        "UPDATE usuarios SET saldo_ferias = saldo_ferias + :dias WHERE id = :user_id",
                        params={"dias": dias_utilizados, "user_id": usuario_id},
                        ttl=0
                    )
                
                return True
            return False
        except:
            return False
    
    def close(self):
        pass