import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database
import sqlite3

def test_database_integrity():
    """Testa integridade do banco de dados"""
    print("=== TESTE INTEGRIDADE DO BANCO ===")
    
    db = Database()
    
    # Teste 1: Verificar estrutura das tabelas
    print("\n1. Verificando estrutura das tabelas...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar tabela usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        usuarios_columns = [col[1] for col in cursor.fetchall()]
        expected_usuarios = ['id', 'nome', 'email', 'senha', 'setor', 'funcao', 'nivel_acesso', 'saldo_ferias', 'data_cadastro']
        
        if all(col in usuarios_columns for col in expected_usuarios):
            print("[OK] Tabela usuarios com estrutura correta")
        else:
            print(f"[ERRO] Tabela usuarios incorreta. Encontrado: {usuarios_columns}")
        
        # Verificar tabela ferias
        cursor.execute("PRAGMA table_info(ferias)")
        ferias_columns = [col[1] for col in cursor.fetchall()]
        expected_ferias = ['id', 'usuario_id', 'data_inicio', 'data_fim', 'dias_utilizados', 'status', 'data_registro']
        
        if all(col in ferias_columns for col in expected_ferias):
            print("[OK] Tabela ferias com estrutura correta")
        else:
            print(f"[ERRO] Tabela ferias incorreta. Encontrado: {ferias_columns}")
    
    # Teste 2: Verificar chaves estrangeiras
    print("\n2. Verificando integridade referencial...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar se todas as férias têm usuários válidos
        cursor.execute("""
            SELECT COUNT(*) FROM ferias f 
            LEFT JOIN usuarios u ON f.usuario_id = u.id 
            WHERE u.id IS NULL
        """)
        orphaned_ferias = cursor.fetchone()[0]
        
        if orphaned_ferias == 0:
            print("[OK] Todas as férias têm usuários válidos")
        else:
            print(f"[ERRO] {orphaned_ferias} férias órfãs encontradas")
    
    # Teste 3: Verificar consistência de saldos
    print("\n3. Verificando consistência de saldos...")
    users = db.get_users()
    inconsistencias = 0
    
    for _, user in users.iterrows():
        user_id = user['id']
        saldo_atual = user['saldo_ferias']
        
        # Calcular saldo baseado apenas nas férias APROVADAS
        ferias = db.get_ferias_usuario(user_id)
        if not ferias.empty:
            ferias_aprovadas = ferias[ferias['status'] == 'Aprovada']
            total_usado = ferias_aprovadas['dias_utilizados'].sum() if not ferias_aprovadas.empty else 0
        else:
            total_usado = 0
        saldo_calculado = 12 - total_usado
        
        if abs(saldo_atual - saldo_calculado) > 0:
            print(f"[ERRO] Inconsistência usuário {user['nome']}: Saldo={saldo_atual}, Calculado={saldo_calculado}")
            inconsistencias += 1
    
    if inconsistencias == 0:
        print("[OK] Todos os saldos estão consistentes")
    else:
        print(f"[ERRO] {inconsistencias} inconsistências encontradas")
    
    # Teste 4: Verificar dados obrigatórios
    print("\n4. Verificando dados obrigatórios...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Usuários sem nome ou email
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nome IS NULL OR nome = '' OR email IS NULL OR email = ''")
        invalid_users = cursor.fetchone()[0]
        
        if invalid_users == 0:
            print("[OK] Todos os usuários têm dados obrigatórios")
        else:
            print(f"[ERRO] {invalid_users} usuários com dados inválidos")
        
        # Férias sem datas
        cursor.execute("SELECT COUNT(*) FROM ferias WHERE data_inicio IS NULL OR data_fim IS NULL")
        invalid_ferias = cursor.fetchone()[0]
        
        if invalid_ferias == 0:
            print("[OK] Todas as férias têm datas válidas")
        else:
            print(f"[ERRO] {invalid_ferias} férias com datas inválidas")
    
    # Teste 5: Verificar backup automático
    print("\n5. Verificando sistema de backup...")
    import os
    backup_dir = "data/backups"
    
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.startswith("rpontes_rh_backup_")]
        if backups:
            print(f"[OK] Sistema de backup funcionando: {len(backups)} backups encontrados")
        else:
            print("[ERRO] Nenhum backup encontrado")
    else:
        print("[ERRO] Diretório de backup não existe")
    
    # Teste 6: Verificar performance de consultas
    print("\n6. Testando performance de consultas...")
    import time
    
    start_time = time.time()
    users = db.get_users()
    users_time = time.time() - start_time
    
    start_time = time.time()
    if not users.empty:
        ferias = db.get_ferias_usuario(users.iloc[0]['id'])
    ferias_time = time.time() - start_time
    
    if users_time < 1.0 and ferias_time < 1.0:
        print(f"[OK] Performance adequada: users={users_time:.3f}s, ferias={ferias_time:.3f}s")
    else:
        print(f"[ERRO] Performance lenta: users={users_time:.3f}s, ferias={ferias_time:.3f}s")

if __name__ == "__main__":
    test_database_integrity()