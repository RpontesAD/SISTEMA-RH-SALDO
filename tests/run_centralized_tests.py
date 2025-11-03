"""
Script para executar testes dos módulos centralizados
"""
import unittest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_centralized_tests():
    """Executa todos os testes dos módulos centralizados"""
    
    # Descobrir e executar testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes específicos dos módulos centralizados
    test_modules = [
        'tests.unit.test_constants',
        'tests.unit.test_validators', 
        'tests.unit.test_formatters'
    ]
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(module)
            suite.addTests(tests)
            print(f"OK Carregado: {module}")
        except Exception as e:
            print(f"ERRO ao carregar {module}: {e}")
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumo
    print(f"\n{'='*50}")
    print(f"RESUMO DOS TESTES CENTRALIZADOS")
    print(f"{'='*50}")
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("SUCESSO: TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("FALHA: ALGUNS TESTES FALHARAM!")
        return False

if __name__ == '__main__':
    success = run_centralized_tests()
    sys.exit(0 if success else 1)