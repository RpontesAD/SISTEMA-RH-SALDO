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
        # Construir connection string a partir dos componentes
        pg_config = st.secrets["connections"]["postgresql"]
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
                ativo BOOLEAN DEFAULT true,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_admissao DATE
            )
        """)
        
        # Adicionar coluna ativo se não existir (para bancos existentes)
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
        
        # Criar tabela renovacao_saldo (sem backup)
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS renovacao_saldo (
                id SERIAL PRIMARY KEY,
                ano INTEGER UNIQUE NOT NULL,
                saldo_padrao INTEGER NOT NULL,
                data_aplicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_responsavel_id INTEGER REFERENCES usuarios(id)
            )
        """)
        
        # Remover coluna backup_dados se existir
        self._execute_query("""
            ALTER TABLE renovacao_saldo DROP COLUMN IF EXISTS backup_dados
        """)
        
        # Criar tabela saldos_anuais
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS saldos_anuais (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                ano INTEGER NOT NULL,
                saldo_inicial INTEGER NOT NULL,
                saldo_atual INTEGER NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(usuario_id, ano)
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
        
        # Adicionar coluna oculto se não existir (forçar atualização)
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        # Garantir que registros existentes tenham oculto = false
        self._execute_query("""
            UPDATE avisos_destinatarios SET oculto = false WHERE oculto IS NULL
        """)
        
        # Habilitar RLS nas novas tabelas
        self._execute_query("ALTER TABLE renovacao_saldo ENABLE ROW LEVEL SECURITY")
        self._execute_query("ALTER TABLE saldos_anuais ENABLE ROW LEVEL SECURITY")
        self._execute_query("ALTER TABLE avisos ENABLE ROW LEVEL SECURITY")
        self._execute_query("ALTER TABLE avisos_destinatarios ENABLE ROW LEVEL SECURITY")
        
        # Criar políticas RLS para renovacao_saldo
        self._execute_query("""
            CREATE POLICY IF NOT EXISTS "Permitir acesso total" ON renovacao_saldo
            FOR ALL USING (true)
        """)
        
        # Criar políticas RLS para saldos_anuais
        self._execute_query("""
            CREATE POLICY IF NOT EXISTS "Permitir acesso total" ON saldos_anuais
            FOR ALL USING (true)
        """)
        
        # Criar políticas RLS para avisos
        self._execute_query("""
            CREATE POLICY IF NOT EXISTS "Permitir acesso total" ON avisos
            FOR ALL USING (true)
        """)
        
        # Criar políticas RLS para avisos_destinatarios
        self._execute_query("""
            CREATE POLICY IF NOT EXISTS "Permitir acesso total" ON avisos_destinatarios
            FOR ALL USING (true)
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
    
    def authenticate_user(self, email, senha):
        """Autentica usuário (apenas usuários ativos)"""
        try:
            users = self._execute_query("SELECT * FROM usuarios WHERE email = %s AND ativo = true", (email,), fetch=True)
            
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
                        'saldo_ferias': user['saldo_ferias'],
                        'ativo': user.get('ativo', True)
                    }
            return None
        except Exception as e:
            st.error(f"Erro na autenticação: {e}")
            return None
    
    def get_users(self, setor=None, incluir_inativos=False):
        """Obtém usuários - retorna lista de dicts"""
        try:
            if incluir_inativos:
                # Incluir todos os usuários (ativos e inativos)
                if setor:
                    return self._execute_query("SELECT * FROM usuarios WHERE setor = %s ORDER BY nome", (setor,), fetch=True)
                return self._execute_query("SELECT * FROM usuarios ORDER BY nome", fetch=True)
            else:
                # Apenas usuários ativos (padrão)
                if setor:
                    return self._execute_query("SELECT * FROM usuarios WHERE setor = %s AND ativo = true ORDER BY nome", (setor,), fetch=True)
                return self._execute_query("SELECT * FROM usuarios WHERE ativo = true ORDER BY nome", fetch=True)
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return []
    
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
    
    def inativar_usuario(self, user_id):
        """Inativa usuário (não exclui, apenas marca como inativo)"""
        return self._execute_query("UPDATE usuarios SET ativo = false WHERE id = %s", (user_id,))
    
    def ativar_usuario(self, user_id):
        """Reativa usuário"""
        return self._execute_query("UPDATE usuarios SET ativo = true WHERE id = %s", (user_id,))
    
    def delete_user(self, user_id):
        """Exclui usuário"""
        return self._execute_query("DELETE FROM usuarios WHERE id=%s", (user_id,))
    
    def update_saldo_ferias(self, user_id, novo_saldo, usuario_responsavel_id=None, usuario_responsavel_nome=None, motivo="Ajuste manual"):
        """Atualiza saldo"""
        return self._execute_query("UPDATE usuarios SET saldo_ferias=%s WHERE id=%s", (novo_saldo, user_id))
    
    def update_password(self, user_id, nova_senha):
        """Atualiza senha do usuário"""
        try:
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return self._execute_query("UPDATE usuarios SET senha_hash=%s WHERE id=%s", (senha_hash, user_id))
        except Exception as e:
            return False
    
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
                        
                        # Ajustar saldo - aceitar tanto "Aprovado" quanto "Aprovada"
                        status_atual_lower = status_atual.lower() if status_atual else ""
                        novo_status_lower = novo_status.lower() if novo_status else ""
                        

                        
                        # Se mudou de não-aprovado para aprovado
                        if status_atual_lower not in ["aprovado", "aprovada"] and novo_status_lower in ["aprovado", "aprovada"]:
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE id = %s", (dias_utilizados, usuario_id))
                            print(f"Descontando {dias_utilizados} dias do usuário {usuario_id}")
                        # Se mudou de aprovado para não-aprovado
                        elif status_atual_lower in ["aprovado", "aprovada"] and novo_status_lower not in ["aprovado", "aprovada"]:
                            cur.execute("UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE id = %s", (dias_utilizados, usuario_id))
                            print(f"Devolvendo {dias_utilizados} dias ao usuário {usuario_id}")

                        
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
    
    def verificar_renovacao_ano(self, ano):
        """Verifica se já houve renovação no ano"""
        result = self._execute_query("SELECT COUNT(*) as count FROM renovacao_saldo WHERE ano = %s", (ano,), fetch=True)
        return result[0]['count'] > 0 if result else False
    

    
    def renovar_saldo_anual_simples(self, ano, saldo_adicional, usuario_responsavel_id):
        """Renova saldo anual - versão simplificada sem backup"""
        try:
            # Verificar se já existe renovação para o ano
            result = self._execute_query("SELECT COUNT(*) as count FROM renovacao_saldo WHERE ano = %s", (ano,), fetch=True)
            if result and result[0]['count'] > 0:
                return False, "Já foi realizada renovação para este ano"
            
            # Atualizar saldos
            success1 = self._execute_query(
                "UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE ativo = true",
                (saldo_adicional,)
            )
            
            if not success1:
                return False, "Erro ao atualizar saldos"
            
            # Registrar renovação
            success2 = self._execute_query(
                "INSERT INTO renovacao_saldo (ano, saldo_padrao, usuario_responsavel_id) VALUES (%s, %s, %s)",
                (ano, saldo_adicional, usuario_responsavel_id)
            )
            
            if not success2:
                return False, "Erro ao registrar renovação"
            
            # Contar usuários
            usuarios = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE ativo = true", fetch=True)
            total = usuarios[0]['count'] if usuarios else 0
            
            return True, f"Renovação aplicada! {total} colaboradores receberam +{saldo_adicional} dias para {ano}."
            
        except Exception as e:
            return False, f"Erro na renovação: {str(e)}"
    
    def renovar_saldo_anual(self, ano, saldo_adicional, usuario_responsavel_id, modo_teste=False):
        """Método compatível que chama a versão simplificada"""
        if modo_teste:
            usuarios = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE ativo = true", fetch=True)
            total = usuarios[0]['count'] if usuarios else 0
            return True, f"SIMULAÇÃO: {total} colaboradores receberiam +{saldo_adicional} dias somados ao saldo atual"
        
        return self.renovar_saldo_anual_simples(ano, saldo_adicional, usuario_responsavel_id)
    
    def get_historico_renovacoes(self):
        """Obtém histórico de renovações"""
        return self._execute_query("""
            SELECT r.*, u.nome as responsavel_nome 
            FROM renovacao_saldo r 
            LEFT JOIN usuarios u ON r.usuario_responsavel_id = u.id 
            ORDER BY r.ano DESC
        """, fetch=True)
    
    def desfazer_ultima_renovacao(self, usuario_responsavel_id):
        """Desfaz a última renovação subtraindo o valor adicionado"""
        try:
            # Buscar última renovação
            renovacoes = self._execute_query(
                "SELECT * FROM renovacao_saldo ORDER BY data_aplicacao DESC LIMIT 1",
                fetch=True
            )
            
            if not renovacoes:
                return False, "Nenhuma renovação encontrada para desfazer"
            
            renovacao = renovacoes[0]
            saldo_adicionado = renovacao['saldo_padrao']
            
            # Verificar se foi feita hoje (segurança)
            from datetime import date
            data_renovacao = renovacao['data_aplicacao'].date()
            if data_renovacao != date.today():
                return False, "Só é possível desfazer renovações do mesmo dia"
            
            # Subtrair o valor que foi adicionado
            success1 = self._execute_query(
                "UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE ativo = true AND saldo_ferias >= %s",
                (saldo_adicionado, saldo_adicionado)
            )
            
            if not success1:
                return False, "Erro ao atualizar saldos"
            
            # Remover registro de renovação
            success2 = self._execute_query(
                "DELETE FROM renovacao_saldo WHERE id = %s",
                (renovacao['id'],)
            )
            
            if not success2:
                return False, "Erro ao remover registro"
            
            return True, f"Renovação desfeita! Valor de {saldo_adicionado} dias foi removido dos saldos."
            
        except Exception as e:
            return False, f"Erro ao desfazer renovação: {str(e)}"
    
    def get_estatisticas_saldo(self, ano=None):
        """Obtém estatísticas dos saldos atuais ou por ano"""
        if ano:
            return self._execute_query("""
                SELECT 
                    COUNT(*) as total_colaboradores,
                    AVG(saldo_atual) as saldo_medio,
                    MIN(saldo_atual) as saldo_minimo,
                    MAX(saldo_atual) as saldo_maximo
                FROM saldos_anuais WHERE ano = %s
            """, (ano,), fetch=True)
        else:
            return self._execute_query("""
                SELECT 
                    COUNT(*) as total_colaboradores,
                    AVG(saldo_ferias) as saldo_medio,
                    MIN(saldo_ferias) as saldo_minimo,
                    MAX(saldo_ferias) as saldo_maximo
                FROM usuarios
            """, fetch=True)
    
    def get_saldo_usuario_ano(self, usuario_id, ano):
        """Obtém saldo de um usuário em um ano específico"""
        result = self._execute_query("""
            SELECT saldo_atual FROM saldos_anuais 
            WHERE usuario_id = %s AND ano = %s
        """, (usuario_id, ano), fetch=True)
        return result[0]['saldo_atual'] if result else None
    
    def get_historico_saldos_usuario(self, usuario_id):
        """Obtém histórico de saldos de um usuário por ano"""
        return self._execute_query("""
            SELECT ano, saldo_inicial, saldo_atual, data_criacao
            FROM saldos_anuais 
            WHERE usuario_id = %s 
            ORDER BY ano DESC
        """, (usuario_id,), fetch=True)
    
    def get_anos_disponiveis(self):
        """Obtém lista de anos com saldos registrados"""
        return self._execute_query("""
            SELECT DISTINCT ano FROM saldos_anuais ORDER BY ano DESC
        """, fetch=True)
    
    def migrar_saldos_existentes(self):
        """Migra saldos existentes para a nova estrutura"""
        try:
            from datetime import date
            ano_atual = date.today().year
            
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    # Buscar usuários que não têm saldo no ano atual
                    cur.execute("""
                        SELECT u.id, u.saldo_ferias 
                        FROM usuarios u
                        LEFT JOIN saldos_anuais sa ON u.id = sa.usuario_id AND sa.ano = %s
                        WHERE sa.id IS NULL
                    """, (ano_atual,))
                    
                    usuarios_sem_saldo = cur.fetchall()
                    
                    # Criar registros para o ano atual
                    for usuario in usuarios_sem_saldo:
                        cur.execute("""
                            INSERT INTO saldos_anuais (usuario_id, ano, saldo_inicial, saldo_atual)
                            VALUES (%s, %s, %s, %s)
                        """, (usuario[0], ano_atual, usuario[1], usuario[1]))
                    
                    conn.commit()
                    return len(usuarios_sem_saldo)
        except Exception as e:
            return 0
    
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
        """Obtém todos os avisos para administração (incluindo ocultos pelos usuários)"""
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
        """Obtém status de leitura de um aviso específico (incluindo ocultos)"""
        # Primeiro garantir que a coluna oculto existe
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
    
    def remover_aviso_usuario(self, aviso_id, usuario_id):
        """Oculta aviso da visualização do usuário (preserva dados para controle)"""
        # Garantir que a coluna oculto existe
        self._execute_query("""
            ALTER TABLE avisos_destinatarios ADD COLUMN IF NOT EXISTS oculto BOOLEAN DEFAULT false
        """)
        
        # Atualizar para oculto
        return self._execute_query("""
            UPDATE avisos_destinatarios SET oculto = true 
            WHERE aviso_id = %s AND usuario_id = %s
        """, (aviso_id, usuario_id))
    

    def close(self):
        pass