"""
Constantes de Negócio - Valores fixos das regras de negócio

Este módulo centraliza todas as constantes relacionadas às regras de negócio,
separadas das configurações técnicas do sistema.
"""

# Setores da empresa
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

# Funções disponíveis
FUNCOES = [
    "Analista",
    "Assistente", 
    "Auxiliar",
    "Coordenador",
    "Diretor", 
    "Estagiário",
    "Gerente",
    "RH",
    "Supervisor",
    "Técnico",
]

# Níveis de acesso do sistema
NIVEIS_ACESSO = {
    "master": "RH - Acesso Total",
    "diretoria": "Diretoria - Relatórios Executivos", 
    "coordenador": "Coordenador - Gestão do Setor",
    "colaborador": "Colaborador - Visualização Pessoal",
}

# Regras de férias
DIAS_FERIAS_PADRAO = 12
SALDO_MINIMO = 0
SALDO_MAXIMO = 12
DIAS_ANTECEDENCIA_MINIMA = 7
PERIODO_MAXIMO_DIAS = 30
CONSIDERAR_FERIADOS = True

# Status de férias
STATUS_FERIAS = {
    "APROVADA": "Aprovada",
    "PENDENTE": "Pendente", 
    "CANCELADA": "Cancelada",
    "REJEITADA": "Rejeitada",
}

STATUS_FERIAS_OPTIONS = list(STATUS_FERIAS.values())