import sys
import os
import streamlit as st
import atexit
import traceback
import pandas as pd


pd.options.display.date_dayfirst = True



sys.path.append(os.path.join(os.path.dirname(__file__), 'codigo'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Tentar importar da nova estrutura primeiro, depois da antiga
try:
    from codigo.configuracao import (
        TITULO_APP as APP_TITLE, LAYOUT_PAGINA as PAGE_LAYOUT, USAR_MYSQL as USE_MYSQL,
        HOST_MYSQL as MYSQL_HOST, PORTA_MYSQL as MYSQL_PORT, BANCO_MYSQL as MYSQL_DATABASE, 
        USUARIO_MYSQL as MYSQL_USER, SENHA_MYSQL as MYSQL_PASSWORD
    )
except ImportError:
    try:
        from src.config_secure import (
            APP_TITLE, PAGE_LAYOUT, get_database_config
        )
        config = get_database_config()
        
        if config["type"] == "mysql":
            from src.config_secure import USE_MYSQL, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
        elif config["type"] == "sheets":
            from src.config_secure import USE_SHEETS
        else:
            from src.config_secure import USE_MYSQL, SQLITE_PATH
    except ImportError:
        from src.config import (
            APP_TITLE, PAGE_LAYOUT, USE_MYSQL, SQLITE_PATH
        )

# Configurar página e localização
st.set_page_config(page_title=APP_TITLE, layout=PAGE_LAYOUT)

# Configurar localização brasileira
import locale
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Manter padrão se não conseguir configurar



# Forçar recriação se houver problema com métodos
if "users_db" in st.session_state:
    try:
        # Testar se métodos de avisos existem
        if not hasattr(st.session_state.users_db, 'remover_aviso_usuario'):
            raise AttributeError("Método remover_aviso_usuario não encontrado")
        if not hasattr(st.session_state.users_db, 'get_matriz_leitura_avisos'):
            raise AttributeError("Método get_matriz_leitura_avisos não encontrado")
        # Testar conexão básica
        st.session_state.users_db.get_users(incluir_inativos=False)
    except (TypeError, AttributeError):
        # Limpar cache se houver erro
        if "db_conn" in st.session_state:
            del st.session_state.db_conn
        if "users_db" in st.session_state:
            del st.session_state.users_db
        if "ferias_db" in st.session_state:
            del st.session_state.ferias_db
        if "db" in st.session_state:
            del st.session_state.db
    except:
        # Outros erros são normais
        pass

# Inicializar banco de dados
if "db_conn" not in st.session_state:
    try:
        # Verificar tipo de banco
        config = get_database_config()
        
        if config["type"] == "sheets":
            # Usar database simples (PostgreSQL)
            from src.database import DatabaseManager
            st.session_state.db = DatabaseManager()
            
        elif config["type"] == "mysql":
            # Usar MySQL
            try:
                from codigo.banco_dados.mysql_database import MySQLDatabase
            except ImportError:
                from src.database.mysql_database import MySQLDatabase
            
            st.session_state.db = MySQLDatabase(
                MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
            )
            
        else:
            # Usar SQLite
            try:
                from codigo.banco_dados.sqlite_database import SQLiteDatabase
            except ImportError:
                from src.database.sqlite_database import SQLiteDatabase
            
            sqlite_path = SQLITE_PATH if 'SQLITE_PATH' in globals() else 'data/rpontes_rh.db'
            st.session_state.db = SQLiteDatabase(sqlite_path)
        
        # Criar interfaces compatíveis
        st.session_state.users_db = st.session_state.db
        st.session_state.ferias_db = st.session_state.db
        st.session_state.db_conn = st.session_state.db.connection
            
    except Exception as e:
        st.error(f"Erro ao inicializar banco de dados: {e}")
        st.write(f"Tipo de banco: {config.get('type', 'desconhecido')}")
        st.write(f"Diretório atual: {os.getcwd()}")
        st.stop()

# Importar e executar main após inicialização
try:
    from codigo.aplicacao import main
except ImportError:
    from src.app import main

if __name__ == "__main__":
    main()  