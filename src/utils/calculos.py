"""
Utilitários de Cálculo - Funções puras para cálculos de férias

Este módulo contém funções utilitárias para cálculos relacionados a férias,
sem dependências de interface ou banco de dados.
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import pandas as pd


def calcular_dias_uteis(data_inicio: date, data_fim: date) -> int:
    """
    Calcula dias úteis entre duas datas (segunda a sexta).
    
    Args:
        data_inicio: Data de início
        data_fim: Data de fim
        
    Returns:
        Número de dias úteis
    """
    if data_fim < data_inicio:
        return 0
    
    dias_uteis = 0
    current_date = data_inicio
    
    while current_date <= data_fim:
        # 0-4 = segunda a sexta
        if current_date.weekday() < 5:
            dias_uteis += 1
        current_date += timedelta(days=1)
    
    return dias_uteis


def calcular_dias_com_feriados(data_inicio: date, data_fim: date, feriados: List[date] = None) -> Dict[str, Any]:
    """
    Calcula dias úteis descontando feriados.
    
    Args:
        data_inicio: Data de início
        data_fim: Data de fim
        feriados: Lista de datas de feriados
        
    Returns:
        Dict com detalhes do cálculo
    """
    if feriados is None:
        feriados = []
    
    total_dias = (data_fim - data_inicio).days + 1
    dias_uteis_brutos = calcular_dias_uteis(data_inicio, data_fim)
    
    # Contar feriados que caem em dias úteis
    feriados_uteis = 0
    for feriado in feriados:
        if data_inicio <= feriado <= data_fim and feriado.weekday() < 5:
            feriados_uteis += 1
    
    dias_finais = max(0, dias_uteis_brutos - feriados_uteis)
    
    return {
        "total_dias": total_dias,
        "dias_uteis_brutos": dias_uteis_brutos,
        "feriados_uteis": feriados_uteis,
        "dias_finais": dias_finais,
        "fins_semana": total_dias - dias_uteis_brutos
    }


def calcular_antecedencia(data_inicio: date, data_referencia: date = None) -> int:
    """
    Calcula dias de antecedência entre data de referência e início.
    
    Args:
        data_inicio: Data de início das férias
        data_referencia: Data de referência (padrão: hoje)
        
    Returns:
        Número de dias de antecedência
    """
    if data_referencia is None:
        data_referencia = date.today()
    
    return (data_inicio - data_referencia).days


def formatar_periodo_ferias(data_inicio: date, data_fim: date) -> str:
    """
    Formata período de férias para exibição.
    
    Args:
        data_inicio: Data de início
        data_fim: Data de fim
        
    Returns:
        String formatada do período
    """
    from .security import sanitize_html
    
    inicio_str = data_inicio.strftime('%d/%m/%Y')
    fim_str = data_fim.strftime('%d/%m/%Y')
    
    return sanitize_html(f"{inicio_str} a {fim_str}")


def calcular_proximo_aniversario_admissao(data_admissao: date, data_referencia: date = None) -> date:
    """
    Calcula próximo aniversário de admissão para renovação de saldo.
    
    Args:
        data_admissao: Data de admissão do colaborador
        data_referencia: Data de referência (padrão: hoje)
        
    Returns:
        Data do próximo aniversário de admissão
    """
    if data_referencia is None:
        data_referencia = date.today()
    
    # Próximo aniversário no ano atual
    proximo_aniversario = data_admissao.replace(year=data_referencia.year)
    
    # Se já passou, calcular para o próximo ano
    if proximo_aniversario <= data_referencia:
        proximo_aniversario = proximo_aniversario.replace(year=data_referencia.year + 1)
    
    return proximo_aniversario