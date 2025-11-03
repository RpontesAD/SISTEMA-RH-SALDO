"""
Serviço de Colaboradores - Orquestra operações de usuários

Esta camada separa a lógica de negócio da interface para operações de colaboradores.
"""

from typing import Dict, Any
from datetime import date
from ..core.regras_saldo import RegrasSaldo
from ..utils.validators import validar_email, validar_senha, validar_nome
from ..utils.constants import DIAS_FERIAS_PADRAO
from ..utils.code_standards import (
    Usuario, ResultadoOperacao, ValidacaoResult, Constantes, 
    Validadores, NivelAcesso, UsuarioFactory, documentar_operacao
)


class ColaboradoresService:
    """
    Serviço que orquestra operações de colaboradores.
    
    Responsabilidades:
    - Validar dados de colaboradores
    - Coordenar operações CRUD
    - Preparar dados para interface
    - Aplicar regras de negócio
    """
    
    def __init__(self, users_db):
        """
        Inicializa o serviço.
        
        Args:
            users_db: Instância do UserManager
        """
        self.users_db = users_db
    
    def validar_dados_colaborador(self, nome: str, email: str, senha: str, 
                                 setor: str, funcao: str, saldo_ferias: int = 12) -> Dict[str, Any]:
        """
        Valida todos os dados do colaborador.
        
        Args:
            nome: Nome do colaborador
            email: Email do colaborador
            senha: Senha do colaborador
            setor: Setor do colaborador
            funcao: Função do colaborador
            saldo_ferias: Saldo inicial de férias
            
        Returns:
            Dict com resultado da validação
        """
        # Validar nome usando validadores centralizados
        nome_valido, nome_msg = validar_nome(nome)
        if not nome_valido:
            return {
                "valido": False,
                "erro": nome_msg,
                "campo": "nome"
            }
        
        # Validar email usando validadores centralizados
        if not validar_email(email):
            return {
                "valido": False,
                "erro": "Email inválido",
                "campo": "email"
            }
        
        # Validar senha usando validadores centralizados
        senha_valida, senha_msg = validar_senha(senha)
        if not senha_valida:
            return {
                "valido": False,
                "erro": senha_msg,
                "campo": "senha"
            }
        
        # Validar campos obrigatórios
        if not setor or not setor.strip():
            return {
                "valido": False,
                "erro": "Setor é obrigatório",
                "campo": "setor"
            }
        
        if not funcao or not funcao.strip():
            return {
                "valido": False,
                "erro": "Função é obrigatória",
                "campo": "funcao"
            }
        
        # Validar saldo usando RegrasSaldo
        validacao_saldo = RegrasSaldo.validar_saldo_dentro_limites(saldo_ferias)
        if not validacao_saldo["valido"]:
            return {
                "valido": False,
                "erro": validacao_saldo["mensagem"],
                "campo": "saldo_ferias",
                "saldo_corrigido": validacao_saldo["saldo_corrigido"]
            }
        
        return {
            "valido": True,
            "saldo_corrigido": validacao_saldo["saldo_corrigido"]
        }
    
    @documentar_operacao("cadastrar_colaborador", "Cadastro de novo colaborador")
    def cadastrar_colaborador(self, nome: str, email: str, senha: str, setor: str, 
                             funcao: str, nivel_acesso: str = "colaborador", saldo_ferias: int = None, 
                             data_admissao: date = None) -> Dict[str, Any]:
        """
        Cadastra novo colaborador após validações.
        
        Args:
            nome: Nome do colaborador
            email: Email do colaborador
            senha: Senha do colaborador
            setor: Setor do colaborador
            funcao: Função do colaborador
            saldo_ferias: Saldo inicial de férias
            data_admissao: Data de admissão
            
        Returns:
            Dict com resultado da operação
        """
        # Validar dados
        validacao = self.validar_dados_colaborador(nome, email, senha, setor, funcao, saldo_ferias)
        
        if not validacao["valido"]:
            return {
                "sucesso": False,
                "erro": validacao["erro"],
                "campo": validacao["campo"],
                "saldo_corrigido": validacao.get("saldo_corrigido")
            }
        
        # Usar saldo corrigido ou padrão
        saldo_final = validacao.get("saldo_corrigido", saldo_ferias or DIAS_FERIAS_PADRAO)
        
        # Cadastrar no banco
        try:
            resultado = self.users_db.create_user(
                nome=nome.strip(),
                email=email.strip().lower(),
                senha=senha,
                setor=setor,
                funcao=funcao,
                nivel_acesso=nivel_acesso,
                saldo_ferias=saldo_final,
                data_admissao=data_admissao or date.today()
            )
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": f"Colaborador {nome} cadastrado com sucesso",
                    "saldo_usado": saldo_final
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Email já está em uso ou erro interno",
                    "campo": "email"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "campo": "sistema"
            }
    
    def obter_colaboradores(self, setor: str = None) -> Dict[str, Any]:
        """
        Obtém lista de colaboradores.
        
        Args:
            setor: Filtro por setor (opcional)
            
        Returns:
            Dict com colaboradores
        """
        try:
            users_df = self.users_db.get_users(setor=setor)
            
            if users_df.empty:
                return {
                    "sucesso": True,
                    "vazio": True,
                    "mensagem": "Nenhum colaborador encontrado",
                    "colaboradores": []
                }
            
            return {
                "sucesso": True,
                "vazio": False,
                "colaboradores": users_df,
                "total": len(users_df)
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao carregar colaboradores: {e}",
                "colaboradores": []
            }
    
    def atualizar_colaborador(self, user_id: int, nome: str, email: str, setor: str,
                             funcao: str, nivel_acesso: str, saldo_ferias: int) -> Dict[str, Any]:
        """
        Atualiza dados do colaborador.
        
        Args:
            user_id: ID do colaborador
            nome: Nome do colaborador
            email: Email do colaborador
            setor: Setor do colaborador
            funcao: Função do colaborador
            nivel_acesso: Nível de acesso
            saldo_ferias: Saldo de férias
            
        Returns:
            Dict com resultado da operação
        """
        # Validar dados básicos (sem senha)
        nome_valido, nome_msg = validar_nome(nome)
        if not nome_valido:
            return {
                "sucesso": False,
                "erro": nome_msg,
                "campo": "nome"
            }
        
        if not validar_email(email):
            return {
                "sucesso": False,
                "erro": "Email inválido",
                "campo": "email"
            }
        
        # Validar saldo
        validacao_saldo = RegrasSaldo.validar_saldo_dentro_limites(saldo_ferias)
        if not validacao_saldo["valido"]:
            return {
                "sucesso": False,
                "erro": validacao_saldo["mensagem"],
                "campo": "saldo_ferias",
                "saldo_corrigido": validacao_saldo["saldo_corrigido"]
            }
        
        # Atualizar no banco
        try:
            resultado = self.users_db.update_user(
                user_id=user_id,
                nome=nome.strip(),
                email=email.strip().lower(),
                setor=setor,
                funcao=funcao,
                nivel_acesso=nivel_acesso,
                saldo_ferias=validacao_saldo["saldo_corrigido"]
            )
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": f"Colaborador {nome} atualizado com sucesso"
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Erro ao atualizar colaborador",
                    "campo": "sistema"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "campo": "sistema"
            }
    
    def excluir_colaborador(self, user_id: int, nome_colaborador: str) -> Dict[str, Any]:
        """
        Exclui colaborador após validações.
        
        Args:
            user_id: ID do colaborador
            nome_colaborador: Nome do colaborador (para confirmação)
            
        Returns:
            Dict com resultado da operação
        """
        try:
            resultado = self.users_db.delete_user(user_id)
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": f"Colaborador {nome_colaborador} excluído com sucesso"
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Erro ao excluir colaborador ou colaborador não encontrado"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}"
            }
    
    def atualizar_saldo_colaborador(self, user_id: int, novo_saldo: int, 
                                   motivo: str = "Ajuste manual") -> Dict[str, Any]:
        """
        Atualiza apenas o saldo do colaborador.
        
        Args:
            user_id: ID do colaborador
            novo_saldo: Novo saldo
            motivo: Motivo da alteração
            
        Returns:
            Dict com resultado da operação
        """
        # Validar saldo
        validacao = RegrasSaldo.validar_saldo_dentro_limites(novo_saldo)
        
        if not validacao["valido"]:
            return {
                "sucesso": False,
                "erro": validacao["mensagem"],
                "saldo_corrigido": validacao["saldo_corrigido"]
            }
        
        try:
            resultado = self.users_db.update_saldo_ferias(
                user_id=user_id,
                novo_saldo=validacao["saldo_corrigido"],
                motivo=motivo
            )
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": f"Saldo atualizado para {validacao['saldo_corrigido']} dias",
                    "saldo_final": validacao["saldo_corrigido"]
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Erro ao atualizar saldo"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}"
            }