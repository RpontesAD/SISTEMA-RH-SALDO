import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database
import sqlite3
import os

def debug_system():
    """Script de debug completo do sistema"""
    print("DEBUG COMPLETO DO SISTEMA RPONTES RH")
    print("=" * 50)
    
    # 1. Verificar arquivos e estrutura
    print("\nVERIFICANDO ESTRUTURA DE ARQUIVOS")
    print("-" * 30)
    
    required_files = [
        '../src/database.py',
        '../src/auth.py', 
        '../src/menus.py',
        '../src/config.py',
        '../src/utils/validators.py',
        '../src/utils/ui_components.py',
        '../data/rpontes_rh.db'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path} ({size} bytes)")
        else:
            print(f"[ERRO] {file_path} - ARQUIVO FALTANDO")
    
    # 2. Verificar banco de dados
    print("\nVERIFICANDO BANCO DE DADOS")
    print("-" * 30)
    
    try:
        db = Database()
        print("[OK] Conexão com banco estabelecida")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Tabelas encontradas: {tables}")
            
            # Contar registros
            for table in ['usuarios', 'ferias']:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"{table}: {count} registros")
    
    except Exception as e:
        print(f"[ERRO] Erro no banco: {str(e)}")
    
    # 3. Verificar usuários
    print("\nVERIFICANDO USUARIOS")
    print("-" * 30)
    
    try:
        users = db.get_users()
        print(f"Total de usuarios: {len(users)}")
        
        if not users.empty:
            print("\nDetalhes dos usuarios:")
            for _, user in users.iterrows():
                print(f"  ID: {user['id']} | {user['nome']} | {user['email']} | Saldo: {user['saldo_ferias']}")
                
                # Verificar férias de cada usuário
                ferias = db.get_ferias_usuario(user['id'])
                if not ferias.empty:
                    total_dias = ferias['dias_utilizados'].sum()
                    print(f"    └─ Férias: {len(ferias)} períodos, {total_dias} dias utilizados")
    
    except Exception as e:
        print(f"[ERRO] Erro ao verificar usuários: {str(e)}")
    
    # 4. Verificar configurações
    print("\nVERIFICANDO CONFIGURACOES")
    print("-" * 30)
    
    try:
        from config import SETORES, NIVEIS_ACESSO, DIAS_FERIAS_PADRAO
        print(f"[OK] DIAS_FERIAS_PADRAO: {DIAS_FERIAS_PADRAO}")
        print(f"[OK] Setores configurados: {len(SETORES)}")
        print(f"[OK] Níveis de acesso: {len(NIVEIS_ACESSO)}")
    except Exception as e:
        print(f"[ERRO] Erro nas configurações: {str(e)}")
    
    # 5. Verificar imports
    print("\nVERIFICANDO IMPORTS")
    print("-" * 30)
    
    modules_to_test = [
        'database',
        'auth', 
        'menus',
        'config',
        'utils.validators',
        'utils.ui_components'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[ERRO] {module}: {str(e)}")
    
    # 6. Teste rápido de funcionalidade
    print("\nTESTE RAPIDO DE FUNCIONALIDADE")
    print("-" * 30)
    
    try:
        # Teste de autenticação
        user = db.authenticate_user("admin@rpontes.com", "admin123")
        if user:
            print("[OK] Autenticação funcionando")
        else:
            print("[ERRO] Falha na autenticação")
        
        # Teste de validação
        from utils.validators import validate_email
        if validate_email("test@example.com"):
            print("[OK] Validadores funcionando")
        else:
            print("[ERRO] Falha nos validadores")
    
    except Exception as e:
        print(f"[ERRO] Erro nos testes: {str(e)}")
    
    # 7. Verificar performance
    print("\nVERIFICANDO PERFORMANCE")
    print("-" * 30)
    
    import time
    
    try:
        start = time.time()
        users = db.get_users()
        end = time.time()
        
        query_time = end - start
        if query_time < 1.0:
            print(f"[OK] Performance adequada: {query_time:.3f}s para buscar usuários")
        else:
            print(f"[AVISO] Performance lenta: {query_time:.3f}s para buscar usuários")
    
    except Exception as e:
        print(f"[ERRO] Erro no teste de performance: {str(e)}")
    
    print("\n" + "=" * 50)
    print("DEBUG CONCLUIDO")

if __name__ == "__main__":
    debug_system()