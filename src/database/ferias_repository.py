"""
Repositório de férias
"""
import psycopg2
from .base_connection import BaseConnection

class FeriasRepository(BaseConnection):
    """Gerenciamento de férias"""
    
    def add_ferias(self, usuario_id, data_inicio, data_fim, status="Pendente", usuario_nivel="colaborador"):
        """Adiciona férias"""
        try:
            # Calcular apenas dias úteis (sem fins de semana)
            from ..utils.calculos import calcular_dias_uteis
            dias_utilizados = calcular_dias_uteis(data_inicio, data_fim)
            
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    # Inserir férias
                    cur.execute("""
                        INSERT INTO ferias (usuario_id, data_inicio, data_fim, dias_utilizados, status) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (usuario_id, data_inicio, data_fim, dias_utilizados, status))
                    
                    # Atualizar saldo se aprovada
                    if status.lower() in ["aprovado", "aprovada"]:
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
                        status_atual_lower = status_atual.lower() if status_atual else ""
                        novo_status_lower = novo_status.lower() if novo_status else ""
                        
                        # Se mudou de não-aprovado para aprovado
                        if status_atual_lower not in ["aprovado", "aprovada"] and novo_status_lower in ["aprovado", "aprovada"]:
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_utilizados, usuario_id))
                        # Se mudou de aprovado para não-aprovado
                        elif status_atual_lower in ["aprovado", "aprovada"] and novo_status_lower not in ["aprovado", "aprovada"]:
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
                        if status.lower() in ["aprovado", "aprovada"]:
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
                        
                        conn.commit()
                        return True
            return False
        except:
            return False