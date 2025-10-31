import pandas as pd
import bcrypt
from mysql.connector import Error
from datetime import datetime, date
from ..core.regras_saldo import RegrasSaldo

class MySQLUserManager:
    def __init__(self, connection):
        self.connection = connection
        self.create_default_admin()
    
    def create_default_admin(self):
        """Cria usuário admin padrão se não existir"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", ('admin@rpontes.com',))
            count = cursor.fetchone()[0]
            
            if count == 0:
                try:
                    from ..config import DIAS_FERIAS_PADRAO
                except ImportError:
                    DIAS_FERIAS_PADRAO = 12
                
                senha_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, ("Administrador", "admin@rpontes.com", senha_hash, 
                     "GESTÃO DE PESSOAS (RH)", "RH", "master", DIAS_FERIAS_PADRAO))
                
                conn.commit()
                print("Admin padrão criado no MySQL")
                
        except Error as e:
            print(f"Erro ao criar admin padrão: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def authenticate_user(self, email, senha):
        """Autentica usuário"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias
                FROM usuarios WHERE email = %s
            """, (email,))
            
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(senha.encode("utf-8"), user[3].encode("utf-8")):
                return {
                    "id": user[0],
                    "nome": user[1],
                    "email": user[2],
                    "setor": user[4],
                    "funcao": user[5],
                    "nivel_acesso": user[6],
                    "saldo_ferias": user[7]
                }
            return None
            
        except Error as e:
            print(f"Erro na autenticação: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_users(self, setor=None):
        """Obtém lista de usuários"""
        try:
            conn = self.connection.get_connection()
            
            query = """
                SELECT id, nome, email, setor, funcao, nivel_acesso, saldo_ferias,
                       data_cadastro, data_admissao, ultima_renovacao
                FROM usuarios
            """
            
            if setor:
                query += " WHERE setor = %s"
                df = pd.read_sql(query, conn, params=[setor])
            else:
                df = pd.read_sql(query, conn)
            
            if df.empty:
                return pd.DataFrame()
            
            # Processar saldos e férias pendentes
            for idx, user in df.iterrows():
                try:
                    # Buscar férias do usuário
                    ferias_query = """
                        SELECT dias_utilizados, status
                        FROM ferias
                        WHERE usuario_id = %s
                    """
                    ferias_df = pd.read_sql(ferias_query, conn, params=[user['id']])
                    
                    saldo_base = user['saldo_ferias'] if user['saldo_ferias'] is not None else 0
                    
                    if not ferias_df.empty:
                        ferias_pendentes = ferias_df[ferias_df['status'] == 'Pendente']
                        dias_pendentes = ferias_pendentes['dias_utilizados'].sum() if not ferias_pendentes.empty else 0
                        saldo_pendente = max(0, saldo_base - dias_pendentes)
                        df.at[idx, 'saldo_pendente'] = saldo_pendente
                    else:
                        df.at[idx, 'saldo_pendente'] = saldo_base
                    
                    df.at[idx, 'saldo_atual'] = saldo_base
                    
                except Exception as e:
                    print(f"Erro ao calcular saldo para usuário {user['id']}: {e}")
                    df.at[idx, 'saldo_atual'] = saldo_base
                    df.at[idx, 'saldo_pendente'] = saldo_base
            
            return df
            
        except Error as e:
            print(f"Erro ao buscar usuários: {e}")
            return pd.DataFrame()
    
    def create_user(self, nome, email, senha, setor, funcao, nivel_acesso="colaborador", saldo_ferias=12, data_admissao=None):
        """Cria novo usuário"""
        try:
            senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode('utf-8')
            
            if data_admissao is None:
                data_admissao = date.today()
            
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, setor, funcao, nivel_acesso, saldo_ferias, 
                                    data_admissao, ultima_renovacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, setor, funcao, nivel_acesso, saldo_ferias,
                  data_admissao, data_admissao))
            
            conn.commit()
            return True
            
        except Error as e:
            print(f"Erro ao criar usuário: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usuarios 
                SET nome = %s, email = %s, setor = %s, funcao = %s,
                    nivel_acesso = %s, saldo_ferias = %s
                WHERE id = %s
            """, (nome, email, setor, funcao, nivel_acesso, saldo_ferias, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao atualizar usuário: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def delete_user(self, user_id):
        """Exclui usuário e suas férias"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            # MySQL com CASCADE vai excluir férias automaticamente
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao excluir usuário: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Edição manual de saldo"):
        """Atualiza saldo de férias"""
        try:
            # Validar saldo usando RegrasSaldo
            validacao = RegrasSaldo.validar_saldo_dentro_limites(novo_saldo)
            if not validacao["valido"]:
                print(f"ERRO: {validacao['mensagem']}")
                return False
            
            novo_saldo = validacao["saldo_corrigido"]
            
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            # Obter saldo anterior
            cursor.execute("SELECT saldo_ferias FROM usuarios WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            saldo_anterior = result[0]
            
            # Atualizar saldo
            cursor.execute("UPDATE usuarios SET saldo_ferias = %s WHERE id = %s", (novo_saldo, user_id))
            
            # Registrar auditoria se houve mudança
            if saldo_anterior != novo_saldo:
                try:
                    from .mysql_auditoria import MySQLAuditoriaManager
                    auditoria = MySQLAuditoriaManager(self.connection)
                    auditoria.registrar_alteracao_saldo(
                        usuario_id=user_id,
                        valor_anterior=saldo_anterior,
                        valor_novo=novo_saldo,
                        tipo_operacao="edicao_manual",
                        motivo=motivo,
                        usuario_responsavel_id=usuario_responsavel_id,
                        usuario_responsavel_nome=usuario_responsavel_nome
                    )
                except Exception as e:
                    print(f"Erro ao registrar auditoria: {e}")
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao atualizar saldo: {e}")
            return False
        finally:
            if cursor:
                cursor.close()