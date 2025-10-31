"""
Utilitários de Segurança - Prevenção de XSS e sanitização
"""
import html
import re
from typing import Any, Dict, List, Union

def sanitize_html(text: str) -> str:
    """
    Sanitiza texto removendo HTML perigoso.
    
    Args:
        text: Texto a ser sanitizado
        
    Returns:
        Texto sanitizado
    """
    if not isinstance(text, str):
        return str(text)
    
    # Escapar caracteres HTML
    sanitized = html.escape(text)
    
    # Remover scripts e tags perigosas
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'onmouseover='
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza todos os valores string de um dicionário.
    
    Args:
        data: Dicionário a ser sanitizado
        
    Returns:
        Dicionário sanitizado
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        else:
            sanitized[key] = value
    return sanitized

def sanitize_list(data: List[Any]) -> List[Any]:
    """
    Sanitiza todos os valores string de uma lista.
    
    Args:
        data: Lista a ser sanitizada
        
    Returns:
        Lista sanitizada
    """
    sanitized = []
    for item in data:
        if isinstance(item, str):
            sanitized.append(sanitize_html(item))
        elif isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        elif isinstance(item, list):
            sanitized.append(sanitize_list(item))
        else:
            sanitized.append(item)
    return sanitized

def validate_input(text: str, max_length: int = 1000, allow_html: bool = False) -> bool:
    """
    Valida entrada do usuário.
    
    Args:
        text: Texto a ser validado
        max_length: Comprimento máximo
        allow_html: Se permite HTML
        
    Returns:
        True se válido, False caso contrário
    """
    if not isinstance(text, str):
        return False
    
    if len(text) > max_length:
        return False
    
    if not allow_html:
        # Verificar se contém HTML
        html_pattern = r'<[^>]+>'
        if re.search(html_pattern, text):
            return False
    
    return True

def safe_format_html(template: str, **kwargs) -> str:
    """
    Formata HTML de forma segura, sanitizando variáveis.
    
    Args:
        template: Template HTML
        **kwargs: Variáveis para substituição
        
    Returns:
        HTML formatado e seguro
    """
    # Sanitizar todas as variáveis
    safe_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            safe_kwargs[key] = sanitize_html(value)
        else:
            safe_kwargs[key] = value
    
    return template.format(**safe_kwargs)