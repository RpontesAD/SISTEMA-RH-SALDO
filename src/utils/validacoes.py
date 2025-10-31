"""
Utilitários de Validação - Validações básicas de dados

Este módulo contém validações simples de dados,
sem regras de negócio complexas (que ficam em core/).
"""

import re
from datetime import date, datetime
from typing import Tuple, Any


def validar_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email.strip()) is not None


def validar_senha(senha: str) -> Tuple[bool, str]:
    """
    Valida força da senha.
    
    Args:
        senha: Senha a ser validada
        
    Returns:
        Tupla (válida, mensagem)
    """
    if not senha:
        return False, "Senha é obrigatória"
    
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    return True, ""


def validar_nome(nome: str) -> Tuple[bool, str]:
    """
    Valida nome de pessoa.
    
    Args:
        nome: Nome a ser validado
        
    Returns:
        Tupla (válido, mensagem)
    """
    if not nome or not nome.strip():
        return False, "Nome é obrigatório"
    
    nome = nome.strip()
    
    if len(nome) < 2:
        return False, "Nome deve ter pelo menos 2 caracteres"
    
    if len(nome) > 100:
        return False, "Nome não pode exceder 100 caracteres"
    
    return True, ""


def validar_data(data_input: Any) -> Tuple[bool, str, date]:
    """
    Valida e converte entrada de data.
    
    Args:
        data_input: Data em vários formatos
        
    Returns:
        Tupla (válida, mensagem, data_convertida)
    """
    if data_input is None:
        return False, "Data é obrigatória", None
    
    # Se já é date
    if isinstance(data_input, date):
        return True, "", data_input
    
    # Se é string, tentar converter
    if isinstance(data_input, str):
        try:
            # Formato ISO (YYYY-MM-DD)
            data_convertida = datetime.strptime(data_input, "%Y-%m-%d").date()
            return True, "", data_convertida
        except ValueError:
            try:
                # Formato brasileiro (DD/MM/YYYY)
                data_convertida = datetime.strptime(data_input, "%d/%m/%Y").date()
                return True, "", data_convertida
            except ValueError:
                return False, "Formato de data inválido", None
    
    return False, "Tipo de data não suportado", None


def validar_numero_inteiro(valor: Any, minimo: int = None, maximo: int = None) -> Tuple[bool, str, int]:
    """
    Valida e converte número inteiro.
    
    Args:
        valor: Valor a ser validado
        minimo: Valor mínimo permitido
        maximo: Valor máximo permitido
        
    Returns:
        Tupla (válido, mensagem, valor_convertido)
    """
    try:
        numero = int(valor)
        
        if minimo is not None and numero < minimo:
            return False, f"Valor deve ser maior ou igual a {minimo}", None
        
        if maximo is not None and numero > maximo:
            return False, f"Valor deve ser menor ou igual a {maximo}", None
        
        return True, "", numero
        
    except (ValueError, TypeError):
        return False, "Valor deve ser um número inteiro", None


def validar_texto_obrigatorio(texto: str, nome_campo: str = "Campo") -> Tuple[bool, str]:
    """
    Valida texto obrigatório.
    
    Args:
        texto: Texto a ser validado
        nome_campo: Nome do campo para mensagem de erro
        
    Returns:
        Tupla (válido, mensagem)
    """
    if not texto or not texto.strip():
        return False, f"{nome_campo} é obrigatório"
    
    return True, ""


def validar_opcao_lista(valor: str, opcoes_validas: list, nome_campo: str = "Campo") -> Tuple[bool, str]:
    """
    Valida se valor está em lista de opções válidas.
    
    Args:
        valor: Valor a ser validado
        opcoes_validas: Lista de opções válidas
        nome_campo: Nome do campo para mensagem de erro
        
    Returns:
        Tupla (válido, mensagem)
    """
    if valor not in opcoes_validas:
        opcoes_str = ", ".join(opcoes_validas)
        return False, f"{nome_campo} deve ser uma das opções: {opcoes_str}"
    
    return True, ""