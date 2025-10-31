import pandas as pd
from mysql.connector import Error
from datetime import datetime, date
from ..core.regras_ferias import RegrasFerias

class MySQLFeriasManager:
    def __init__(self, connection):
        self.connection = connection
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Aprovado", usuario_nivel="colaborador"):
        """Adiciona período de férias"""
        try:
            # Calcular dias úteis
            from ..utils.calculos import calcular_dias_uteis
            dias_utilizados = calcular_dias_uteis(data_inicio, data_fim)
            
            # Validar usando regras de negócio apenas se não for RH
            if usuario_nivel != "master":
                validacao_antecedencia = RegrasFerias.validar_antecedencia(data_inicio, usuario_nivel)
                if not validacao_antecedencia["valida"]:
                    raise ValueError(validacao_antecedencia["mensagem"])
            
            # Se for férias aprovada, verificar saldo
            if status == "Aprovado":
                conn = self.connection.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT saldo_ferias FROM usuarios WHERE id = %s", (usuario_id,))
                result = cursor.fetchone()
                if not result:
                    raise ValueError("Usuário não encontrado")
                
                saldo_atual = result[0]
                validacao_saldo = RegrasFerias.validar_saldo_suficiente(saldo_atual, dias_utilizados, status)
                if not validacao_saldo["valida"]:
                    raise ValueError(validacao_saldo["mensagem"])
                
                cursor.close()
            
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario_id, data_inicio, data_fim, dias_utilizados, status))
            
            # Se for aprovada, descontar do saldo
            if status == "Aprovado":
                cursor.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", 
                             (dias_utilizados, usuario_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao adicionar férias: {e}")
            return False
        except ValueError as ve:
            print(f"Erro de validação: {ve}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_ferias_usuario(self, usuario_id):
        """Obtém férias de um usuário"""
        try:
            conn = self.connection.get_connection()
            
            query = """
                SELECT id, usuario_id, data_inicio, data_fim, dias_utilizados, status, data_registro
                FROM ferias
                WHERE usuario_id = %s
                ORDER BY data_inicio DESC
            """
            
            df = pd.read_sql(query, conn, params=[usuario_id])
            return df if not df.empty else pd.DataFrame()
            
        except Error as e:
            print(f"Erro ao buscar férias do usuário: {e}")
            return pd.DataFrame()
    
    def get_all_ferias(self, status=None, data_inicio=None, data_fim=None):
        """Obtém todas as férias com filtros opcionais"""
        try:
            conn = self.connection.get_connection()
            
            query = """
                SELECT f.id, f.usuario_id, u.nome, u.setor, f.data_inicio, f.data_fim, 
                       f.dias_utilizados, f.status, f.data_registro
                FROM ferias f
                JOIN usuarios u ON f.usuario_id = u.id
                WHERE 1=1
            """
            
            params = []
            
            if status:
                query += " AND f.status = %s"
                params.append(status)
            
            if data_inicio:
                query += " AND f.data_inicio >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND f.data_fim <= %s"
                params.append(data_fim)
            
            query += " ORDER BY f.data_inicio DESC"
            
            df = pd.read_sql(query, conn, params=params if params else None)
            return df if not df.empty else pd.DataFrame()
            
        except Error as e:
            print(f"Erro ao buscar todas as férias: {e}")
            return pd.DataFrame()
    
    def update_ferias_status(self, ferias_id, novo_status, usuario_responsavel_id=None):
        """Atualiza status das férias"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            # Obter dados das férias
            cursor.execute("""
                SELECT usuario_id, dias_utilizados, status
                FROM ferias
                WHERE id = %s
            """, (ferias_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            usuario_id, dias_utilizados, status_atual = result
            
            # Obter saldo atual do usuário
            cursor.execute("SELECT saldo_ferias FROM usuarios WHERE id = %s", (usuario_id,))
            saldo_result = cursor.fetchone()
            if not saldo_result:
                return False
            
            saldo_atual = saldo_result[0]
            
            # Atualizar status das férias
            cursor.execute("UPDATE ferias SET status = %s WHERE id = %s", (novo_status, ferias_id))
            
            # Atualizar saldo baseado na mudança de status
            if status_atual != novo_status:
                if status_atual == "Aprovado" and novo_status != "Aprovado":
                    # Devolver saldo
                    novo_saldo = saldo_atual + dias_utilizados
                    cursor.execute("UPDATE usuarios SET saldo_ferias = %s WHERE id = %s", (novo_saldo, usuario_id))
                elif status_atual != "Aprovado" and novo_status == "Aprovado":
                    # Descontar saldo
                    if saldo_atual >= dias_utilizados:
                        novo_saldo = saldo_atual - dias_utilizados
                        cursor.execute("UPDATE usuarios SET saldo_ferias = %s WHERE id = %s", (novo_saldo, usuario_id))
                    else:
                        cursor.close()
                        return False
            
            conn.commit()
            return True
            
        except Error as e:
            print(f"Erro ao atualizar status das férias: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def delete_ferias(self, ferias_id, usuario_responsavel_id=None):
        """Exclui período de férias"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            # Obter dados das férias antes de excluir
            cursor.execute("""
                SELECT usuario_id, dias_utilizados, status
                FROM ferias
                WHERE id = %s
            """, (ferias_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            usuario_id, dias_utilizados, status = result
            
            # Se férias estavam aprovadas, devolver saldo
            if status == "Aprovado":
                cursor.execute("SELECT saldo_ferias FROM usuarios WHERE id = %s", (usuario_id,))
                saldo_result = cursor.fetchone()
                
                if saldo_result:
                    saldo_atual = saldo_result[0]
                    novo_saldo = saldo_atual + dias_utilizados  # Sem limite máximo
                    
                    cursor.execute("UPDATE usuarios SET saldo_ferias = %s WHERE id = %s", 
                                 (novo_saldo, usuario_id))
                    
                    # Registrar auditoria
                    try:
                        from .mysql_auditoria import MySQLAuditoriaManager
                        auditoria = MySQLAuditoriaManager(self.connection)
                        auditoria.registrar_alteracao_saldo(
                            usuario_id=usuario_id,
                            valor_anterior=saldo_atual,
                            valor_novo=novo_saldo,
                            tipo_operacao="exclusao_ferias",
                            motivo="Exclusão de período de férias aprovado",
                            usuario_responsavel_id=usuario_responsavel_id
                        )
                    except Exception as e:
                        print(f"Erro ao registrar auditoria: {e}")
            
            # Excluir férias
            cursor.execute("DELETE FROM ferias WHERE id = %s", (ferias_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao excluir férias: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def verificar_antecedencia(self, data_inicio, usuario_nivel="colaborador"):
        """Verifica antecedência mínima"""
        return RegrasFerias.validar_antecedencia(data_inicio, usuario_nivel)
    
    def calcular_detalhes_periodo(self, data_inicio, data_fim):
        """Calcula detalhes do período de férias"""
        return RegrasFerias.validar_periodo(data_inicio, data_fim)