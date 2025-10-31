from .mysql_connection import MySQLConnection
from .mysql_users import MySQLUserManager
from .mysql_ferias import MySQLFeriasManager

class MySQLDatabase:
    """Classe principal que unifica todos os managers do MySQL"""
    
    def __init__(self, host, port, database, user, password):
        self.connection = MySQLConnection(host, port, database, user, password)
        self.connection.init_database()
        
        # Inicializar managers
        self.users = MySQLUserManager(self.connection)
        self.ferias = MySQLFeriasManager(self.connection)
    
    # Métodos de usuários
    def authenticate_user(self, email, senha):
        return self.users.authenticate_user(email, senha)
    
    def get_users(self, setor=None):
        return self.users.get_users(setor)
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        return self.users.create_user(nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao)
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        return self.users.update_user(user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias)
    
    def delete_user(self, user_id):
        return self.users.delete_user(user_id)
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Edição manual de saldo"):
        return self.users.update_saldo_ferias(user_id, novo_saldo, usuario_responsavel_id, usuario_responsavel_nome, motivo)
    
    # Métodos de férias
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Aprovada", usuario_nivel="colaborador"):
        return self.ferias.add_ferias(usuario_id, data_inicio, data_fim, status, usuario_nivel)
    
    def get_ferias_usuario(self, usuario_id):
        return self.ferias.get_ferias_usuario(usuario_id)
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        return self.ferias.get_all_ferias(status, data_inicio, data_fim)
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        return self.ferias.update_ferias_status(ferias_id, novo_status, usuario_responsavel_id)
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        return self.ferias.delete_ferias(ferias_id, usuario_responsavel_id)
    
    def verificar_antecedencia(self, data_inicio, usuario_nivel="colaborador"):
        return self.ferias.verificar_antecedencia(data_inicio, usuario_nivel)
    
    def calcular_detalhes_periodo(self, data_inicio, data_fim):
        return self.ferias.calcular_detalhes_periodo(data_inicio, data_fim)
    

    
    def close(self):
        """Fecha conexão MySQL"""
        self.connection.close()