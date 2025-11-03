# Constantes movidas para utils/constants.py
from .utils.constants import SETORES, FUNCOES, NIVEIS_ACESSO, DIAS_FERIAS_PADRAO, SALDO_MINIMO, SALDO_MAXIMO

APP_TITLE = "RPONTES - Sistema RH"
PAGE_LAYOUT = "wide"

# Valores movidos para utils/constants.py  

DIAS_ANTECEDENCIA_MINIMA = 30
CONSIDERAR_FERIADOS = True

# Status movidos para utils/constants.py

# AVISO: Este arquivo contém configurações legadas
# Use config_secure.py para configurações com variáveis de ambiente

# Configurações MySQL - Sempre usar MySQL
USE_MYSQL = True  # Sistema usa apenas MySQL
MYSQL_HOST = "localhost"  # Será sobrescrito por variável de ambiente
MYSQL_PORT = 3306
MYSQL_DATABASE = "sistema_ferias_rh"
MYSQL_USER = "root"  # Será sobrescrito por variável de ambiente
MYSQL_PASSWORD = ""  # OBRIGATÓRIO - use variável de ambiente MYSQL_PASSWORD