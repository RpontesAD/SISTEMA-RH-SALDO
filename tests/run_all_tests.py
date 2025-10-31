import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    """Executa todos os testes do sistema"""
    print("EXECUTANDO TODOS OS TESTES DO SISTEMA RPONTES RH")
    print("=" * 60)
    
    tests = [
        ("test_auth", "Autenticação"),
        ("test_validators", "Validadores"),
        ("test_crud_users", "CRUD Usuários"),
        ("test_ferias_operations", "Operações de Férias"),
        ("test_database_integrity", "Integridade do Banco"),
        ("test_logica", "Lógica de Férias"),
        ("test_add_ferias", "Função Add Férias")
    ]
    
    results = []
    
    for test_file, test_name in tests:
        print(f"\nExecutando: {test_name}")
        print("-" * 40)
        
        try:
            # Importar e executar o teste
            if test_file == "test_auth":
                from test_auth import test_authentication
                test_authentication()
            elif test_file == "test_validators":
                from test_validators import test_validators
                test_validators()
            elif test_file == "test_crud_users":
                from test_crud_users import test_crud_users
                test_crud_users()
            elif test_file == "test_ferias_operations":
                from test_ferias_operations import test_ferias_operations
                test_ferias_operations()
            elif test_file == "test_database_integrity":
                from test_database_integrity import test_database_integrity
                test_database_integrity()
            elif test_file == "test_logica":
                exec(open(os.path.join(os.path.dirname(__file__), 'test_logica.py')).read())
            elif test_file == "test_add_ferias":
                exec(open(os.path.join(os.path.dirname(__file__), 'test_add_ferias.py')).read())
            
            results.append((test_name, "[OK] PASSOU"))
            
        except Exception as e:
            results.append((test_name, f"[ERRO] FALHOU: {str(e)}"))
            print(f"[ERRO] ERRO: {str(e)}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        print(f"{result:<20} {test_name}")
        if "PASSOU" in result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"[OK] Testes que passaram: {passed}")
    print(f"[ERRO] Testes que falharam: {failed}")
    print(f"Taxa de sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
    else:
        print(f"\n[AVISO] {failed} teste(s) falharam. Verifique os erros acima.")

if __name__ == "__main__":
    run_all_tests()