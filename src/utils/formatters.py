"""
Formatadores centralizados - Elimina duplicações de formatação
"""
from datetime import datetime

def formatar_data_brasileira(data) -> str:
    """Formatação única para datas brasileiras"""
    if hasattr(data, 'strftime'):
        return data.strftime('%d/%m/%Y')
    if isinstance(data, str):
        try:
            dt = datetime.strptime(data, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except:
            return str(data)
    return str(data)

def formatar_saldo_ferias(saldo: int) -> str:
    """Formatação única para saldo de férias"""
    return "1 dia" if saldo == 1 else f"{saldo} dias"