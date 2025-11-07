"""
Repositório de usuários
"""
import bcrypt
from datetime import date
from .base_connection import BaseConnection

class UsersRepository(BaseConnection):
    """Gerenciamento de usuários"""
    
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
            return None
    
    def get_users(self, setor=None, incluir_inativos=False):
        """Obtém usuários - retorna lista de dicts"""
        try:
            if incluir_inativos:
                if setor:
                    return self._execute_query("SELECT * FROM usuarios WHERE setor = %s ORDER BY nome", (setor,), fetch=True)
                return self._execute_query("SELECT * FROM usuarios ORDER BY nome", fetch=True)
            else:
                if setor:
                    return self._execute_query("SELECT * FROM usuarios WHERE setor = %s AND ativo = true ORDER BY nome", (setor,), fetch=True)
                return self._execute_query("SELECT * FROM usuarios WHERE ativo = true ORDER BY nome", fetch=True)
        except Exception as e:
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
            return False
    
    def update_user(self, user_id, nome, email, setor, funcao, nivel_acesso, saldo_ferias):
        """Atualiza usuário"""
        return self._execute_query("""
            UPDATE usuarios SET nome=%s, email=%s, setor=%s, funcao=%s, 
            nivel_acesso=%s, saldo_ferias=%s WHERE id=%s
        """, (nome, email, setor, funcao, nivel_acesso, saldo_ferias, user_id))
    
    def inativar_usuario(self, user_id):
        """Inativa usuário"""
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