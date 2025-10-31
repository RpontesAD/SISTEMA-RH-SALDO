"""
Script simplificado para executar testes automatizados
"""
import unittest
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_tests():
    """Executa todos os testes automatizados"""
    print("=" * 50)
    print("TESTES AUTOMATIZADOS - SISTEMA FERIAS RPONTES")
    print("=" * 50)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar testes unitários
    print("[UNIT] Executando testes unitarios...")
    loader = unittest.TestLoader()
    
    # Carregar testes unitários
    unit_dir = os.path.join(os.path.dirname(__file__), 'unit')
    unit_suite = loader.discover(unit_dir, pattern='test_*.py')
    
    # Carregar testes de cobertura
    coverage_dir = os.path.join(os.path.dirname(__file__), 'coverage')
    coverage_suite = loader.discover(coverage_dir, pattern='test_*.py')
    
    # Combinar suites
    combined_suite = unittest.TestSuite([unit_suite, coverage_suite])
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    total_tests = result.testsRun
    total_failures = len(result.failures)
    total_errors = len(result.errors)
    
    print(f"[TOTAL] {total_tests} testes executados")
    print(f"[FALHAS] {total_failures}")
    print(f"[ERROS] {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"\n[FAIL] {total_failures + total_errors} testes falharam.")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)