import pandas as pd
from mysql.connector import Error
from datetime import datetime

class MySQLAuditoriaManager:
    def __init__(self, connection):
        self.connection = connection
    
    def registrar_alteracao_saldo(self, usuario_id, valor_anterior, valor_novo, 
                                 tipo_operacao, motivo, usuario_responsavel_id=None, 
                                 usuario_responsavel_nome=None, detalhes_adicionais=None):
        """Registra alteração de saldo no log de auditoria"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO auditoria_saldo 
                (usuario_id, usuario_responsavel_id, usuario_responsavel_nome,
                 motivo, valor_anterior, valor_novo, tipo_operacao, detalhes_adicionais)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, usuario_responsavel_id, usuario_responsavel_nome,
                  motivo, valor_anterior, valor_novo, tipo_operacao, detalhes_adicionais))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Erro ao registrar auditoria: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def obter_logs_auditoria(self, usuario_id=None, data_inicio=None, data_fim=None, 
                           tipo_operacao=None, limit=1000):
        """Obtém logs de auditoria com filtros"""
        try:
            conn = self.connection.get_connection()
            
            query = """
                SELECT a.*, u.nome as nome_usuario
                FROM auditoria_saldo a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE 1=1
            """
            
            params = []
            
            if usuario_id:
                query += " AND a.usuario_id = %s"
                params.append(usuario_id)
            
            if data_inicio:
                query += " AND DATE(a.data_hora) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(a.data_hora) <= %s"
                params.append(data_fim)
            
            if tipo_operacao:
                query += " AND a.tipo_operacao = %s"
                params.append(tipo_operacao)
            
            query += f" ORDER BY a.data_hora DESC LIMIT {limit}"
            
            df = pd.read_sql(query, conn, params=params if params else None)
            return df if not df.empty else pd.DataFrame()
            
        except Error as e:
            print(f"Erro ao obter logs de auditoria: {e}")
            return pd.DataFrame()
    
    def obter_historico_usuario(self, usuario_id):
        """Obtém histórico completo de alterações de saldo de um usuário"""
        return self.obter_logs_auditoria(usuario_id=usuario_id)
    
    def obter_estatisticas_auditoria(self):
        """Obtém estatísticas dos logs de auditoria"""
        try:
            conn = self.connection.get_connection()
            cursor = conn.cursor()
            
            # Verificar se tabela existe
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() AND table_name = 'auditoria_saldo'
            """)
            
            if cursor.fetchone()[0] == 0:
                return {
                    'total_registros': 0,
                    'por_tipo_operacao': [],
                    'ultimos_30_dias': 0
                }
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM auditoria_saldo")
            total_registros = cursor.fetchone()[0]
            
            # Registros por tipo de operação
            cursor.execute("""
                SELECT tipo_operacao, COUNT(*) as quantidade
                FROM auditoria_saldo
                GROUP BY tipo_operacao
                ORDER BY quantidade DESC
            """)
            por_tipo = cursor.fetchall()
            
            # Registros dos últimos 30 dias
            cursor.execute("""
                SELECT COUNT(*) FROM auditoria_saldo
                WHERE DATE(data_hora) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """)
            ultimos_30_dias = cursor.fetchone()[0]
            
            return {
                'total_registros': total_registros,
                'por_tipo_operacao': por_tipo,
                'ultimos_30_dias': ultimos_30_dias
            }
            
        except Error as e:
            print(f"Erro ao obter estatísticas de auditoria: {e}")
            return {
                'total_registros': 0,
                'por_tipo_operacao': [],
                'ultimos_30_dias': 0
            }
        finally:
            if cursor:
                cursor.close()