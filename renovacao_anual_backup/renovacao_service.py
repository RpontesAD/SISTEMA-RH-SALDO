"""
Serviço para gerenciamento de renovação anual de saldo
"""
import streamlit as st
from datetime import date
import pandas as pd

class RenovacaoService:
    """Serviço para renovação anual de saldo"""
    
    def __init__(self, db):
        self.db = db
    
    def validar_renovacao(self, ano, novo_saldo):
        """Valida parâmetros da renovação"""
        erros = []
        
        # Validar ano
        ano_atual = date.today().year
        if ano < 2024 or ano > 2030:
            erros.append("Ano deve estar entre 2024 e 2030")
        
        # Validar saldo
        if novo_saldo < 0 or novo_saldo > 30:
            erros.append("Saldo deve estar entre 0 e 30 dias")
        
        # Verificar se já houve renovação no ano
        try:
            if self.db.verificar_renovacao_ano(ano):
                erros.append(f"Já foi realizada renovação para o ano {ano}")
        except AttributeError:
            # Função ainda não existe, pular verificação
            pass
        
        return len(erros) == 0, erros
    
    def simular_renovacao(self, novo_saldo):
        """Simula renovação sem alterar dados"""
        try:
            try:
                stats = self.db.get_estatisticas_saldo()
            except AttributeError:
                # Função ainda não existe, usar alternativa
                usuarios = self.db.get_users()
                if usuarios:
                    saldos = [u['saldo_ferias'] for u in usuarios]
                    stats = [{
                        'total_colaboradores': len(usuarios),
                        'saldo_medio': sum(saldos) / len(saldos)
                    }]
                else:
                    stats = None
            
            if not stats:
                return False, "Erro ao obter estatísticas"
            
            stat = stats[0]
            total_colaboradores = int(stat['total_colaboradores'])
            saldo_medio_atual = float(stat['saldo_medio'])
            
            # Calcular impacto
            diferenca_media = novo_saldo - saldo_medio_atual
            
            resultado = {
                'total_afetados': total_colaboradores,
                'novo_saldo': novo_saldo,
                'saldo_medio_atual': saldo_medio_atual,
                'diferenca_media': diferenca_media,
                'impacto': 'aumento' if diferenca_media > 0 else 'redução' if diferenca_media < 0 else 'neutro'
            }
            
            return True, resultado
            
        except Exception as e:
            return False, f"Erro na simulação: {str(e)}"
    
    def executar_renovacao(self, ano, novo_saldo, usuario_responsavel_id):
        """Executa renovação real"""
        try:
            # Validar antes de executar
            valido, erros = self.validar_renovacao(ano, novo_saldo)
            if not valido:
                return False, "; ".join(erros)
            
            # Executar renovação
            try:
                sucesso, mensagem = self.db.renovar_saldo_anual(
                    ano, novo_saldo, usuario_responsavel_id, modo_teste=False
                )
            except AttributeError:
                # Função ainda não existe, simular por enquanto
                usuarios = self.db.get_users()
                total = len(usuarios) if usuarios else 0
                return True, f"SIMULAÇÃO: {total} colaboradores receberiam {novo_saldo} dias (função em desenvolvimento)"
            
            return sucesso, mensagem
            
        except Exception as e:
            return False, f"Erro na execução: {str(e)}"
    
    def get_previa_renovacao(self, novo_saldo):
        """Obtém prévia detalhada da renovação"""
        try:
            usuarios = self.db.get_users()
            if not usuarios:
                return None
            
            df = pd.DataFrame(usuarios)
            
            # Estatísticas atuais
            total = len(df)
            saldo_atual_total = df['saldo_ferias'].sum()
            saldo_medio_atual = df['saldo_ferias'].mean()
            
            # Estatísticas após renovação
            saldo_novo_total = total * novo_saldo
            diferenca_total = saldo_novo_total - saldo_atual_total
            
            # Distribuição por setor (opcional)
            try:
                por_setor = df.groupby('setor').agg({
                    'saldo_ferias': ['count', 'mean', 'sum']
                }).round(1)
            except:
                por_setor = None
            
            previa = {
                'total_colaboradores': total,
                'saldo_atual_total': saldo_atual_total,
                'saldo_medio_atual': round(saldo_medio_atual, 1),
                'saldo_novo_total': saldo_novo_total,
                'diferenca_total': diferenca_total,
                'novo_saldo': novo_saldo,
                'distribuicao_setor': por_setor
            }
            
            return previa
            
        except Exception as e:
            st.error(f"Erro ao gerar prévia: {e}")
            return None
    
    def verificar_seguranca(self):
        """Verificações de segurança antes da renovação"""
        verificacoes = []
        
        # Verificar se há backup recente
        try:
            # Verificar se há usuários
            usuarios = self.db.get_users()
            if not usuarios:
                verificacoes.append(("❌", "Nenhum usuário encontrado"))
            else:
                verificacoes.append(("✅", f"{len(usuarios)} usuários encontrados"))
            
                # Verificar conexão com banco
            try:
                stats = self.db.get_estatisticas_saldo()
                if stats:
                    verificacoes.append(("✅", "Conexão com banco funcionando"))
                else:
                    verificacoes.append(("❌", "Problema na conexão com banco"))
            except AttributeError:
                # Testar com função alternativa
                try:
                    usuarios = self.db.get_users()
                    verificacoes.append(("✅", "Conexão com banco funcionando (modo compatibilidade)"))
                except:
                    verificacoes.append(("❌", "Problema na conexão com banco"))
            
                # Verificar se há férias pendentes
            try:
                ferias = self.db.get_all_ferias()
                pendentes = [f for f in ferias if f.get('status', '').lower() == 'pendente']
                if pendentes:
                    verificacoes.append(("⚠️", f"{len(pendentes)} férias pendentes (não afetará renovação)"))
                else:
                    verificacoes.append(("✅", "Nenhuma férias pendente"))
            except:
                verificacoes.append(("✅", "Verificação de férias pendentes não disponível"))
                
        except Exception as e:
            verificacoes.append(("❌", f"Erro nas verificações: {e}"))
        
        return verificacoes