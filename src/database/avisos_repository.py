"""
Repositório de avisos
"""
import psycopg2
from .base_connection import BaseConnection

class AvisosRepository(BaseConnection):
    """Gerenciamento de avisos"""
    
    def criar_aviso(self, titulo, conteudo, autor_id, destinatarios_ids):
        """Cria um novo aviso e associa aos destinatários"""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    # Inserir aviso
                    cur.execute("""
                        INSERT INTO avisos (titulo, conteudo, autor_id) 
                        VALUES (%s, %s, %s) RETURNING id
                    """, (titulo, conteudo, autor_id))
                    
                    aviso_id = cur.fetchone()[0]
                    
                    # Inserir destinatários
                    for usuario_id in destinatarios_ids:
                        cur.execute("""
                            INSERT INTO avisos_destinatarios (aviso_id, usuario_id) 
                            VALUES (%s, %s)
                        """, (aviso_id, usuario_id))
                    
                    conn.commit()
                    return True
        except Exception as e:
            return False
    
    def get_avisos_usuario(self, usuario_id):
        """Obtém avisos para um usuário específico (apenas não ocultos)"""
        # Garantir que a coluna oculto existe
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        return self._execute_query("""
            SELECT a.id, a.titulo, a.conteudo, a.data_criacao, 
                   u.nome as autor_nome, ad.lido, ad.data_leitura
            FROM avisos a
            JOIN avisos_destinatarios ad ON a.id = ad.aviso_id
            JOIN usuarios u ON a.autor_id = u.id
            WHERE ad.usuario_id = %s AND a.ativo = true AND COALESCE(ad.oculto, false) = false
            ORDER BY a.data_criacao DESC
        """, (usuario_id,), fetch=True)
    
    def marcar_aviso_lido(self, aviso_id, usuario_id):
        """Marca um aviso como lido"""
        return self._execute_query("""
            UPDATE avisos_destinatarios 
            SET lido = true, data_leitura = CURRENT_TIMESTAMP 
            WHERE aviso_id = %s AND usuario_id = %s
        """, (aviso_id, usuario_id))
    
    def get_avisos_admin(self):
        """Obtém todos os avisos para administração"""
        return self._execute_query("""
            SELECT a.id, a.titulo, a.data_criacao, u.nome as autor_nome,
                   COUNT(ad.id) as total_destinatarios,
                   COUNT(CASE WHEN ad.lido = true THEN 1 END) as total_lidos
            FROM avisos a
            JOIN usuarios u ON a.autor_id = u.id
            LEFT JOIN avisos_destinatarios ad ON a.id = ad.aviso_id
            WHERE a.ativo = true
            GROUP BY a.id, a.titulo, a.data_criacao, u.nome
            ORDER BY a.data_criacao DESC
        """, fetch=True)
    
    def get_status_leitura_aviso(self, aviso_id):
        """Obtém status de leitura de um aviso específico"""
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        return self._execute_query("""
            SELECT u.nome, u.setor, u.funcao, ad.lido, ad.data_leitura, COALESCE(ad.oculto, false) as oculto
            FROM avisos_destinatarios ad
            JOIN usuarios u ON ad.usuario_id = u.id
            WHERE ad.aviso_id = %s
            ORDER BY u.nome
        """, (aviso_id,), fetch=True)
    
    def get_aviso_detalhes(self, aviso_id):
        """Obtém detalhes de um aviso ativo"""
        result = self._execute_query("""
            SELECT titulo, conteudo FROM avisos WHERE id = %s AND ativo = true
        """, (aviso_id,), fetch=True)
        return result[0] if result else None
    
    def atualizar_aviso(self, aviso_id, titulo, conteudo):
        """Atualiza um aviso"""
        return self._execute_query("""
            UPDATE avisos SET titulo = %s, conteudo = %s WHERE id = %s
        """, (titulo, conteudo, aviso_id))
    
    def excluir_aviso(self, aviso_id):
        """Exclui um aviso (marca como inativo)"""
        return self._execute_query("""
            UPDATE avisos SET ativo = false WHERE id = %s
        """, (aviso_id,))
    
    def get_matriz_leitura_avisos(self):
        """Obtém matriz de leitura: todos os avisos ativos (incluindo ocultos pelos usuários)"""
        # Primeiro garantir que a coluna oculto existe
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        return self._execute_query("""
            SELECT 
                u.nome,
                u.setor,
                u.funcao,
                a.id as aviso_id,
                a.titulo,
                COALESCE(ad.lido, false) as lido,
                ad.data_leitura,
                COALESCE(ad.oculto, false) as oculto
            FROM avisos a
            JOIN avisos_destinatarios ad ON a.id = ad.aviso_id
            JOIN usuarios u ON ad.usuario_id = u.id
            WHERE a.ativo = true AND u.ativo = true
            ORDER BY a.data_criacao DESC, u.nome
        """, fetch=True)
    
    def remover_aviso_usuario(self, aviso_id, usuario_id):
        """Oculta aviso da visualização do usuário"""
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        return self._execute_query("""
            UPDATE avisos_destinatarios SET oculto = true 
            WHERE aviso_id = %s AND usuario_id = %s
        """, (aviso_id, usuario_id))