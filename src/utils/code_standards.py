"""
Padrões de Código - Utilitários para melhorar legibilidade e manutenibilidade
"""
from typing import Dict, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import functools

# Enums para valores constantes
class StatusFerias(Enum):
    APROVADA = "Aprovada"
    PENDENTE = "Pendente"
    CANCELADA = "Cancelada"
    REJEITADA = "Rejeitada"

class NivelAcesso(Enum):
    MASTER = "master"
    DIRETORIA = "diretoria"
    COORDENADOR = "coordenador"
    COLABORADOR = "colaborador"

class TipoOperacao(Enum):
    CADASTRO = "cadastro"
    EDICAO = "edicao_manual"
    APROVACAO = "aprovacao_ferias"
    CANCELAMENTO = "cancelamento_ferias"
    EXCLUSAO = "exclusao_ferias"
    CORRECAO = "correcao_automatica"

# Dataclasses para estruturas de dados
@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    setor: str
    funcao: str
    nivel_acesso: NivelAcesso
    saldo_ferias: int
    data_cadastro: Optional[str] = None
    data_admissao: Optional[str] = None

@dataclass
class Ferias:
    id: int
    usuario_id: int
    data_inicio: str
    data_fim: str
    dias_utilizados: int
    status: StatusFerias
    data_registro: Optional[str] = None

@dataclass
class ResultadoOperacao:
    sucesso: bool
    mensagem: str
    dados: Optional[Any] = None
    erro_codigo: Optional[str] = None

@dataclass
class ValidacaoResult:
    valido: bool
    mensagem: str
    detalhes: Optional[Dict] = None

# Constantes organizadas
class Constantes:
    # Limites de saldo
    SALDO_MINIMO = 0
    SALDO_MAXIMO = 12
    DIAS_FERIAS_PADRAO = 12
    
    # Antecedência
    DIAS_ANTECEDENCIA_MINIMA = 30
    
    # Validação
    TAMANHO_MINIMO_SENHA = 6
    TAMANHO_MINIMO_NOME = 2
    
    # Cache
    CACHE_TTL_USUARIOS = 60
    CACHE_TTL_FERIAS = 30
    
    # Performance
    LIMITE_QUERIES_LENTAS = 100  # ms
    LIMITE_QUERIES_MUITO_LENTAS = 1000  # ms

# Utilitários para validação
class Validadores:
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validar_senha(senha: str) -> ValidacaoResult:
        """Valida força da senha"""
        if len(senha) < Constantes.TAMANHO_MINIMO_SENHA:
            return ValidacaoResult(
                valido=False,
                mensagem=f"Senha deve ter pelo menos {Constantes.TAMANHO_MINIMO_SENHA} caracteres"
            )
        return ValidacaoResult(valido=True, mensagem="Senha válida")
    
    @staticmethod
    def validar_saldo(saldo: int) -> ValidacaoResult:
        """Valida saldo de férias"""
        if saldo < Constantes.SALDO_MINIMO:
            return ValidacaoResult(
                valido=False,
                mensagem=f"Saldo não pode ser menor que {Constantes.SALDO_MINIMO}"
            )
        if saldo > Constantes.SALDO_MAXIMO:
            return ValidacaoResult(
                valido=False,
                mensagem=f"Saldo não pode ser maior que {Constantes.SALDO_MAXIMO}"
            )
        return ValidacaoResult(valido=True, mensagem="Saldo válido")

# Decorators para melhorar legibilidade
def validar_parametros(**validacoes):
    """Decorator para validação automática de parâmetros"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validar parâmetros baseado nas validações definidas
            for param, validador in validacoes.items():
                if param in kwargs:
                    valor = kwargs[param]
                    if not validador(valor):
                        raise ValueError(f"Parâmetro '{param}' inválido: {valor}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def documentar_operacao(operacao: str, descricao: str):
    """Decorator para documentar operações importantes"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log da operação
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Iniciando {operacao}: {descricao}")
            
            try:
                resultado = func(*args, **kwargs)
                logger.info(f"Concluído {operacao}: sucesso")
                return resultado
            except Exception as e:
                logger.error(f"Erro em {operacao}: {e}")
                raise
        return wrapper
    return decorator

# Utilitários para formatação
class Formatadores:
    @staticmethod
    def formatar_data_brasileira(data_str: str) -> str:
        """Converte data para formato brasileiro"""
        from datetime import datetime
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
            return data.strftime('%d/%m/%Y')
        except:
            return data_str
    
    @staticmethod
    def formatar_periodo_ferias(data_inicio: str, data_fim: str) -> str:
        """Formata período de férias"""
        inicio = Formatadores.formatar_data_brasileira(data_inicio)
        fim = Formatadores.formatar_data_brasileira(data_fim)
        return f"{inicio} a {fim}"
    
    @staticmethod
    def formatar_saldo_ferias(saldo: int) -> str:
        """Formata saldo de férias"""
        if saldo == 1:
            return "1 dia"
        return f"{saldo} dias"

# Builder pattern para queries complexas
class QueryBuilder:
    def __init__(self):
        self.select_fields = []
        self.from_table = ""
        self.joins = []
        self.where_conditions = []
        self.order_by = []
        self.limit_value = None
    
    def select(self, *fields):
        self.select_fields.extend(fields)
        return self
    
    def from_table(self, table):
        self.from_table = table
        return self
    
    def join(self, table, condition):
        self.joins.append(f"JOIN {table} ON {condition}")
        return self
    
    def where(self, condition):
        self.where_conditions.append(condition)
        return self
    
    def order_by_field(self, field, direction="ASC"):
        self.order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count):
        self.limit_value = count
        return self
    
    def build(self):
        query_parts = []
        
        # SELECT
        if self.select_fields:
            query_parts.append(f"SELECT {', '.join(self.select_fields)}")
        else:
            query_parts.append("SELECT *")
        
        # FROM
        if self.from_table:
            query_parts.append(f"FROM {self.from_table}")
        
        # JOINs
        for join in self.joins:
            query_parts.append(join)
        
        # WHERE
        if self.where_conditions:
            query_parts.append(f"WHERE {' AND '.join(self.where_conditions)}")
        
        # ORDER BY
        if self.order_by:
            query_parts.append(f"ORDER BY {', '.join(self.order_by)}")
        
        # LIMIT
        if self.limit_value:
            query_parts.append(f"LIMIT {self.limit_value}")
        
        return " ".join(query_parts)

# Factory pattern para criação de objetos
class UsuarioFactory:
    @staticmethod
    def criar_usuario_padrao(nome: str, email: str, setor: str, funcao: str) -> Usuario:
        """Cria usuário com valores padrão"""
        nivel = NivelAcesso.MASTER if "RH" in funcao else NivelAcesso.COLABORADOR
        
        return Usuario(
            id=0,  # Será definido pelo banco
            nome=nome,
            email=email,
            setor=setor,
            funcao=funcao,
            nivel_acesso=nivel,
            saldo_ferias=Constantes.DIAS_FERIAS_PADRAO
        )

class FeriasFactory:
    @staticmethod
    def criar_ferias_padrao(usuario_id: int, data_inicio: str, data_fim: str, dias: int) -> Ferias:
        """Cria férias com valores padrão"""
        return Ferias(
            id=0,  # Será definido pelo banco
            usuario_id=usuario_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_utilizados=dias,
            status=StatusFerias.PENDENTE
        )