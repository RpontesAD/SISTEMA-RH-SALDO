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
    "DIRETORIA",
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

APP_TITLE = "RPONTES - Sistema RH"
PAGE_LAYOUT = "wide"

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

# AVISO: Este arquivo contém configurações legadas
# Use config_secure.py para configurações com variáveis de ambiente

# Configurações MySQL - Sempre usar MySQL
USE_MYSQL = True  # Sistema usa apenas MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "sistema_ferias_rh"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""  # REMOVIDO - use variável de ambiente MYSQL_PASSWORD