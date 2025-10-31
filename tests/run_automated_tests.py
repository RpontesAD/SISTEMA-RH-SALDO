"""
Script para executar todos os testes automatizados
"""
import unittest
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    """Executa todos os testes automatizados"""
    print("=" * 60)
    print("EXECUTANDO TESTES AUTOMATIZADOS - SISTEMA FÉRIAS RPONTES")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Descobrir e executar todos os testes
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    
    # Carregar testes unitários
    print("[UNIT] TESTES UNITARIOS")
    print("-" * 30)
    unit_suite = loader.discover(os.path.join(start_dir, 'unit'), pattern='test_*.py')
    unit_runner = unittest.TextTestRunner(verbosity=2)
    unit_result = unit_runner.run(unit_suite)
    
    print("\n[INTEGRATION] TESTES DE INTEGRACAO")
    print("-" * 30)
    integration_suite = loader.discover(os.path.join(start_dir, 'integration'), pattern='test_*.py')
    integration_runner = unittest.TextTestRunner(verbosity=2)
    integration_result = integration_runner.run(integration_suite)
    
    print("\n[COVERAGE] TESTES DE COBERTURA (REGRAS CRITICAS)")
    print("-" * 30)
    coverage_suite = loader.discover(os.path.join(start_dir, 'coverage'), pattern='test_*.py')
    coverage_runner = unittest.TextTestRunner(verbosity=2)
    coverage_result = coverage_runner.run(coverage_suite)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = (unit_result.testsRun + 
                  integration_result.testsRun + 
                  coverage_result.testsRun)
    
    total_failures = (len(unit_result.failures) + 
                     len(integration_result.failures) + 
                     len(coverage_result.failures))
    
    total_errors = (len(unit_result.errors) + 
                   len(integration_result.errors) + 
                   len(coverage_result.errors))
    
    print(f"[OK] Testes Unitarios: {unit_result.testsRun} executados")
    print(f"   - Falhas: {len(unit_result.failures)}")
    print(f"   - Erros: {len(unit_result.errors)}")
    
    print(f"[OK] Testes Integracao: {integration_result.testsRun} executados")
    print(f"   - Falhas: {len(integration_result.failures)}")
    print(f"   - Erros: {len(integration_result.errors)}")
    
    print(f"[OK] Testes Cobertura: {coverage_result.testsRun} executados")
    print(f"   - Falhas: {len(coverage_result.failures)}")
    print(f"   - Erros: {len(coverage_result.errors)}")
    
    print(f"\n[TOTAL] {total_tests} testes executados")
    print(f"[FALHAS] {total_failures}")
    print(f"[ERROS] {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM! Sistema validado.")
        return True
    else:
        print(f"\n[FAIL] {total_failures + total_errors} testes falharam. Revisar implementacao.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)