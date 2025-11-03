"""
Script de inicialização do banco de dados para deploy
"""
import os
import sys

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def init_database():
    """Inicializa o banco SQLite com usuário admin"""
    try:
        from src.database.sqlite_database import SQLiteDatabase
        
        # Criar diretório se não existir
        os.makedirs('data', exist_ok=True)
        
        # Inicializar banco
        db = SQLiteDatabase('data/rpontes_rh.db')
        print("Banco SQLite inicializado com sucesso!")
        print("Admin: admin@rpontes.com")
        print("Senha: admin123")
        
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        return False

if __name__ == "__main__":
    init_database()