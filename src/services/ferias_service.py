"""
Serviço de Férias - Orquestra operações de férias

Esta camada separa a lógica de negócio da interface,
coordenando entre as regras de negócio (core) e acesso a dados (database).
"""

from typing import Dict, Any, Tuple
from datetime import date
from ..core.regras_ferias import RegrasFerias
from ..core.regras_saldo import RegrasSaldo
from ..utils.calculos import calcular_dias_uteis
from ..utils.error_handler import handle_critical_operation, DatabaseError, ValidationError, log_operation


class FeriasService:
    """
    Serviço que orquestra operações de férias.
    
    Responsabilidades:
    - Coordenar validações de regras de negócio
    - Orquestrar operações no banco de dados
    - Preparar dados para a interface
    - Não contém lógica de interface (sem Streamlit)
    """
    
    def __init__(self, ferias_db, users_db):
        """
        Inicializa o serviço com dependências.
        
        Args:
            ferias_db: Instância do FeriasManager
            users_db: Instância do UserManager
        """
        self.ferias_db = ferias_db
        self.users_db = users_db
    
    def validar_cadastro_ferias(self, usuario_id: int, data_inicio: date, data_fim: date, 
                               status: str, usuario_nivel: str) -> Dict[str, Any]:
        """
        Valida todos os aspectos do cadastro de férias.
        
        Args:
            usuario_id: ID do usuário
            data_inicio: Data de início
            data_fim: Data de fim
            status: Status das férias
            usuario_nivel: Nível do usuário
            
        Returns:
            Dict com resultado da validação
        """
        # 1. Validar período
        validacao_periodo = RegrasFerias.validar_periodo(data_inicio, data_fim)
        if not validacao_periodo["valida"]:
            return {
                "valido": False,
                "erro": validacao_periodo["mensagem"],
                "tipo": "periodo"
            }
        
        # 2. Validar antecedência (apenas se não for RH)
        if usuario_nivel != "master":
            validacao_antecedencia = RegrasFerias.validar_antecedencia(data_inicio, usuario_nivel)
            if not validacao_antecedencia["valida"]:
                return {
                    "valido": False,
                    "erro": validacao_antecedencia["mensagem"],
                    "tipo": "antecedencia",
                    "detalhes": validacao_antecedencia
                }
        else:
            validacao_antecedencia = {"valida": True, "mensagem": "RH pode cadastrar sem antecedência"}
        
        # 3. Calcular dias úteis
        try:
            dias_uteis = calcular_dias_uteis(data_inicio, data_fim)
            if dias_uteis <= 0:
                raise ValidationError("Período de férias inválido", "periodo", f"{data_inicio} a {data_fim}")
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Erro ao calcular dias úteis: {e}")
        
        # 4. Validar saldo (se necessário)
        if status == "Aprovada":
            try:
                users_list = self.users_db.get_users()
                
                # Converter lista para DataFrame se necessário
                if isinstance(users_list, list):
                    import pandas as pd
                    users_df = pd.DataFrame(users_list)
                else:
                    users_df = users_list
                    
                user_data = users_df[users_df["id"] == usuario_id].iloc[0]
                saldo_atual = user_data["saldo_ferias"]
                
                validacao_saldo = RegrasFerias.validar_saldo_suficiente(saldo_atual, dias_uteis, status)
                if not validacao_saldo["valida"]:
                    return {
                        "valido": False,
                        "erro": validacao_saldo["mensagem"],
                        "tipo": "saldo",
                        "detalhes": {
                            "saldo_atual": saldo_atual,
                            "dias_solicitados": dias_uteis
                        }
                    }
            except Exception as e:
                return {
                    "valido": False,
                    "erro": f"Erro ao validar saldo: {e}",
                    "tipo": "saldo"
                }
        
        return {
            "valido": True,
            "dias_uteis": dias_uteis,
            "validacao_antecedencia": validacao_antecedencia,
            "validacao_periodo": validacao_periodo
        }
    
    def cadastrar_ferias(self, usuario_id: int, data_inicio: date, data_fim: date,
                        status: str, usuario_nivel: str) -> Dict[str, Any]:
        """
        Cadastra férias após validações.
        
        Args:
            usuario_id: ID do usuário
            data_inicio: Data de início
            data_fim: Data de fim
            status: Status das férias
            usuario_nivel: Nível do usuário
            
        Returns:
            Dict com resultado da operação
        """
        # Validar antes de cadastrar
        validacao = self.validar_cadastro_ferias(usuario_id, data_inicio, data_fim, status, usuario_nivel)
        
        if not validacao["valido"]:
            return {
                "sucesso": False,
                "erro": validacao["erro"],
                "tipo": validacao["tipo"],
                "detalhes": validacao.get("detalhes")
            }
        
        # Cadastrar no banco
        try:
            resultado = self.ferias_db.add_ferias(
                usuario_id=usuario_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                usuario_nivel=usuario_nivel
            )
            
            # Garantir que resultado seja tratado como booleano
            sucesso = bool(resultado) if resultado is not None else False
            
            if sucesso:
                return {
                    "sucesso": True,
                    "mensagem": "Férias cadastradas com sucesso",
                    "dias_uteis": validacao["dias_uteis"]
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Erro interno ao cadastrar férias",
                    "tipo": "database"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "tipo": "exception"
            }
    
    def obter_usuarios_para_selecao(self) -> Dict[str, Any]:
        """
        Obtém usuários formatados para seleção na interface.
        
        Returns:
            Dict com usuários e opções para selectbox
        """
        try:
            users_list = self.users_db.get_users()
            
            # Converter lista para DataFrame se necessário
            if isinstance(users_list, list):
                if not users_list:
                    return {
                        "sucesso": False,
                        "erro": "Nenhum colaborador cadastrado",
                        "usuarios": [],
                        "opcoes": {}
                    }
                import pandas as pd
                users_df = pd.DataFrame(users_list)
            else:
                users_df = users_list
                if users_df.empty:
                    return {
                        "sucesso": False,
                        "erro": "Nenhum colaborador cadastrado",
                        "usuarios": [],
                        "opcoes": {}
                    }
            
            # Ordenar por nome e formatar opções para selectbox
            from collections import OrderedDict
            users_df_sorted = users_df.sort_values('nome')
            opcoes = OrderedDict()
            for _, row in users_df_sorted.iterrows():
                opcoes[f"{row['nome']} ({row['email']})"] = row['id']
            
            return {
                "sucesso": True,
                "usuarios": users_df_sorted,
                "opcoes": opcoes
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao carregar usuários: {e}",
                "usuarios": [],
                "opcoes": {}
            }
    
    def obter_historico_ferias(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém histórico de férias formatado para exibição.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com histórico formatado
        """
        try:
            ferias_list = self.ferias_db.get_ferias_usuario(user_id)
            
            # Converter lista para DataFrame se necessário
            if isinstance(ferias_list, list):
                if not ferias_list:
                    return {
                        "sucesso": True,
                        "vazio": True,
                        "mensagem": "Nenhuma férias cadastrada para este colaborador"
                    }
                import pandas as pd
                ferias_df = pd.DataFrame(ferias_list)
            else:
                ferias_df = ferias_list
                if ferias_df.empty:
                    return {
                        "sucesso": True,
                        "vazio": True,
                        "mensagem": "Nenhuma férias cadastrada para este colaborador"
                    }
            
            # Formatar datas para exibição no padrão brasileiro
            ferias_formatado = ferias_df.copy()
            ferias_formatado['data_inicio'] = ferias_df['data_inicio'].apply(
                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
            )
            ferias_formatado['data_fim'] = ferias_df['data_fim'].apply(
                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
            )
            
            return {
                "sucesso": True,
                "vazio": False,
                "ferias": ferias_formatado,
                "total": len(ferias_df)
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao carregar histórico: {e}"
            }
    
    def alterar_status_ferias(self, ferias_id: int, novo_status: str) -> Dict[str, Any]:
        """
        Altera status de férias com validações flexíveis.
        
        Args:
            ferias_id: ID das férias
            novo_status: Novo status
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verificar se as férias existem
            ferias_info = self._get_ferias_info(ferias_id)
            if not ferias_info:
                return {
                    "sucesso": False,
                    "erro": "Período de férias não encontrado"
                }
            
            # Tentar alterar status
            resultado = self.ferias_db.update_ferias_status(ferias_id, novo_status)
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": f"Status alterado para '{novo_status}' com sucesso"
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Não foi possível alterar o status. Verifique os logs para mais detalhes."
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}"
            }
    
    def _get_ferias_info(self, ferias_id: int) -> dict:
        """Obtém informações das férias"""
        try:
            # Usar o método da nova database
            result = self.ferias_db._execute_query(
                "SELECT id, usuario_id, data_inicio, data_fim, dias_utilizados, status FROM ferias WHERE id = %s", 
                (ferias_id,), 
                fetch=True
            )
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'id': row['id'],
                    'usuario_id': row['usuario_id'],
                    'data_inicio': row['data_inicio'],
                    'data_fim': row['data_fim'],
                    'dias_utilizados': row['dias_utilizados'],
                    'status': row['status']
                }
            return None
        except Exception as e:
            print(f"Erro ao buscar férias ID {ferias_id}: {e}")
            return None
    
    def excluir_ferias(self, ferias_id: int) -> Dict[str, Any]:
        """
        Exclui férias com validações.
        
        Args:
            ferias_id: ID das férias
            
        Returns:
            Dict com resultado da operação
        """
        try:
            resultado = self.ferias_db.delete_ferias(ferias_id)
            
            if resultado:
                return {
                    "sucesso": True,
                    "mensagem": "Férias excluídas com sucesso"
                }
            else:
                return {
                    "sucesso": False,
                    "erro": "Erro ao excluir férias"
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def obter_informacoes_saldo(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém informações completas de saldo para exibição.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com informações de saldo
        """
        try:
            # Obter dados do usuário
            users_list = self.users_db.get_users()
            
            # Converter lista para DataFrame se necessário
            if isinstance(users_list, list):
                import pandas as pd
                users_df = pd.DataFrame(users_list)
            else:
                users_df = users_list
                
            user_data = users_df[users_df["id"] == user_id].iloc[0]
            saldo_atual = user_data["saldo_ferias"]
            
            # Obter férias pendentes
            ferias_list = self.ferias_db.get_ferias_usuario(user_id)
            
            # Converter lista para DataFrame se necessário
            if isinstance(ferias_list, list):
                if not ferias_list:
                    ferias_pendentes = []
                else:
                    import pandas as pd
                    ferias_df = pd.DataFrame(ferias_list)
                    ferias_pendentes = ferias_df[ferias_df["status"] == "Pendente"]
            else:
                ferias_df = ferias_list
                ferias_pendentes = ferias_df[ferias_df["status"] == "Pendente"] if not ferias_df.empty else []
            
            # Calcular usando RegrasSaldo
            pendentes_list = ferias_pendentes.to_dict('records') if len(ferias_pendentes) > 0 else []
            calculo = RegrasSaldo.calcular_saldo_com_pendentes(saldo_atual, pendentes_list)
            
            return {
                "sucesso": True,
                "saldo_atual": calculo["saldo_atual"],
                "dias_pendentes": calculo["dias_pendentes"],
                "saldo_se_aprovadas": calculo["saldo_se_aprovadas"],
                "tem_pendencias": calculo["tem_pendencias"],
                "saldo_suficiente": calculo["saldo_suficiente_para_pendentes"]
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao calcular saldo: {e}",
                "saldo_atual": 0,
                "dias_pendentes": 0,
                "saldo_se_aprovadas": 0,
                "tem_pendencias": False,
                "saldo_suficiente": True
            }
    
    def obter_dias_aprovados(self, user_id: int) -> int:
        """
        Obtém total de dias de férias aprovadas para o usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Total de dias aprovados
        """
        try:
            ferias_list = self.ferias_db.get_ferias_usuario(user_id)
            
            # Converter lista para DataFrame se necessário
            if isinstance(ferias_list, list):
                if not ferias_list:
                    return 0
                import pandas as pd
                ferias_df = pd.DataFrame(ferias_list)
            else:
                ferias_df = ferias_list
                if ferias_df.empty:
                    return 0
            
            ferias_aprovadas = ferias_df[ferias_df["status"] == "Aprovado"]
            if ferias_aprovadas.empty:
                return 0
            
            return int(ferias_aprovadas["dias_utilizados"].sum())
            
        except Exception as e:
            return 0
    
    def aprovar_ferias(self, ferias_id: int) -> Dict[str, Any]:
        """
        Aprova férias específicas.
        
        Args:
            ferias_id: ID das férias
            
        Returns:
            Dict com resultado da operação
        """
        return self.alterar_status_ferias(ferias_id, "Aprovado")
    
    def cancelar_ferias(self, ferias_id: int) -> Dict[str, Any]:
        """
        Cancela férias específicas.
        
        Args:
            ferias_id: ID das férias
            
        Returns:
            Dict com resultado da operação
        """
        return self.alterar_status_ferias(ferias_id, "Rejeitado")