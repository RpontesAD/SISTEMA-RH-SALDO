"""
Database ultra-simples usando apenas psycopg2
"""
import streamlit as st
import bcrypt
from datetime import date
import psycopg2
import psycopg2.extras

class SimplePsycopg2:
    """Database usando apenas psycopg2 - sem pandas, sem SQLAlchemy"""
    
    def __init__(self):
        self.connection = self
        # Debug: verificar se secrets existem
        try:
            pg_config = st.secrets["connections"]["postgresql"]
            st.write(f"✅ Secrets encontrados: host={pg_config['host']}")
        except Exception as e:
            st.error(f"❌ Erro ao acessar secrets: {e}")
            st.stop()
        
        # Construir connection string a partir dos componentes
        # Escapar caracteres especiais na senha
        import urllib.parse
        password_escaped = urllib.parse.quote_plus(pg_config['password'])
        self.conn_str = f"postgresql://{pg_config['username']}:{password_escaped}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        self.init_database()
    
    def _execute_query(self, query, params=None, fetch=False):
        """Executa query simples"""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(query, params)
                    if fetch:
                        return cur.fetchall()
                    conn.commit()
                    return True
        except Exception as e:
            return False if not fetch else []
    
    def init_database(self):
        """Cria tabelas se não existirem"""
        # Criar tabela usuarios
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS usuarios (
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
        """)
        
        # Criar tabela ferias
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS ferias (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                dias_utilizados INTEGER NOT NULL,
                status TEXT DEFAULT 'Pendente',
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar admin se não existir
        self._create_admin_user()
    
    def _create_admin_user(self):
        """Cria admin se não existir"""
        try:
            existing = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE email = %s", ('admin@rpontes.com',), fetch=True)
            
            if existing and existing[0]['count'] == 0:
                senha_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                self._execute_query("""
                    INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, ('Administrador', 'admin@rpontes.com', senha_hash, 'RH', 'RH', 'master', 12, date.today()))
        except:
            pass
    
    def get_connection(self):
        return self
    
    def authenticate_user(self, email, senha):
        """Autentica usuário"""
        try:
            users = self._execute_query("SELECT * FROM usuarios WHERE email = %s", (email,), fetch=True)
            
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
                        'saldo_ferias': user['saldo_ferias']
                    }
            return None
        except Exception as e:
            st.error(f"Erro na autenticação: {e}")
            return None
    
    def get_users(self, setor=None):
        """Obtém usuários - retorna lista de dicts"""
        if setor:
            return self._execute_query("SELECT * FROM usuarios WHERE setor = %s", (setor,), fetch=True)
        return self._execute_query("SELECT * FROM usuarios", fetch=True)
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        """Cria usuário"""
        try:
            # Verificar se email já existe
            existing = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE email = %s", (email,), fetch=True)
            
            if existing and existing[0]['count'] > 0:
                return False
            
            # Criar usuário
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            success = self._execute_query("""
                INSERT INTO usuarios (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias, data_admissao or date.today()))
            
            return success
            
        except Exception as e:
            if "duplicate key" in str(e):
                return False
            st.error(f"Erro create_user: {e}")
            return False
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        return self._execute_query("""
            UPDATE usuarios SET nome=%s, email=%s, setor=%s, funcao=%s, 
            nivel_acesso=%s, saldo_ferias=%s WHERE id=%s
        """, (nome, email, setor, funcao, nivel_acesso, saldo_ferias, user_id))
    
    def delete_user(self, user_id):
        """Exclui usuário"""
        return self._execute_query("DELETE FROM usuarios WHERE id=%s", (user_id,))
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        """Atualiza saldo"""
        return self._execute_query("UPDATE usuarios SET saldo_ferias=%s WHERE id=%s", (novo_saldo, user_id))
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        """Adiciona férias"""
        try:
            dias_utilizados = (data_fim - data_inicio).days + 1
            
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    # Inserir férias
                    cur.execute("""
                        INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (usuario_id, data_inicio, data_fim, dias_utilizados, status))
                    
                    # Atualizar saldo se aprovada
                    if status == "Aprovada":
                        cur.execute("""
                            UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s
                        """, (dias_utilizados, usuario_id))
                    
                    conn.commit()
                    return True
        except:
            return False
    
    def get_ferias_usuario(self, usuario_id):
        """Obtém férias do usuário"""
        return self._execute_query("SELECT * FROM ferias WHERE usuario_id = %s ORDER BY data_inicio DESC", (usuario_id,), fetch=True)
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        """Obtém todas as férias"""
        return self._execute_query("""
            SELECT f.*, u.nome as nome_usuario 
            FROM ferias f 
            JOIN usuarios u ON f.usuario_id = u.id 
            ORDER BY f.data_inicio DESC
        """, fetch=True)
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        """Atualiza status das férias"""
        try:
            # Buscar férias atual
            ferias_list = self._execute_query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = %s", (ferias_id,), fetch=True)
            
            if ferias_list:
                ferias = ferias_list[0]
                usuario_id = ferias['usuario_id']
                dias_utilizados = ferias['dias_utilizados']
                status_atual = ferias['status']
                
                with psycopg2.connect(self.conn_str) as conn:
                    with conn.cursor() as cur:
                        # Atualizar status
                        cur.execute("UPDATE ferias SET status = %s WHERE id = %s", (novo_status, ferias_id))
                        
                        # Ajustar saldo
                        if status_atual != "Aprovada" and novo_status == "Aprovada":
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_utilizados, usuario_id))
                        elif status_atual == "Aprovada" and novo_status != "Aprovada":
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
                        
                        conn.commit()
                        return True
            return False
        except:
            return False
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        """Exclui férias"""
        try:
            # Buscar férias antes de excluir
            ferias_list = self._execute_query("SELECT usuario_id, dias_utilizados, status FROM ferias WHERE id = %s", (ferias_id,), fetch=True)
            
            if ferias_list:
                ferias = ferias_list[0]
                usuario_id = ferias['usuario_id']
                dias_utilizados = ferias['dias_utilizados']
                status = ferias['status']
                
                with psycopg2.connect(self.conn_str) as conn:
                    with conn.cursor() as cur:
                        # Excluir férias
                        cur.execute("DELETE FROM ferias WHERE id = %s", (ferias_id,))
                        
                        # Se estava aprovada, devolver ao saldo
                        if status == "Aprovada":
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
                        
                        conn.commit()
                        return True
            return False
        except:
            return False
    
    def close(self):
        pass