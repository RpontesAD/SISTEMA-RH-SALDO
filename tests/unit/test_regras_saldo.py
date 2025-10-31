"""
Testes unitários para RegrasSaldo
"""
import unittest
from datetime import datetime, date
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.regras_saldo import RegrasSaldo


class TestRegrasSaldo(unittest.TestCase):
    
    def setUp(self):
        self.regras = RegrasSaldo()
    
    def test_validar_saldo_dentro_limites_valido(self):
        """Teste para saldo dentro dos limites"""
        resultado = self.regras.validar_saldo_dentro_limites(10)
        self.assertTrue(resultado['valido'])
    
    def test_validar_saldo_acima_limite(self):
        """Teste para saldo acima do limite máximo"""
        resultado = self.regras.validar_saldo_dentro_limites(15)
        self.assertFalse(resultado['valido'])
    
    def test_validar_saldo_zero(self):
        """Teste para saldo zero (limite mínimo)"""
        resultado = self.regras.validar_saldo_dentro_limites(0)
        self.assertTrue(resultado['valido'])
    
    def test_validar_saldo_negativo(self):
        """Teste para saldo negativo"""
        resultado = self.regras.validar_saldo_dentro_limites(-5)
        self.assertFalse(resultado['valido'])
    
    def test_calcular_saldo_teorico(self):
        """Teste para cálculo de saldo teórico"""
        ferias_aprovadas = [
            {'dias_utilizados': 5},
            {'dias_utilizados': 3}
        ]
        
        resultado = self.regras.calcular_saldo_teorico(ferias_aprovadas)
        self.assertEqual(resultado, 4)  # 12 - 5 - 3 = 4
    
    def test_detectar_inconsistencia_saldo(self):
        """Teste para detecção de inconsistência"""
        saldo_atual = 10
        ferias_aprovadas = [{'dias_utilizados': 5}]  # Deveria ter saldo 7
        
        resultado = self.regras.detectar_inconsistencia_saldo(saldo_atual, ferias_aprovadas)
        self.assertTrue(resultado['inconsistente'])
    
    def test_calcular_saldo_com_pendentes(self):
        """Teste para cálculo com férias pendentes"""
        saldo_atual = 10
        ferias_pendentes = [{'dias_utilizados': 3}]
        
        resultado = self.regras.calcular_saldo_com_pendentes(saldo_atual, ferias_pendentes)
        self.assertEqual(resultado['saldo_se_aprovadas'], 7)
    
    def test_validar_operacao_saldo_valida(self):
        """Teste para validação de operação válida"""
        saldo_atual = 10
        
        resultado = self.regras.validar_operacao_saldo(saldo_atual, "subtrair", 5)
        self.assertTrue(resultado['permitida'])
        self.assertEqual(resultado['novo_saldo'], 5)
    
    def test_validar_operacao_saldo_invalida(self):
        """Teste para validação de operação inválida"""
        saldo_atual = 10
        
        resultado = self.regras.validar_operacao_saldo(saldo_atual, "subtrair", 15)
        self.assertFalse(resultado['permitida'])
    
    def test_validar_operacao_adicionar(self):
        """Teste para operação de adição"""
        saldo_atual = 5
        
        resultado = self.regras.validar_operacao_saldo(saldo_atual, "adicionar", 3)
        self.assertTrue(resultado['permitida'])
        self.assertEqual(resultado['novo_saldo'], 8)
    
    def test_validar_operacao_definir(self):
        """Teste para operação de definição"""
        saldo_atual = 5
        
        resultado = self.regras.validar_operacao_saldo(saldo_atual, "definir", 8)
        self.assertTrue(resultado['permitida'])
        self.assertEqual(resultado['novo_saldo'], 8)


if __name__ == '__main__':
    unittest.main()