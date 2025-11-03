"""
Testes para constantes centralizadas
"""
import unittest
from src.utils.constants import (
    SETORES, FUNCOES, NIVEIS_ACESSO, STATUS_FERIAS,
    SALDO_MINIMO, SALDO_MAXIMO, DIAS_FERIAS_PADRAO
)

class TestConstants(unittest.TestCase):
    
    def test_setores_nao_vazio(self):
        """Testa se SETORES não está vazio"""
        self.assertGreater(len(SETORES), 0)
        self.assertIn("RH", SETORES)
    
    def test_funcoes_nao_vazio(self):
        """Testa se FUNCOES não está vazio"""
        self.assertGreater(len(FUNCOES), 0)
        self.assertIn("RH", FUNCOES)
    
    def test_niveis_acesso_completos(self):
        """Testa se todos os níveis de acesso estão definidos"""
        niveis_esperados = ["master", "diretoria", "coordenador", "colaborador"]
        for nivel in niveis_esperados:
            self.assertIn(nivel, NIVEIS_ACESSO)
    
    def test_status_ferias_completos(self):
        """Testa se todos os status de férias estão definidos"""
        status_esperados = ["APROVADA", "PENDENTE", "CANCELADA", "REJEITADA"]
        for status in status_esperados:
            self.assertIn(status, STATUS_FERIAS)
    
    def test_saldos_validos(self):
        """Testa se os valores de saldo são válidos"""
        self.assertGreaterEqual(SALDO_MINIMO, 0)
        self.assertGreater(SALDO_MAXIMO, SALDO_MINIMO)
        self.assertGreaterEqual(DIAS_FERIAS_PADRAO, SALDO_MINIMO)
        self.assertLessEqual(DIAS_FERIAS_PADRAO, SALDO_MAXIMO)

if __name__ == '__main__':
    unittest.main()