"""
Gerenciador principal do banco de dados
"""
import bcrypt
from datetime import date
from .base_connection import BaseConnection
from .users_repository import UsersRepository
from .ferias_repository import FeriasRepository
from .avisos_repository import AvisosRepository
from .renovacao_repository import RenovacaoRepository

class DatabaseManager(BaseConnection):
    """Classe principal que combina todos os repositórios"""
    
    def __init__(self):
        super().__init__()
        self.connection = self
        
        # Inicializar repositórios
        self.users = UsersRepository()
        self.ferias = FeriasRepository()
        self.avisos = AvisosRepository()
        self.renovacao = RenovacaoRepository()
        
        # Inicializar banco
        self.init_database()
    
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
                ativo BOOLEAN DEFAULT true,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_admissao DATE
            )
        """)
        
        # Adicionar coluna ativo se não existir
        self._execute_query("""
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT true
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
        
        # Criar tabela avisos
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS avisos (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                autor_id INTEGER REFERENCES usuarios(id),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT true
            )
        """)
        
        # Criar tabela avisos_destinatarios
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS avisos_destinatarios (
                id SERIAL PRIMARY KEY,
                aviso_id INTEGER REFERENCES avisos(id) ON DELETE CASCADE,
                usuario_id INTEGER REFERENCES usuarios(id),
                lido BOOLEAN DEFAULT false,
                data_leitura TIMESTAMP,
                oculto BOOLEAN DEFAULT false
            )
        """)
        
        # Criar tabela renovacao_saldo
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS renovacao_saldo (
                id SERIAL PRIMARY KEY,
                ano INTEGER UNIQUE NOT NULL,
                saldo_padrao INTEGER NOT NULL,
                data_aplicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_responsavel_id INTEGER REFERENCES usuarios(id)
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
                """, ('Administrador', 'admin@rpontes.com', senha_hash, 'GESTÃO DE PESSOAS', 'Gerente', 'master', 12, date.today()))
        except:
            pass
    
    def get_connection(self):
        return self
    
    # Métodos delegados para compatibilidade
    def authenticate_user(self, email, senha):
        return self.users.authenticate_user(email, senha)
    
    def get_users(self, setor=None, incluir_inativos=False):
        return self.users.get_users(setor, incluir_inativos)
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        return self.users.create_user(nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao)
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        return self.users.update_user(user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias)
    
    def inativar_usuario(self, user_id):
        return self.users.inativar_usuario(user_id)
    
    def ativar_usuario(self, user_id):
        return self.users.ativar_usuario(user_id)
    
    def delete_user(self, user_id):
        return self.users.delete_user(user_id)
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        return self.users.update_saldo_ferias(user_id, novo_saldo, usuario_responsavel_id, usuario_responsavel_nome, motivo)
    
    def update_password(self, user_id, nova_senha):
        return self.users.update_password(user_id, nova_senha)
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        return self.ferias.add_ferias(usuario_id, data_inicio, data_fim, status, usuario_nivel)
    
    def get_ferias_usuario(self, usuario_id):
        return self.ferias.get_ferias_usuario(usuario_id)
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        return self.ferias.get_all_ferias(status, data_inicio, data_fim)
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        return self.ferias.update_ferias_status(ferias_id, novo_status, usuario_responsavel_id)
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        return self.ferias.delete_ferias(ferias_id, usuario_responsavel_id)
    
    def criar_aviso(self, titulo, conteudo, autor_id, destinatarios_ids):
        return self.avisos.criar_aviso(titulo, conteudo, autor_id, destinatarios_ids)
    
    def get_avisos_usuario(self, usuario_id):
        return self.avisos.get_avisos_usuario(usuario_id)
    
    def marcar_aviso_lido(self, aviso_id, usuario_id):
        return self.avisos.marcar_aviso_lido(aviso_id, usuario_id)
    
    def get_avisos_admin(self):
        return self.avisos.get_avisos_admin()
    
    def get_status_leitura_aviso(self, aviso_id):
        return self.avisos.get_status_leitura_aviso(aviso_id)
    
    def get_aviso_detalhes(self, aviso_id):
        return self.avisos.get_aviso_detalhes(aviso_id)
    
    def atualizar_aviso(self, aviso_id, titulo, conteudo):
        return self.avisos.atualizar_aviso(aviso_id, titulo, conteudo)
    
    def excluir_aviso(self, aviso_id):
        return self.avisos.excluir_aviso(aviso_id)
    
    def get_matriz_leitura_avisos(self):
        return self.avisos.get_matriz_leitura_avisos()
    
    def remover_aviso_usuario(self, aviso_id, usuario_id):
        return self.avisos.remover_aviso_usuario(aviso_id, usuario_id)
    
    def verificar_renovacao_ano(self, ano):
        return self.renovacao.verificar_renovacao_ano(ano)
    
    def renovar_saldo_anual_simples(self, ano, saldo_adicional, usuario_responsavel_id):
        return self.renovacao.renovar_saldo_anual_simples(ano, saldo_adicional, usuario_responsavel_id)
    
    def renovar_saldo_anual(self, ano, saldo_adicional, usuario_responsavel_id, modo_teste=False):
        return self.renovacao.renovar_saldo_anual(ano, saldo_adicional, usuario_responsavel_id, modo_teste)
    
    def get_historico_renovacoes(self):
        return self.renovacao.get_historico_renovacoes()
    
    def desfazer_ultima_renovacao(self, usuario_responsavel_id):
        return self.renovacao.desfazer_ultima_renovacao(usuario_responsavel_id)
    
    def close(self):
        pass