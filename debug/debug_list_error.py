#!/usr/bin/env python3
"""
Script para debugar o erro 'name List is not defined'
"""
import sys
import os
import traceback

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa importacoes uma por uma para identificar o problema"""
    
    print("=== DEBUG: Testando importacoes ===")
    
    try:
        print("1. Testando typing...")
        from typing import Dict, Any
        print("   [OK] typing OK")
    except Exception as e:
        print(f"   [ERRO] Erro em typing: {e}")
        traceback.print_exc()
        return
    
    try:
        print("2. Testando core.regras_saldo...")
        from src.core.regras_saldo import RegrasSaldo
        print("   [OK] regras_saldo OK")
    except Exception as e:
        print(f"   [ERRO] Erro em regras_saldo: {e}")
        traceback.print_exc()
        return
    
    try:
        print("3. Testando utils.code_standards...")
        from src.utils.code_standards import Constantes
        print("   [OK] code_standards OK")
    except Exception as e:
        print(f"   [ERRO] Erro em code_standards: {e}")
        traceback.print_exc()
        return
    
    try:
        print("4. Testando database.connection...")
        from src.database.connection import DatabaseConnection
        print("   [OK] connection OK")
    except Exception as e:
        print(f"   [ERRO] Erro em connection: {e}")
        traceback.print_exc()
        return
    
    try:
        print("5. Testando database.users...")
        from src.database.users import UserManager
        print("   [OK] users OK")
    except Exception as e:
        print(f"   [ERRO] Erro em users: {e}")
        traceback.print_exc()
        return
    
    try:
        print("6. Testando services.colaboradores_service...")
        from src.services.colaboradores_service import ColaboradoresService
        print("   [OK] colaboradores_service OK")
    except Exception as e:
        print(f"   [ERRO] Erro em colaboradores_service: {e}")
        traceback.print_exc()
        return
    
    try:
        print("7. Testando services.ferias_service...")
        from src.services.ferias_service import FeriasService
        print("   [OK] ferias_service OK")
    except Exception as e:
        print(f"   [ERRO] Erro em ferias_service: {e}")
        traceback.print_exc()
        return
    
    print("\n=== Todas as importacoes OK! ===")

def test_mysql_imports():
    """Testa importações específicas do MySQL"""
    print("\n=== Testando MySQL ===")
    
    try:
        print("1. Testando config_secure...")
        from src.config_secure import USE_MYSQL
        print(f"   [OK] USE_MYSQL = {USE_MYSQL}")
    except Exception as e:
        print(f"   [ERRO] Erro em config_secure: {e}")
        traceback.print_exc()
        return
    
    if USE_MYSQL:
        try:
            print("2. Testando mysql_database...")
            from src.database.mysql_database import MySQLDatabase
            print("   [OK] mysql_database OK")
        except Exception as e:
            print(f"   [ERRO] Erro em mysql_database: {e}")
            traceback.print_exc()

def simulate_app_initialization():
    """Simula a inicialização do app.py"""
    print("\n=== Simulando inicialização do app.py ===")
    
    try:
        # Simular as importações do app.py
        from src.config import (
            APP_TITLE, PAGE_LAYOUT, USE_MYSQL,
            MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
        )
        print("   [OK] Importacoes de config OK")
        
        if USE_MYSQL:
            from src.database.mysql_database import MySQLDatabase
            print("   [OK] MySQLDatabase importado")
        else:
            from src.database.connection import DatabaseConnection
            from src.database.users import UserManager
            from src.database.ferias import FeriasManager
            print("   [OK] SQLite imports OK")
        
        from src.app import main
        print("   [OK] main importado")
        
        print("\n=== Inicialização simulada com sucesso! ===")
        
    except Exception as e:
        print(f"   [ERRO] Erro na simulacao: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
    test_mysql_imports()
    simulate_app_initialization()