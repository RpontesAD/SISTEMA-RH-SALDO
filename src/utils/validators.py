"""
Validadores centralizados - Elimina duplicações de validação
"""
import re
from typing import Tuple

def validar_email(email: str) -> bool:
    """Validação única de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validar_senha(senha: str) -> Tuple[bool, str]:
    """Validação única de senha"""
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    return True, "Senha válida"

def validar_nome(nome: str) -> Tuple[bool, str]:
    """Validação única de nome"""
    if len(nome.strip()) < 2:
        return False, "Nome deve ter pelo menos 2 caracteres"
    return True, "Nome válido"