# Constantes movidas para utils/constants.py
from .utils.constants import SETORES, FUNCOES, NIVEIS_ACESSO, DIAS_FERIAS_PADRAO, SALDO_MINIMO, SALDO_MAXIMO

# Forçar SQLite
USE_MYSQL = False
SQLITE_PATH = "data/rpontes_rh.db"

APP_TITLE = "RPONTES - Sistema RH"
PAGE_LAYOUT = "wide"

# Valores movidos para utils/constants.py  

DIAS_ANTECEDENCIA_MINIMA = 30
CONSIDERAR_FERIADOS = True

# Status movidos para utils/constants.py

# AVISO: Este arquivo contém configurações legadas
# Use config_secure.py para configurações com variáveis de ambiente

# Forçar SQLite - NÃO usar MySQL
USE_MYSQL = False  # Sistema usa SQLite
SQLITE_PATH = "data/rpontes_rh.db"