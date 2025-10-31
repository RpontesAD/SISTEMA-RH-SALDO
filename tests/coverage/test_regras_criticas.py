"""
Testes de cobertura para regras críticas do sistema
"""
import unittest
from datetime import datetime, date, timedelta
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.regras_ferias import RegrasFerias
from core.regras_saldo import RegrasSaldo


class TestRegrasCriticas(unittest.TestCase):
    """
    Testes focados nas regras críticas de negócio que devem ter 100% de cobertura
    """
    
    def setUp(self):
        self.regras_ferias = RegrasFerias()
        self.regras_saldo = RegrasSaldo()
    
    # REGRAS CRÍTICAS DE ANTECEDÊNCIA
    def test_antecedencia_exato_30_dias(self):
        """Teste crítico: exatamente 30 dias de antecedência"""
        data_inicio = date.today() + timedelta(days=30)
        resultado = self.regras_ferias.validar_antecedencia(data_inicio)
        self.assertTrue(resultado['valida'])
    
    def test_antecedencia_29_dias(self):
        """Teste crítico: 29 dias de antecedência (limite inferior)"""
        data_inicio = date.today() + timedelta(days=29)
        resultado = self.regras_ferias.validar_antecedencia(data_inicio)
        self.assertFalse(resultado['valida'])
    
    def test_antecedencia_31_dias(self):
        """Teste crítico: 31 dias de antecedência (acima do limite)"""
        data_inicio = date.today() + timedelta(days=31)
        resultado = self.regras_ferias.validar_antecedencia(data_inicio)
        self.assertTrue(resultado['valida'])
    
    # REGRAS CRÍTICAS DE PERÍODO MÍNIMO
    def test_periodo_valido(self):
        """Teste crítico: período válido de férias"""
        data_inicio = date(2024, 12, 1)
        data_fim = date(2024, 12, 10)
        resultado = self.regras_ferias.validar_periodo(data_inicio, data_fim)
        self.assertTrue(resultado['valida'])
    
    def test_periodo_muito_longo(self):
        """Teste crítico: período muito longo (acima de 30 dias)"""
        data_inicio = date(2024, 12, 1)
        data_fim = date(2025, 1, 15)  # 45 dias
        resultado = self.regras_ferias.validar_periodo(data_inicio, data_fim)
        self.assertFalse(resultado['valida'])
    
    # REGRAS CRÍTICAS DE SALDO
    def test_saldo_exato_limite_maximo(self):
        """Teste crítico: saldo exatamente no limite máximo (12 dias)"""
        resultado = self.regras_saldo.validar_saldo_dentro_limites(12)
        self.assertTrue(resultado['valido'])
    
    def test_saldo_acima_limite_maximo(self):
        """Teste crítico: saldo acima do limite máximo"""
        resultado = self.regras_saldo.validar_saldo_dentro_limites(13)
        self.assertFalse(resultado['valido'])
    
    def test_saldo_zero(self):
        """Teste crítico: saldo zero"""
        resultado = self.regras_saldo.validar_saldo_dentro_limites(0)
        self.assertTrue(resultado['valido'])
        
        # Teste se pode tirar férias com saldo zero
        resultado_ferias = self.regras_ferias.validar_saldo_suficiente(0, 1, "Aprovada")
        self.assertFalse(resultado_ferias['valida'])
    
    def test_saldo_negativo(self):
        """Teste crítico: saldo negativo"""
        resultado = self.regras_saldo.validar_saldo_dentro_limites(-1)
        self.assertFalse(resultado['valido'])
        
        # Teste se pode tirar férias com saldo negativo
        resultado_ferias = self.regras_ferias.validar_saldo_suficiente(-1, 1, "Aprovada")
        self.assertFalse(resultado_ferias['valida'])
    
    # REGRAS CRÍTICAS DE CÁLCULO
    def test_calculo_saldo_teorico_completo(self):
        """Teste crítico: usar todo o saldo em férias"""
        ferias_aprovadas = [{'dias_utilizados': 12}]  # Todo o saldo
        saldo_final = self.regras_saldo.calcular_saldo_teorico(ferias_aprovadas)
        self.assertEqual(saldo_final, 0)
    
    def test_detectar_inconsistencia_perfeita(self):
        """Teste crítico: saldo perfeitamente consistente"""
        saldo_atual = 7
        ferias_aprovadas = [{'dias_utilizados': 5}]  # 12 - 5 = 7
        resultado = self.regras_saldo.detectar_inconsistencia_saldo(saldo_atual, ferias_aprovadas)
        self.assertFalse(resultado['inconsistente'])
    
    def test_saldo_com_pendentes_zero(self):
        """Teste crítico: sem férias pendentes"""
        saldo_atual = 10
        ferias_pendentes = []
        resultado = self.regras_saldo.calcular_saldo_com_pendentes(saldo_atual, ferias_pendentes)
        self.assertEqual(resultado['dias_pendentes'], 0)
        self.assertFalse(resultado['tem_pendencias'])
    
    # CENÁRIOS CRÍTICOS COMBINADOS
    def test_cenario_critico_limite_total(self):
        """Teste crítico: solicitar exatamente o saldo disponível"""
        saldo_atual = 12
        dias_solicitados = 12
        
        # Deve passar na validação de saldo
        resultado_saldo = self.regras_ferias.validar_saldo_suficiente(saldo_atual, dias_solicitados)
        self.assertTrue(resultado_saldo['valida'])
        
        # Deve passar na validação de férias se outros critérios forem atendidos
        data_inicio = date.today() + timedelta(days=45)
        data_fim = data_inicio + timedelta(days=11)  # 12 dias
        
        antecedencia = self.regras_ferias.validar_antecedencia(data_inicio)
        periodo = self.regras_ferias.validar_periodo(data_inicio, data_fim)
        
        self.assertTrue(antecedencia['valida'])
        self.assertTrue(periodo['valida'])
    
    def test_cenario_critico_multiplas_violacoes(self):
        """Teste crítico: múltiplas violações simultâneas"""
        # Antecedência insuficiente + período longo + saldo insuficiente
        data_inicio = date.today() + timedelta(days=15)  # < 30 dias
        data_fim = data_inicio + timedelta(days=35)  # > 30 dias
        dias_solicitados = 15  # > saldo
        saldo_atual = 10
        
        antecedencia = self.regras_ferias.validar_antecedencia(data_inicio)
        periodo = self.regras_ferias.validar_periodo(data_inicio, data_fim)
        saldo = self.regras_ferias.validar_saldo_suficiente(saldo_atual, dias_solicitados, "Aprovada")
        
        self.assertFalse(antecedencia['valida'])  # Antecedência insuficiente
        self.assertFalse(periodo['valida'])  # Período muito longo
        self.assertFalse(saldo['valida'])  # Saldo insuficiente
    
    def test_cenario_critico_data_passada(self):
        """Teste crítico: data de início no passado"""
        data_inicio = date.today() - timedelta(days=1)
        
        resultado = self.regras_ferias.validar_antecedencia(data_inicio)
        self.assertFalse(resultado['valida'])
    
    def test_cenario_critico_data_fim_antes_inicio(self):
        """Teste crítico: data fim antes da data início"""
        data_inicio = date(2024, 12, 10)
        data_fim = date(2024, 12, 5)  # Antes do início
        
        resultado = self.regras_ferias.validar_periodo(data_inicio, data_fim)
        self.assertFalse(resultado['valida'])


if __name__ == '__main__':
    unittest.main()