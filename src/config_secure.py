"""
Configuração segura do sistema usando variáveis de ambiente
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações básicas do sistema
SETORES = [
    "ASSISTÊNCIA TÉCNICA",
    "GESTÃO DE PESSOAS (RH)",
    "FINANCEIRO",
    "SUPRIMENTO",
    "ENGENHARIA",
    "MARKETING",
    "TI",
    "ANÁLISE DE DADOS",
    "COMERCIAL",
    "RH",
]

FUNCOES = [
    "Analista",
    "Assistente",
    "Auxiliar",
    "Coordenador",
    "Diretor",
    "Gerente",
    "RH",
    "Supervisor",
    "Técnico",
]

NIVEIS_ACESSO = {
    "master": "RH - Acesso Total",
    "diretoria": "Diretoria - Relatórios Executivos",
    "coordenador": "Coordenador - Gestão do Setor",
    "colaborador": "Colaborador - Visualização Pessoal",
}

# Configurações da aplicação
APP_TITLE = os.getenv("APP_TITLE", "RPONTES - Sistema RH")
PAGE_LAYOUT = "wide"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Configurações de férias
DIAS_FERIAS_PADRAO = 12 
SALDO_MINIMO = 0  
SALDO_MAXIMO = 12  
DIAS_ANTECEDENCIA_MINIMA = 30
CONSIDERAR_FERIADOS = True

STATUS_FERIAS = {
    "APROVADA": "Aprovada",
    "PENDENTE": "Pendente",
    "CANCELADA": "Cancelada",
    "REJEITADA": "Rejeitada",
}

STATUS_FERIAS_OPTIONS = list(STATUS_FERIAS.values())

# Configurações seguras do banco de dados
# Detectar se está rodando no Streamlit Cloud
try:
    import streamlit as st
    # Tentar usar secrets do Streamlit Cloud
    try:
        if 'mysql' in st.secrets:
            USE_MYSQL = True
            MYSQL_HOST = st.secrets["mysql"]["host"]
            MYSQL_PORT = int(st.secrets["mysql"]["port"])
            MYSQL_DATABASE = st.secrets["mysql"]["database"]
            MYSQL_USER = st.secrets["mysql"]["user"]
            MYSQL_PASSWORD = st.secrets["mysql"]["password"]
        else:
            raise KeyError("mysql not in secrets")
    except (KeyError, FileNotFoundError, Exception):
        # Fallback para variáveis de ambiente
        USE_MYSQL = os.getenv("USE_MYSQL", "False").lower() == "true"
        MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "sistema_ferias_rh")
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
except ImportError:
    # Fallback se streamlit não estiver disponível
    USE_MYSQL = os.getenv("USE_MYSQL", "False").lower() == "true"
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "sistema_ferias_rh")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

# Configurações de segurança
try:
    import streamlit as st
    try:
        if 'app' in st.secrets:
            SECRET_KEY = st.secrets["app"]["secret_key"]
            ADMIN_EMAIL = st.secrets["app"]["admin_email"]
            ADMIN_PASSWORD = st.secrets["app"]["admin_password"]
        else:
            raise KeyError("app not in secrets")
    except (KeyError, FileNotFoundError, Exception):
        SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rpontes.com")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
except ImportError:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rpontes.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Validação de configurações críticas
def validate_config():
    """Valida se as configurações críticas estão definidas"""
    errors = []
    
    if USE_MYSQL and not MYSQL_PASSWORD:
        errors.append("MYSQL_PASSWORD não definida para conexão MySQL")
    
    if SECRET_KEY == "chave-padrao-insegura":
        errors.append("SECRET_KEY usando valor padrão inseguro")
    
    if ADMIN_PASSWORD == "admin123":
        errors.append("ADMIN_PASSWORD usando valor padrão inseguro")
    
    return errors

def get_database_config():
    """Retorna configuração do banco de dados"""
    if USE_MYSQL:
        return {
            "type": "mysql",
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "database": MYSQL_DATABASE,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD
        }
    else:
        return {
            "type": "sqlite",
            "path": "data/rpontes_rh.db"
        }