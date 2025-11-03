"""
Regras de Negócio para Férias - Lógica pura sem interface

Este módulo contém apenas a lógica de negócio relacionada a férias,
sem dependências de interface ou banco de dados.
"""

from datetime import date, timedelta
from typing import Dict, Any, Tuple, Optional
from ..utils.constants import DIAS_ANTECEDENCIA_MINIMA, SALDO_MAXIMO, DIAS_FERIAS_PADRAO, SALDO_MINIMO


class RegrasFerias:
    """
    Classe que implementa as regras de negócio para férias.
    
    Todas as validações e cálculos relacionados a férias estão aqui,
    separados da interface e do acesso a dados.
    """
    
    # Constantes importadas do módulo constants
    PERIODO_MAXIMO_DIAS = SALDO_MAXIMO
    SALDO_PADRAO = DIAS_FERIAS_PADRAO
    
    @classmethod
    def validar_antecedencia(cls, data_inicio: date, usuario_nivel: str = "colaborador") -> Dict[str, Any]:
        """
        Valida se a antecedência mínima foi respeitada.
        
        Args:
            data_inicio: Data de início das férias
            usuario_nivel: Nível do usuário ("master" para RH)
            
        Returns:
            Dict com resultado da validação
        """
        hoje = date.today()
        dias_antecedencia = (data_inicio - hoje).days
        
        # RH pode cadastrar sem antecedência
        if usuario_nivel == "master":
            return {
                "valida": True,
                "dias_antecedencia": dias_antecedencia,
                "eh_rh": True,
                "mensagem": "RH pode cadastrar sem antecedência mínima"
            }
        
        # Validar antecedência para outros usuários
        valida = dias_antecedencia >= DIAS_ANTECEDENCIA_MINIMA
        
        return {
            "valida": valida,
            "dias_antecedencia": dias_antecedencia,
            "eh_rh": False,
            "mensagem": f"Antecedência mínima: {DIAS_ANTECEDENCIA_MINIMA} dias" if not valida else ""
        }
    
    @classmethod
    def validar_periodo(cls, data_inicio: date, data_fim: date) -> Dict[str, Any]:
        """
        Valida se o período de férias está dentro das regras.
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            Dict com resultado da validação
        """
        if data_fim < data_inicio:
            return {
                "valida": False,
                "mensagem": "Data de fim deve ser posterior à data de início"
            }
        
        dias_totais = (data_fim - data_inicio).days + 1
        
        if dias_totais > SALDO_MAXIMO:
            return {
                "valida": False,
                "mensagem": f"Período não pode exceder {SALDO_MAXIMO} dias"
            }
        
        return {
            "valida": True,
            "dias_totais": dias_totais,
            "mensagem": ""
        }
    
    @classmethod
    def validar_saldo_suficiente(cls, saldo_atual: int, dias_solicitados: int, status: str = "Aprovada") -> Dict[str, Any]:
        """
        Valida se o saldo é suficiente para as férias solicitadas.
        
        Args:
            saldo_atual: Saldo atual do colaborador
            dias_solicitados: Dias de férias solicitados
            status: Status das férias
            
        Returns:
            Dict com resultado da validação
        """
        # Férias pendentes podem ser cadastradas mesmo com saldo insuficiente
        if status != "Aprovada":
            return {
                "valida": True,
                "saldo_suficiente": saldo_atual >= dias_solicitados,
                "mensagem": "Férias pendentes - saldo será verificado na aprovação"
            }
        
        # Para férias aprovadas, saldo deve ser suficiente
        if saldo_atual < dias_solicitados:
            return {
                "valida": False,
                "saldo_suficiente": False,
                "mensagem": f"Saldo insuficiente. Disponível: {saldo_atual}, Solicitado: {dias_solicitados}"
            }
        
        return {
            "valida": True,
            "saldo_suficiente": True,
            "saldo_restante": saldo_atual - dias_solicitados,
            "mensagem": ""
        }
    
    @classmethod
    def calcular_impacto_mudanca_status(cls, status_atual: str, novo_status: str, dias_utilizados: int, saldo_atual: int) -> Dict[str, Any]:
        """
        Calcula o impacto de uma mudança de status no saldo.
        
        Args:
            status_atual: Status atual das férias
            novo_status: Novo status desejado
            dias_utilizados: Dias utilizados nas férias
            saldo_atual: Saldo atual do colaborador
            
        Returns:
            Dict com o impacto da mudança
        """
        if status_atual == novo_status:
            return {
                "altera_saldo": False,
                "novo_saldo": saldo_atual,
                "operacao": "sem_alteracao"
            }
        
        # Aprovação de férias pendentes
        if status_atual != "Aprovada" and novo_status == "Aprovada":
            if saldo_atual < dias_utilizados:
                return {
                    "altera_saldo": False,
                    "erro": f"Saldo insuficiente para aprovação. Disponível: {saldo_atual}, Necessário: {dias_utilizados}"
                }
            
            return {
                "altera_saldo": True,
                "novo_saldo": saldo_atual - dias_utilizados,
                "operacao": "desconto",
                "dias_afetados": dias_utilizados
            }
        
        # Cancelamento de férias aprovadas
        if status_atual == "Aprovada" and novo_status in ["Pendente", "Cancelada", "Rejeitada"]:
            novo_saldo = saldo_atual + dias_utilizados
            
            if novo_saldo > SALDO_MAXIMO:
                return {
                    "altera_saldo": False,
                    "erro": f"Operação resultaria em saldo acima do máximo ({SALDO_MAXIMO})"
                }
            
            return {
                "altera_saldo": True,
                "novo_saldo": novo_saldo,
                "operacao": "devolucao",
                "dias_afetados": dias_utilizados
            }
        
        # Outras mudanças não afetam saldo
        return {
            "altera_saldo": False,
            "novo_saldo": saldo_atual,
            "operacao": "sem_impacto_saldo"
        }