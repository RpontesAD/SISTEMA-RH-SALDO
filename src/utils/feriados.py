"""
Utilitários de Feriados - Cálculos e validações de feriados

Este módulo contém funções para trabalhar com feriados nacionais,
sem dependências de interface ou banco de dados.
"""

from datetime import date
from typing import List, Dict


def obter_feriados_nacionais(ano: int) -> List[date]:
    """
    Retorna lista de feriados nacionais fixos para um ano.
    
    Args:
        ano: Ano para obter os feriados
        
    Returns:
        Lista de datas dos feriados
    """
    feriados = [
        date(ano, 1, 1),   # Confraternização Universal
        date(ano, 4, 21),  # Tiradentes
        date(ano, 5, 1),   # Dia do Trabalhador
        date(ano, 9, 7),   # Independência do Brasil
        date(ano, 10, 12), # Nossa Senhora Aparecida
        date(ano, 11, 2),  # Finados
        date(ano, 11, 15), # Proclamação da República
        date(ano, 12, 25), # Natal
    ]
    
    return feriados


def obter_nome_feriado(data_feriado: date) -> str:
    """
    Retorna o nome do feriado para uma data.
    
    Args:
        data_feriado: Data do feriado
        
    Returns:
        Nome do feriado ou "Feriado Nacional" se não encontrado
    """
    feriados_nomes = {
        (1, 1): "Confraternização Universal",
        (4, 21): "Tiradentes",
        (5, 1): "Dia do Trabalhador", 
        (9, 7): "Independência do Brasil",
        (10, 12): "Nossa Senhora Aparecida",
        (11, 2): "Finados",
        (11, 15): "Proclamação da República",
        (12, 25): "Natal"
    }
    
    chave = (data_feriado.month, data_feriado.day)
    return feriados_nomes.get(chave, "Feriado Nacional")


def obter_feriados_no_periodo(data_inicio: date, data_fim: date) -> List[Dict]:
    """
    Retorna feriados que ocorrem em um período.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        
    Returns:
        Lista de dicionários com informações dos feriados
    """
    feriados_periodo = []
    
    # Obter anos do período
    anos = set()
    current_date = data_inicio
    while current_date <= data_fim:
        anos.add(current_date.year)
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    # Verificar feriados de cada ano
    for ano in anos:
        feriados_ano = obter_feriados_nacionais(ano)
        
        for feriado in feriados_ano:
            if data_inicio <= feriado <= data_fim:
                feriados_periodo.append({
                    'data': feriado,
                    'nome': obter_nome_feriado(feriado),
                    'dia_semana': feriado.weekday()  # 0=segunda, 6=domingo
                })
    
    return sorted(feriados_periodo, key=lambda x: x['data'])


def contar_feriados_periodo(data_inicio: date, data_fim: date) -> int:
    """
    Conta quantos feriados em dias úteis ocorrem no período.
    
    Args:
        data_inicio: Data de início
        data_fim: Data de fim
        
    Returns:
        Número de feriados em dias úteis
    """
    feriados = obter_feriados_no_periodo(data_inicio, data_fim)
    
    # Contar apenas feriados que caem em dias úteis (segunda a sexta)
    feriados_uteis = sum(1 for f in feriados if f['dia_semana'] < 5)
    
    return feriados_uteis


def eh_feriado(data: date) -> bool:
    """
    Verifica se uma data é feriado nacional.
    
    Args:
        data: Data a ser verificada
        
    Returns:
        True se for feriado, False caso contrário
    """
    feriados_ano = obter_feriados_nacionais(data.year)
    return data in feriados_ano


def proximo_feriado(data_referencia: date = None) -> Dict:
    """
    Encontra o próximo feriado a partir de uma data.
    
    Args:
        data_referencia: Data de referência (padrão: hoje)
        
    Returns:
        Dicionário com informações do próximo feriado
    """
    if data_referencia is None:
        data_referencia = date.today()
    
    # Verificar feriados do ano atual
    feriados_ano_atual = obter_feriados_nacionais(data_referencia.year)
    
    for feriado in feriados_ano_atual:
        if feriado > data_referencia:
            return {
                'data': feriado,
                'nome': obter_nome_feriado(feriado),
                'dias_restantes': (feriado - data_referencia).days
            }
    
    # Se não encontrou no ano atual, pegar o primeiro do próximo ano
    feriados_proximo_ano = obter_feriados_nacionais(data_referencia.year + 1)
    primeiro_feriado = min(feriados_proximo_ano)
    
    return {
        'data': primeiro_feriado,
        'nome': obter_nome_feriado(primeiro_feriado),
        'dias_restantes': (primeiro_feriado - data_referencia).days
    }