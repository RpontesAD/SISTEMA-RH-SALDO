"""
Testes unitários para RegrasFerias
"""
import unittest
from datetime import datetime, date
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.regras_ferias import RegrasFerias


class TestRegrasFerias(unittest.TestCase):
    
    def setUp(self):
        self.regras = RegrasFerias()
    
    def test_validar_antecedencia_valida(self):
        """Teste para antecedência válida (30+ dias)"""
        from datetime import timedelta
        data_inicio = date.today() + timedelta(days=45)
        resultado = self.regras.validar_antecedencia(data_inicio)
        self.assertTrue(resultado['valida'])
    
    def test_validar_antecedencia_invalida(self):
        """Teste para antecedência inválida (<30 dias)"""
        from datetime import timedelta
        data_inicio = date.today() + timedelta(days=15)
        resultado = self.regras.validar_antecedencia(data_inicio)
        self.assertFalse(resultado['valida'])
    
    def test_validar_periodo_valido(self):
        """Teste para período válido"""
        data_inicio = date(2024, 12, 1)
        data_fim = date(2024, 12, 10)
        resultado = self.regras.validar_periodo(data_inicio, data_fim)
        self.assertTrue(resultado['valida'])
    
    def test_validar_periodo_invalido(self):
        """Teste para período inválido (data fim antes do início)"""
        data_inicio = date(2024, 12, 10)
        data_fim = date(2024, 12, 5)
        resultado = self.regras.validar_periodo(data_inicio, data_fim)
        self.assertFalse(resultado['valida'])
    
    def test_validar_saldo_suficiente_valido(self):
        """Teste para saldo suficiente"""
        resultado = self.regras.validar_saldo_suficiente(30, 15)
        self.assertTrue(resultado['valida'])
    
    def test_validar_saldo_suficiente_invalido(self):
        """Teste para saldo insuficiente"""
        resultado = self.regras.validar_saldo_suficiente(10, 15, "Aprovada")
        self.assertFalse(resultado['valida'])
    
    def test_validar_ferias_completa_valida(self):
        """Teste para validação completa de férias válidas"""
        from datetime import timedelta
        data_inicio = date.today() + timedelta(days=45)
        data_fim = data_inicio + timedelta(days=9)  # 10 dias
        dias_solicitados = 10
        saldo_atual = 12
        
        # Validar cada regra separadamente
        antecedencia = self.regras.validar_antecedencia(data_inicio)
        periodo = self.regras.validar_periodo(data_inicio, data_fim)
        saldo = self.regras.validar_saldo_suficiente(saldo_atual, dias_solicitados)
        
        self.assertTrue(antecedencia['valida'])
        self.assertTrue(periodo['valida'])
        self.assertTrue(saldo['valida'])
    
    def test_validar_ferias_completa_invalida(self):
        """Teste para validação completa de férias inválidas"""
        from datetime import timedelta
        data_inicio = date.today() + timedelta(days=15)  # Antecedência insuficiente
        data_fim = data_inicio + timedelta(days=35)  # Período muito longo
        dias_solicitados = 15  # Mais dias que o saldo
        saldo_atual = 10
        
        # Validar cada regra separadamente
        antecedencia = self.regras.validar_antecedencia(data_inicio)
        periodo = self.regras.validar_periodo(data_inicio, data_fim)
        saldo = self.regras.validar_saldo_suficiente(saldo_atual, dias_solicitados, "Aprovada")
        
        self.assertFalse(antecedencia['valida'])  # Antecedência insuficiente
        self.assertFalse(periodo['valida'])  # Período muito longo
        self.assertFalse(saldo['valida'])  # Saldo insuficiente


if __name__ == '__main__':
    unittest.main()