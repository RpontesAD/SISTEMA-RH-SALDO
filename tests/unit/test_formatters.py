"""
Testes para formatadores centralizados
"""
import unittest
from datetime import datetime, date
from src.utils.formatters import formatar_data_brasileira, formatar_saldo_ferias

class TestFormatters(unittest.TestCase):
    
    def test_formatar_data_brasileira_datetime(self):
        """Testa formatação de datetime"""
        data = datetime(2024, 12, 25)
        resultado = formatar_data_brasileira(data)
        self.assertEqual(resultado, "25/12/2024")
    
    def test_formatar_data_brasileira_date(self):
        """Testa formatação de date"""
        data = date(2024, 1, 15)
        resultado = formatar_data_brasileira(data)
        self.assertEqual(resultado, "15/01/2024")
    
    def test_formatar_data_brasileira_string(self):
        """Testa formatação de string"""
        data_str = "2024-03-10"
        resultado = formatar_data_brasileira(data_str)
        self.assertEqual(resultado, "10/03/2024")
    
    def test_formatar_data_brasileira_string_invalida(self):
        """Testa formatação de string inválida"""
        data_str = "data_invalida"
        resultado = formatar_data_brasileira(data_str)
        self.assertEqual(resultado, "data_invalida")
    
    def test_formatar_saldo_ferias_singular(self):
        """Testa formatação de saldo singular"""
        resultado = formatar_saldo_ferias(1)
        self.assertEqual(resultado, "1 dia")
    
    def test_formatar_saldo_ferias_plural(self):
        """Testa formatação de saldo plural"""
        resultado = formatar_saldo_ferias(10)
        self.assertEqual(resultado, "10 dias")
        
        resultado = formatar_saldo_ferias(0)
        self.assertEqual(resultado, "0 dias")

if __name__ == '__main__':
    unittest.main()