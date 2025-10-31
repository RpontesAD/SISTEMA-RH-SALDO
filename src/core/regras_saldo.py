"""
Regras de Negócio para Saldo - Lógica pura sem interface

Este módulo contém apenas a lógica relacionada ao controle de saldos,
sem dependências de interface ou banco de dados.
"""

from typing import Dict, Any


class RegrasSaldo:
    """
    Classe que implementa as regras de negócio para saldos de férias.
    
    Centraliza toda a lógica de validação e cálculo de saldos,
    garantindo consistência em todo o sistema.
    """
    
    # Constantes das regras de saldo
    SALDO_PADRAO = 12  # Valor padrão personalizável
    SALDO_MINIMO = 0
    SALDO_MAXIMO = 30  # Período máximo de 30 dias
    
    @classmethod
    def validar_saldo_dentro_limites(cls, saldo: int) -> Dict[str, Any]:
        """
        Valida se o saldo está dentro dos limites permitidos.
        
        Args:
            saldo: Valor do saldo a ser validado
            
        Returns:
            Dict com resultado da validação
        """
        if saldo < cls.SALDO_MINIMO:
            return {
                "valido": False,
                "motivo": "saldo_abaixo_minimo",
                "saldo_corrigido": cls.SALDO_MINIMO,
                "mensagem": f"Saldo abaixo do mínimo ({cls.SALDO_MINIMO})"
            }
        
        if saldo > cls.SALDO_MAXIMO:
            return {
                "valido": False,
                "motivo": "saldo_acima_maximo", 
                "saldo_corrigido": cls.SALDO_MAXIMO,
                "mensagem": f"Saldo acima do máximo ({cls.SALDO_MAXIMO})"
            }
        
        return {
            "valido": True,
            "saldo_corrigido": saldo,
            "mensagem": "Saldo dentro dos limites"
        }
    
    @classmethod
    def calcular_saldo_teorico(cls, ferias_aprovadas: list) -> int:
        """
        Calcula o saldo teórico baseado nas férias aprovadas.
        
        Args:
            ferias_aprovadas: Lista de férias com status "Aprovada"
            
        Returns:
            Saldo teórico calculado
        """
        total_usado = sum(ferias.get("dias_utilizados", 0) for ferias in ferias_aprovadas)
        saldo_teorico = cls.SALDO_PADRAO - total_usado
        
        # Garantir que não seja negativo
        return max(cls.SALDO_MINIMO, saldo_teorico)
    
    @classmethod
    def detectar_inconsistencia_saldo(cls, saldo_atual: int, ferias_aprovadas: list) -> Dict[str, Any]:
        """
        Detecta inconsistências entre saldo atual e férias aprovadas.
        
        Args:
            saldo_atual: Saldo atual no banco
            ferias_aprovadas: Lista de férias aprovadas
            
        Returns:
            Dict com informações sobre inconsistências
        """
        saldo_teorico = cls.calcular_saldo_teorico(ferias_aprovadas)
        diferenca = abs(saldo_atual - saldo_teorico)
        
        # Tolerância de 1 dia para pequenas diferenças
        if diferenca <= 1:
            return {
                "inconsistente": False,
                "saldo_atual": saldo_atual,
                "saldo_teorico": saldo_teorico,
                "diferenca": diferenca
            }
        
        return {
            "inconsistente": True,
            "saldo_atual": saldo_atual,
            "saldo_teorico": saldo_teorico,
            "diferenca": diferenca,
            "sugestao_correcao": saldo_teorico,
            "motivo": "Diferença significativa entre saldo e férias aprovadas"
        }
    
    @classmethod
    def calcular_saldo_com_pendentes(cls, saldo_atual: int, ferias_pendentes: list) -> Dict[str, Any]:
        """
        Calcula saldo considerando férias pendentes de aprovação.
        
        Args:
            saldo_atual: Saldo atual do colaborador
            ferias_pendentes: Lista de férias pendentes
            
        Returns:
            Dict com cálculos de saldo
        """
        dias_pendentes = sum(ferias.get("dias_utilizados", 0) for ferias in ferias_pendentes)
        saldo_se_aprovadas = max(cls.SALDO_MINIMO, saldo_atual - dias_pendentes)
        
        return {
            "saldo_atual": saldo_atual,
            "dias_pendentes": dias_pendentes,
            "saldo_se_aprovadas": saldo_se_aprovadas,
            "tem_pendencias": dias_pendentes > 0,
            "saldo_suficiente_para_pendentes": saldo_atual >= dias_pendentes
        }
    
    @classmethod
    def validar_operacao_saldo(cls, saldo_atual: int, operacao: str, valor: int) -> Dict[str, Any]:
        """
        Valida se uma operação no saldo é permitida.
        
        Args:
            saldo_atual: Saldo atual
            operacao: Tipo de operação ("adicionar", "subtrair", "definir")
            valor: Valor da operação
            
        Returns:
            Dict com resultado da validação
        """
        if operacao == "adicionar":
            novo_saldo = saldo_atual + valor
        elif operacao == "subtrair":
            novo_saldo = saldo_atual - valor
        elif operacao == "definir":
            novo_saldo = valor
        else:
            return {
                "permitida": False,
                "motivo": f"Operação inválida: {operacao}"
            }
        
        validacao = cls.validar_saldo_dentro_limites(novo_saldo)
        
        if not validacao["valido"]:
            return {
                "permitida": False,
                "saldo_atual": saldo_atual,
                "saldo_pretendido": novo_saldo,
                "motivo": validacao["mensagem"],
                "saldo_corrigido": validacao["saldo_corrigido"]
            }
        
        return {
            "permitida": True,
            "saldo_atual": saldo_atual,
            "novo_saldo": novo_saldo,
            "operacao": operacao,
            "valor": valor
        }