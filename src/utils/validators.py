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
    nome = nome.strip()
    
    if len(nome) < 2:
        return False, "Nome deve ter pelo menos 2 caracteres"
    
    # Verificar se contém números
    if any(char.isdigit() for char in nome):
        return False, "Nome não pode conter números"
    
    # Verificar se está todo em maiúsculas (exceto abreviações de 1-2 letras)
    palavras = nome.split()
    for palavra in palavras:
        if len(palavra) > 2 and palavra.isupper():
            return False, "Nome não pode estar todo em maiúsculas"
    
    return True, "Nome válido"

