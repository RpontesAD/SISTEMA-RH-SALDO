import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseConnection
from database.users import UsersDatabase
from database.ferias import FeriasDatabase

def test_crud_users():
    """Testa operações CRUD de usuários"""
    print("=== TESTE CRUD USUÁRIOS ===")
    
    db_conn = DatabaseConnection()
    db_conn.init_database()
    users_db = UsersDatabase()
    ferias_db = FeriasDatabase()
    
    # Teste 1: Criar usuário
    print("\n1. Testando criação de usuário...")
    success = users_db.create_user(
        "Teste Usuario", 
        "teste@rpontes.com", 
        "senha123", 
        "TI", 
        "Analista"
    )
    if success:
        print("[OK] Usuário criado com sucesso")
    else:
        print("[ERRO] Falha ao criar usuário")
    
    # Teste 2: Buscar usuário criado
    print("\n2. Testando busca de usuário...")
    users = users_db.get_all_users()
    test_user = None
    for user in users:
        if user['email'] == 'teste@rpontes.com':
            test_user = user
            break
    
    if test_user:
        user_id = test_user['id']
        print(f"[OK] Usuário encontrado: ID {user_id}")
    else:
        print("[ERRO] Usuário não encontrado")
        return
    
    # Teste 3: Atualizar usuário
    print("\n3. Testando atualização de usuário...")
    success = db.update_user(
        user_id,
        "Teste Usuario Atualizado",
        "teste@rpontes.com",
        "ENGENHARIA",
        "Coordenador",
        "coordenador",
        10
    )
    if success:
        print("[OK] Usuário atualizado com sucesso")
    else:
        print("[ERRO] Falha ao atualizar usuário")
    
    # Teste 4: Verificar atualização
    print("\n4. Verificando dados atualizados...")
    users = db.get_users()
    updated_user = users[users['id'] == user_id].iloc[0]
    if (updated_user['nome'] == "Teste Usuario Atualizado" and 
        updated_user['setor'] == "ENGENHARIA" and
        updated_user['saldo_ferias'] == 10):
        print("[OK] Dados atualizados corretamente")
    else:
        print("[ERRO] Dados não foram atualizados")
    
    # Teste 5: Atualizar apenas saldo
    print("\n5. Testando atualização de saldo...")
    success = db.update_saldo_ferias(user_id, 8)
    if success:
        users = db.get_users()
        user_saldo = users[users['id'] == user_id].iloc[0]['saldo_ferias']
        if user_saldo == 8:
            print("[OK] Saldo atualizado corretamente")
        else:
            print(f"[ERRO] Saldo não atualizado: {user_saldo}")
    else:
        print("[ERRO] Falha ao atualizar saldo")
    
    # Teste 6: Excluir usuário
    print("\n6. Testando exclusão de usuário...")
    success = db.delete_user(user_id)
    if success:
        print("[OK] Usuário excluído com sucesso")
    else:
        print("[ERRO] Falha ao excluir usuário")
    
    # Teste 7: Verificar exclusão
    print("\n7. Verificando exclusão...")
    users = db.get_users()
    deleted_user = users[users['id'] == user_id]
    if deleted_user.empty:
        print("[OK] Usuário removido do banco")
    else:
        print("[ERRO] Usuário ainda existe no banco")
    
    # Teste 8: Tentar criar usuário com email duplicado
    print("\n8. Testando email duplicado...")
    # Primeiro criar um usuário
    db.create_user("User1", "duplicado@test.com", "123456", "TI", "Analista")
    # Tentar criar outro com mesmo email
    success = db.create_user("User2", "duplicado@test.com", "123456", "TI", "Analista")
    if not success:
        print("[OK] Email duplicado rejeitado corretamente")
    else:
        print("[ERRO] Email duplicado foi aceito")
    
    # Limpar usuário de teste
    users = db.get_users()
    test_user = users[users['email'] == 'duplicado@test.com']
    if not test_user.empty:
        db.delete_user(test_user.iloc[0]['id'])

if __name__ == "__main__":
    test_crud_users()