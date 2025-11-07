"""
Constantes centralizadas do sistema - Elimina duplicações
"""

# Configurações de Saldo
SALDO_MINIMO = 0
SALDO_MAXIMO = 30
DIAS_FERIAS_PADRAO = 12

# Antecedência
DIAS_ANTECEDENCIA_MINIMA = 7

# Setores
SETORES = [
    "ADMINISTRAÇÃO",
    "ASSISTÊNCIA TÉCNICA",
    "GESTÃO DE PESSOAS",
    "FINANCEIRO",
    "SUPRIMENTO",
    "ENGENHARIA",
    "MARKETING",
    "TI",
    "ANÁLISE DE DADOS",
    "COMERCIAL",
    "DIRETORIA",
]

# Funções
FUNCOES = [
    "Analista",
    "Assistente",
    "Auxiliar",
    "Coordenador",
    "Diretor",
    "Estagiário",
    "Gerente",
    "Supervisor",
    "Consultor",
]

# Status de Férias
STATUS_FERIAS = {
    "APROVADA": "Aprovada",
    "PENDENTE": "Pendente",
    "CANCELADA": "Cancelada",
    "REJEITADA": "Rejeitada",
}

STATUS_FERIAS_OPTIONS = list(STATUS_FERIAS.values())

# Níveis de Acesso
NIVEIS_ACESSO = {
    "master": "RH - Acesso Total",
    "diretoria": "Diretoria - Relatórios Executivos",
    "coordenador": "Coordenador - Gestão do Setor",
    "colaborador": "Colaborador - Visualização Pessoal",
}