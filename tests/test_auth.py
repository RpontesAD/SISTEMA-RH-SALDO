import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database
import bcrypt

def test_authentication():
    """Testa sistema de autenticação"""
    print("=== TESTE DE AUTENTICAÇÃO ===")
    
    db = Database()
    
    # Teste 1: Login válido
    print("\n1. Testando login válido...")
    user = db.authenticate_user("admin@rpontes.com", "admin123")
    if user:
        print(f"[OK] Login válido: {user['nome']} - {user['nivel_acesso']}")
    else:
        print("[ERRO] Falha no login válido")
    
    # Teste 2: Login inválido - email errado
    print("\n2. Testando email inválido...")
    user = db.authenticate_user("inexistente@rpontes.com", "admin123")
    if not user:
        print("[OK] Email inválido rejeitado corretamente")
    else:
        print("[ERRO] Email inválido foi aceito")
    
    # Teste 3: Login inválido - senha errada
    print("\n3. Testando senha inválida...")
    user = db.authenticate_user("admin@rpontes.com", "senhaerrada")
    if not user:
        print("[OK] Senha inválida rejeitada corretamente")
    else:
        print("[ERRO] Senha inválida foi aceita")
    
    # Teste 4: Verificar hash de senha
    print("\n4. Testando hash de senhas...")
    users = db.get_users()
    admin = users[users['email'] == 'admin@rpontes.com'].iloc[0]
    
    # Verificar se senha está hasheada
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", ("admin@rpontes.com",))
        senha_hash = cursor.fetchone()[0]
    
    if isinstance(senha_hash, bytes) and senha_hash.startswith(b'$2b$'):
        print("[OK] Senha está corretamente hasheada com bcrypt")
    else:
        print("[ERRO] Senha não está hasheada corretamente")

if __name__ == "__main__":
    test_authentication()