# Imports apenas dos módulos que existem
try:
    from .mysql_connection import MySQLConnection
    from .mysql_users import MySQLUserManager
    from .mysql_ferias import MySQLFeriasManager
    from .mysql_database import MySQLDatabase
except ImportError as e:
    print(f"Aviso: Alguns módulos MySQL não encontrados: {e}")

class Database:
    def __init__(self, db_name="data/rpontes_rh.db"):
        self.connection = DatabaseConnection(db_name)
        self.users = UserManager(self.connection)
        self.ferias = FeriasManager(self.connection)
        self.ferias_manager = self.ferias  # Alias para compatibilidade
        self.backup = BackupManager(self.connection)
        self.renovacao = RenovacaoManager(self.connection)
        self.auditoria = AuditoriaManager(self.connection)
        self.alertas = AlertasManager(self.connection)
        
        # Inicializar sistema
        self.connection.init_database()
        self.users.fix_invalid_balances()
        self.renovacao.verificar_renovacoes_pendentes()
        self.backup.setup_backup()
    
    # Métodos de conveniência para manter compatibilidade
    def get_connection(self):
        return self.connection.get_connection()
    
    def authenticate_user(self, email, senha):
        return self.users.authenticate_user(email, senha)
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        return self.users.create_user(nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias, data_admissao)
    
    def obter_alertas_renovacao(self):
        return self.renovacao.obter_alertas_renovacao()
    
    def verificar_renovacoes_pendentes(self):
        return self.renovacao.verificar_renovacoes_pendentes()
    
    def verificar_antecedencia_ferias(self, data_inicio, usuario_nivel="colaborador"):
        return self.ferias.verificar_antecedencia(data_inicio, usuario_nivel)
    
    def calcular_detalhes_periodo_ferias(self, data_inicio, data_fim):
        return self.ferias.calcular_detalhes_periodo(data_inicio, data_fim)
    
    def get_users(self, setor=None):
        return self.users.get_users(setor)
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        return self.users.update_user(user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias)
    
    def delete_user(self, user_id):
        return self.users.delete_user(user_id)
    
    def update_saldo_ferias(self, user_id, novo_saldo):
        return self.users.update_saldo_ferias(user_id, novo_saldo)
    
    def obter_logs_auditoria(self, **kwargs):
        return self.auditoria.obter_logs_auditoria(**kwargs)
    
    def obter_historico_usuario(self, usuario_id):
        return self.auditoria.obter_historico_usuario(usuario_id)
    
    def obter_estatisticas_auditoria(self):
        return self.auditoria.obter_estatisticas_auditoria()
    
    def obter_todos_alertas(self):
        try:
            if not hasattr(self, 'alertas') or self.alertas is None:
                print("Alertas manager não inicializado, criando...")
                self.alertas = AlertasManager(self.connection)
            return self.alertas.obter_todos_alertas()
        except Exception as e:
            print(f"Erro em obter_todos_alertas: {str(e)}")
            return []
    
    def obter_resumo_alertas(self):
        try:
            if not hasattr(self, 'alertas') or self.alertas is None:
                print("Alertas manager não inicializado, criando...")
                self.alertas = AlertasManager(self.connection)
            return self.alertas.obter_resumo_alertas()
        except Exception as e:
            print(f"Erro em obter_resumo_alertas: {str(e)}")
            return {'total': 0, 'alta_prioridade': 0, 'media_prioridade': 0, 'por_tipo': {}}
    
    def verificar_antecedencia_insuficiente(self, data_inicio, usuario_nivel="colaborador"):
        try:
            if not hasattr(self, 'alertas') or self.alertas is None:
                self.alertas = AlertasManager(self.connection)
            return self.alertas.verificar_antecedencia_insuficiente(data_inicio, usuario_nivel)
        except Exception as e:
            print(f"Erro em verificar_antecedencia_insuficiente: {str(e)}")
            return None
    
    def verificar_feriados_detectados(self, data_inicio, data_fim):
        try:
            if not hasattr(self, 'alertas') or self.alertas is None:
                self.alertas = AlertasManager(self.connection)
            return self.alertas.verificar_feriados_detectados(data_inicio, data_fim)
        except Exception as e:
            print(f"Erro em verificar_feriados_detectados: {str(e)}")
            return None
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Aprovada", usuario_nivel="colaborador"):
        return self.ferias.add_ferias(usuario_id, data_inicio, data_fim, status, usuario_nivel)
    
    def get_ferias_usuario(self, usuario_id):
        return self.ferias.get_ferias_usuario(usuario_id)
    
    def update_ferias_status(self, ferias_id, novo_status):
        return self.ferias.update_ferias_status(ferias_id, novo_status)
    
    def delete_ferias(self, ferias_id):
        return self.ferias.delete_ferias(ferias_id)
    
    def update_ferias(self, ferias_id, data_inicio, data_fim, status):
        """Atualiza dados completos das férias"""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar dados atuais
                cursor.execute("SELECT * FROM ferias WHERE id = ?", (ferias_id,))
                ferias_atual = cursor.fetchone()
                
                if not ferias_atual:
                    return False
                
                usuario_id = ferias_atual[1]
                status_atual = ferias_atual[5]
                
                # Calcular novos dias úteis
                dias_novos = self.ferias._calcular_dias_uteis(data_inicio, data_fim)
                
                # Verificar saldo se mudando para aprovada
                if status_atual != "Aprovada" and status == "Aprovada":
                    cursor.execute("SELECT saldo_ferias FROM usuarios WHERE id = ?", (usuario_id,))
                    saldo_atual = cursor.fetchone()[0]
                    
                    if saldo_atual < dias_novos:
                        raise ValueError(f"Saldo insuficiente. Disponível: {saldo_atual} dias, Solicitado: {dias_novos} dias")
                
                # Atualizar usando o método de status que já gerencia saldo
                cursor.execute("""
                    UPDATE ferias 
                    SET data_inicio = ?, data_fim = ?, dias_utilizados = ?
                    WHERE id = ?
                """, (data_inicio, data_fim, dias_novos, ferias_id))
                
                conn.commit()
                
                # Atualizar status separadamente para aplicar regras de saldo
                return self.ferias.update_ferias_status(ferias_id, status)
                
        except Exception as e:
            print(f"Erro ao atualizar férias: {str(e)}")
            return False