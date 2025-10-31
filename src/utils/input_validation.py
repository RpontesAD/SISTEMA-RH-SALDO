"""
Validação de Entrada - Prevenção de XSS em formulários
"""
import streamlit as st
from .security import sanitize_html, validate_input
from typing import Optional, Union

def safe_text_input(label: str, value: str = "", max_chars: int = 100, key: Optional[str] = None, **kwargs) -> str:
    """
    Text input seguro com sanitização automática.
    
    Args:
        label: Label do campo
        value: Valor padrão
        max_chars: Máximo de caracteres
        key: Chave única
        **kwargs: Argumentos adicionais
        
    Returns:
        Texto sanitizado
    """
    raw_input = st.text_input(
        label=label, 
        value=value, 
        max_chars=max_chars, 
        key=key,
        **kwargs
    )
    
    return sanitize_html(raw_input)

def safe_text_area(label: str, value: str = "", max_chars: int = 500, key: Optional[str] = None, **kwargs) -> str:
    """
    Text area seguro com sanitização automática.
    
    Args:
        label: Label do campo
        value: Valor padrão
        max_chars: Máximo de caracteres
        key: Chave única
        **kwargs: Argumentos adicionais
        
    Returns:
        Texto sanitizado
    """
    raw_input = st.text_area(
        label=label, 
        value=value, 
        max_chars=max_chars, 
        key=key,
        **kwargs
    )
    
    return sanitize_html(raw_input)

def safe_selectbox(label: str, options: list, index: int = 0, key: Optional[str] = None, **kwargs) -> Union[str, int, float]:
    """
    Selectbox seguro com validação de opções.
    
    Args:
        label: Label do campo
        options: Lista de opções
        index: Índice padrão
        key: Chave única
        **kwargs: Argumentos adicionais
        
    Returns:
        Opção selecionada (sanitizada se for string)
    """
    # Sanitizar opções se forem strings
    safe_options = []
    for option in options:
        if isinstance(option, str):
            safe_options.append(sanitize_html(option))
        else:
            safe_options.append(option)
    
    selected = st.selectbox(
        label=label,
        options=safe_options,
        index=index,
        key=key,
        **kwargs
    )
    
    return selected

def validate_form_data(data: dict) -> dict:
    """
    Valida e sanitiza dados de formulário.
    
    Args:
        data: Dicionário com dados do formulário
        
    Returns:
        Dicionário com dados validados e sanitizados
    """
    validated_data = {}
    errors = []
    
    for field, value in data.items():
        if isinstance(value, str):
            # Validar comprimento
            if len(value) > 1000:
                errors.append(f"Campo '{field}' muito longo (máximo 1000 caracteres)")
                continue
            
            # Sanitizar
            validated_data[field] = sanitize_html(value)
        else:
            validated_data[field] = value
    
    if errors:
        for error in errors:
            st.error(error)
        return None
    
    return validated_data