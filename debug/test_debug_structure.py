#!/usr/bin/env python3
"""
Teste da Nova Estrutura de Debug
"""
import sys
import os

# Adicionar pasta debug ao path
debug_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(debug_dir)
sys.path.insert(0, parent_dir)

def test_imports():
    """Testa todas as importações do módulo debug"""
    print("[DEBUG] Testando Nova Estrutura de Debug")
    print("=" * 50)
    
    try:
        # Teste 1: Import básico
        print("1. Testando import básico...")
        from debug import logger
        print("   [OK] logger importado")
        
        # Teste 2: Import de classes
        print("2. Testando classes de debug...")
        from debug import DebugManager, DatabaseDebugger, AuthDebugger
        print("   [OK] Classes de debug importadas")
        
        # Teste 3: Import de decorators
        print("3. Testando decorators...")
        from debug import debug_decorator, debug_streamlit_component
        print("   [OK] Decorators importados")
        
        # Teste 4: Import de painel
        print("4. Testando painel visual...")
        from debug import show_debug_panel, add_debug_to_page
        print("   [OK] Painel visual importado")
        
        # Teste 5: Import de configurações
        print("5. Testando configurações...")
        from debug import get_debug_setting, set_debug_setting, is_debug_enabled
        print("   [OK] Configuracoes importadas")
        
        # Teste 6: Funcionalidade básica
        print("6. Testando funcionalidade...")
        logger.info("Teste de log funcionando!")
        
        debug_enabled = is_debug_enabled()
        print(f"   [OK] Debug habilitado: {debug_enabled}")
        
        log_level = get_debug_setting("LOG_LEVEL", "INFO")
        print(f"   [OK] Nivel de log: {log_level}")
        
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM!")
        print("[OK] A nova estrutura de debug esta funcionando perfeitamente!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_decorator():
    """Testa o decorator de debug"""
    print("\n7. Testando decorator...")
    
    try:
        from debug import debug_decorator
        
        @debug_decorator()
        def funcao_teste():
            return "Resultado do teste"
        
        resultado = funcao_teste()
        print(f"   [OK] Decorator funcionando: {resultado}")
        
    except Exception as e:
        print(f"   [ERROR] Erro no decorator: {e}")

def show_structure():
    """Mostra a estrutura da pasta debug"""
    print("\n[FOLDER] Estrutura da Pasta Debug:")
    print("-" * 30)
    
    debug_dir = os.path.dirname(__file__)
    for item in sorted(os.listdir(debug_dir)):
        if item.endswith('.py'):
            print(f"[PY] {item}")
        elif item.endswith('.md'):
            print(f"[MD] {item}")
        else:
            print(f"[FILE] {item}")

if __name__ == "__main__":
    success = test_imports()
    test_decorator()
    show_structure()
    
    if success:
        print("\n[SUCCESS] Sistema de debug reorganizado com sucesso!")
        print("[INFO] Localizacao: pasta 'debug/'")
        print("[INFO] Documentacao: debug/README.md")
    else:
        print("\n[WARNING] Alguns testes falharam. Verifique os erros acima.")