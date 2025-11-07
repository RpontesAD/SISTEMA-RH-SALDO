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
    "Analista Administrativo",
    "Analista de Dados",
    "Analista de Suprimentos",
    "Analista Financeiro",
    "Analista Técnico",
    "Arquiteta",
    "Assistente",
    "Assistente de Marketing",
    "Assistente Técnico de Informática",
    "Auxiliar",
    "Consultor",
    "Coordenador",
    "Coordenador Comercial",
    "Coordenador de Projetos",
    "Coordenador Financeiro",
    "Coordenadora",
    "Diretor",
    "Diretor Engenharia",
    "Engenheiro Civil",
    "Estagiário",
    "Gerente",
    "Gerente Contábil Financeiro",
    "Gerente de Marketing",
    "Motorista",
    "Supervisor",
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