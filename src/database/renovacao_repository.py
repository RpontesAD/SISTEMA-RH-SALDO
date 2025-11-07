"""
Repositório de renovação de saldo
"""
from datetime import date
from .base_connection import BaseConnection

class RenovacaoRepository(BaseConnection):
    """Gerenciamento de renovação anual de saldo"""
    
    def verificar_renovacao_ano(self, ano):
        """Verifica se já houve renovação no ano"""
        result = self._execute_query("SELECT COUNT(*) as count FROM renovacao_saldo WHERE ano = %s", (ano,), fetch=True)
        return result[0]['count'] > 0 if result else False
    
    def renovar_saldo_anual_simples(self, ano, saldo_adicional, usuario_responsavel_id):
        """Renova saldo anual - versão simplificada sem backup"""
        try:
            # Verificar se já existe renovação para o ano
            result = self._execute_query("SELECT COUNT(*) as count FROM renovacao_saldo WHERE ano = %s", (ano,), fetch=True)
            if result and result[0]['count'] > 0:
                return False, "Já foi realizada renovação para este ano"
            
            # Atualizar saldos
            success1 = self._execute_query(
                "UPDATE usuarios SET saldo_ferias = saldo_ferias + %s WHERE ativo = true",
                (saldo_adicional,)
            )
            
            if not success1:
                return False, "Erro ao atualizar saldos"
            
            # Registrar renovação
            success2 = self._execute_query(
                "INSERT INTO renovacao_saldo (ano, saldo_padrao, usuario_responsavel_id) VALUES (%s, %s, %s)",
                (ano, saldo_adicional, usuario_responsavel_id)
            )
            
            if not success2:
                return False, "Erro ao registrar renovação"
            
            # Contar usuários
            usuarios = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE ativo = true", fetch=True)
            total = usuarios[0]['count'] if usuarios else 0
            
            return True, f"Renovação aplicada! {total} colaboradores receberam +{saldo_adicional} dias para {ano}."
            
        except Exception as e:
            return False, f"Erro na renovação: {str(e)}"
    
    def renovar_saldo_anual(self, ano, saldo_adicional, usuario_responsavel_id, modo_teste=False):
        """Método compatível que chama a versão simplificada"""
        if modo_teste:
            usuarios = self._execute_query("SELECT COUNT(*) as count FROM usuarios WHERE ativo = true", fetch=True)
            total = usuarios[0]['count'] if usuarios else 0
            return True, f"SIMULAÇÃO: {total} colaboradores receberiam +{saldo_adicional} dias somados ao saldo atual"
        
        return self.renovar_saldo_anual_simples(ano, saldo_adicional, usuario_responsavel_id)
    
    def get_historico_renovacoes(self):
        """Obtém histórico de renovações"""
        return self._execute_query("""
            SELECT r.*, u.nome as responsavel_nome 
            FROM renovacao_saldo r 
            LEFT JOIN usuarios u ON r.usuario_responsavel_id = u.id 
            ORDER BY r.ano DESC
        """, fetch=True)
    
    def desfazer_ultima_renovacao(self, usuario_responsavel_id):
        """Desfaz a última renovação subtraindo o valor adicionado"""
        try:
            # Buscar última renovação
            renovacoes = self._execute_query(
                "SELECT * FROM renovacao_saldo ORDER BY data_aplicacao DESC LIMIT 1",
                fetch=True
            )
            
            if not renovacoes:
                return False, "Nenhuma renovação encontrada para desfazer"
            
            renovacao = renovacoes[0]
            saldo_adicionado = renovacao['saldo_padrao']
            
            # Verificar se foi feita hoje (segurança)
            data_renovacao = renovacao['data_aplicacao'].date()
            if data_renovacao != date.today():
                return False, "Só é possível desfazer renovações do mesmo dia"
            
            # Subtrair o valor que foi adicionado
            success1 = self._execute_query(
                "UPDATE usuarios SET saldo_ferias = saldo_ferias - %s WHERE ativo = true AND saldo_ferias >= %s",
                (saldo_adicionado, saldo_adicionado)
            )
            
            if not success1:
                return False, "Erro ao atualizar saldos"
            
            # Remover registro de renovação
            success2 = self._execute_query(
                "DELETE FROM renovacao_saldo WHERE id = %s",
                (renovacao['id'],)
            )
            
            if not success2:
                return False, "Erro ao remover registro"
            
            return True, f"Renovação desfeita! Valor de {saldo_adicionado} dias foi removido dos saldos."
            
        except Exception as e:
            return False, f"Erro ao desfazer renovação: {str(e)}"