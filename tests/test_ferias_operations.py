import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseConnection
from database.users import UsersDatabase
from database.ferias import FeriasDatabase
from datetime import date, timedelta

def test_ferias_operations():
    """Testa operações completas de férias"""
    print("=== TESTE OPERAÇÕES DE FÉRIAS ===")
    
    db_conn = DatabaseConnection()
    db_conn.init_database()
    users_db = UsersDatabase()
    ferias_db = FeriasDatabase()
    
    # Criar usuário de teste
    db.create_user("Teste Ferias", "ferias@test.com", "123456", "TI", "Analista", "colaborador", 12)
    users = db.get_users()
    test_user = users[users['email'] == 'ferias@test.com'].iloc[0]
    user_id = test_user['id']
    
    print(f"Usuário de teste criado: ID {user_id}, Saldo inicial: {test_user['saldo_ferias']}")
    
    # Teste 1: Adicionar férias aprovadas
    print("\n1. Testando férias aprovadas...")
    data_inicio = date.today() + timedelta(days=7)
    data_fim = data_inicio + timedelta(days=4)  # 5 dias
    
    success = db.add_ferias(user_id, data_inicio, data_fim, "Aprovada")
    if success:
        users = db.get_users()
        saldo_atual = users[users['id'] == user_id].iloc[0]['saldo_ferias']
        print(f"[OK] Férias aprovadas adicionadas. Saldo: {saldo_atual} (esperado: 7)")
    else:
        print("[ERRO] Falha ao adicionar férias aprovadas")
    
    # Teste 2: Adicionar férias pendentes
    print("\n2. Testando férias pendentes...")
    data_inicio2 = data_fim + timedelta(days=10)
    data_fim2 = data_inicio2 + timedelta(days=2)  # 3 dias
    
    success = db.add_ferias(user_id, data_inicio2, data_fim2, "Pendente")
    if success:
        users = db.get_users()
        saldo_atual = users[users['id'] == user_id].iloc[0]['saldo_ferias']
        print(f"[OK] Férias pendentes adicionadas. Saldo: {saldo_atual} (esperado: 4)")
    else:
        print("[ERRO] Falha ao adicionar férias pendentes")
    
    # Teste 3: Verificar histórico
    print("\n3. Verificando histórico de férias...")
    ferias = db.get_ferias_usuario(user_id)
    if len(ferias) == 2:
        print(f"[OK] Histórico correto: {len(ferias)} períodos")
        for _, f in ferias.iterrows():
            print(f"   - {f['data_inicio']} a {f['data_fim']} ({f['dias_utilizados']} dias) - {f['status']}")
    else:
        print(f"[ERRO] Histórico incorreto: {len(ferias)} períodos (esperado: 2)")
    
    # Teste 4: Tentar adicionar férias com saldo insuficiente
    print("\n4. Testando saldo insuficiente...")
    data_inicio3 = data_fim2 + timedelta(days=10)
    data_fim3 = data_inicio3 + timedelta(days=9)  # 10 dias (mais que o saldo)
    
    success = db.add_ferias(user_id, data_inicio3, data_fim3, "Aprovada")
    if not success:
        print("[OK] Saldo insuficiente rejeitado corretamente")
    else:
        print("[ERRO] Saldo insuficiente foi aceito")
    
    # Teste 5: Editar férias
    print("\n5. Testando edição de férias...")
    ferias_id = ferias.iloc[0]['id']
    nova_data_fim = data_inicio + timedelta(days=2)  # Reduzir de 5 para 3 dias
    
    success = db.update_ferias(ferias_id, data_inicio, nova_data_fim, "Aprovada")
    if success:
        users = db.get_users()
        saldo_atual = users[users['id'] == user_id].iloc[0]['saldo_ferias']
        print(f"[OK] Férias editadas. Novo saldo: {saldo_atual} (esperado: 6)")
    else:
        print("[ERRO] Falha ao editar férias")
    
    # Teste 6: Excluir férias
    print("\n6. Testando exclusão de férias...")
    ferias = db.get_ferias_usuario(user_id)
    ferias_id = ferias.iloc[1]['id']  # Segunda férias (pendente)
    
    success = db.delete_ferias(ferias_id)
    if success:
        users = db.get_users()
        saldo_atual = users[users['id'] == user_id].iloc[0]['saldo_ferias']
        print(f"[OK] Férias excluídas. Saldo restaurado: {saldo_atual} (esperado: 9)")
    else:
        print("[ERRO] Falha ao excluir férias")
    
    # Teste 7: Verificar sobreposição de datas
    print("\n7. Testando sobreposição de datas...")
    # Tentar adicionar férias que se sobrepõem
    data_sobreposicao = data_inicio + timedelta(days=1)
    data_fim_sobreposicao = data_sobreposicao + timedelta(days=2)
    
    success = db.add_ferias(user_id, data_sobreposicao, data_fim_sobreposicao, "Aprovada")
    if not success:
        print("[OK] Sobreposição de datas rejeitada")
    else:
        print("[ERRO] Sobreposição de datas foi aceita")
    
    # Limpeza: excluir usuário de teste
    print("\n8. Limpando dados de teste...")
    db.delete_user(user_id)
    print("[OK] Usuário de teste removido")

if __name__ == "__main__":
    test_ferias_operations()