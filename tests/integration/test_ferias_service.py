"""
Testes de integração para FeriasService
"""
import unittest
from datetime import datetime, date, timedelta
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.ferias_service import FeriasService
from database.connection import get_connection


class TestFeriasServiceIntegration(unittest.TestCase):
    
    def setUp(self):
        self.service = FeriasService()
        # Usar banco de teste em memória
        self.conn = get_connection(":memory:")
        self._setup_test_data()
    
    def _setup_test_data(self):
        """Configurar dados de teste"""
        cursor = self.conn.cursor()
        
        # Criar tabelas necessárias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                saldo_ferias INTEGER DEFAULT 30,
                data_admissao DATE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ferias (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                data_inicio DATE,
                data_fim DATE,
                dias_solicitados INTEGER,
                status TEXT DEFAULT 'pendente',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Inserir usuário de teste
        cursor.execute('''
            INSERT INTO users (id, nome, saldo_ferias, data_admissao)
            VALUES (1, 'Teste User', 30, '2023-01-01')
        ''')
        
        self.conn.commit()
    
    def test_solicitar_ferias_valida(self):
        """Teste de integração para solicitação de férias válida"""
        data_inicio = date.today() + timedelta(days=45)
        data_fim = data_inicio + timedelta(days=9)
        
        resultado = self.service.solicitar_ferias(
            user_id=1,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_solicitados=10
        )
        
        self.assertTrue(resultado['sucesso'])
        self.assertIn('Férias solicitadas com sucesso', resultado['mensagem'])
    
    def test_solicitar_ferias_saldo_insuficiente(self):
        """Teste de integração para solicitação com saldo insuficiente"""
        data_inicio = date.today() + timedelta(days=45)
        data_fim = data_inicio + timedelta(days=34)
        
        resultado = self.service.solicitar_ferias(
            user_id=1,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_solicitados=35  # Mais que o saldo de 30
        )
        
        self.assertFalse(resultado['sucesso'])
        self.assertIn('saldo insuficiente', resultado['mensagem'].lower())
    
    def test_solicitar_ferias_antecedencia_insuficiente(self):
        """Teste de integração para solicitação com antecedência insuficiente"""
         data_inicio = date.today() + timedelta(days=15)  # Menos de 30 dias
        data_fim = data_inicio + timedelta(days=9)
        
        resultado = self.service.solicitar_ferias(
            user_id=1,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_solicitados=10
        )
        
        self.assertFalse(resultado['sucesso'])
        self.assertIn('antecedência', resultado['mensagem'].lower())
    
    def test_listar_ferias_usuario(self):
        """Teste de integração para listagem de férias do usuário"""
        # Primeiro solicitar férias
        data_inicio = date.today() + timedelta(days=45)
        data_fim = data_inicio + timedelta(days=9)
        
        self.service.solicitar_ferias(
            user_id=1,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_solicitados=10
        )
        
        # Depois listar
        ferias = self.service.listar_ferias_usuario(1)
        
        self.assertGreater(len(ferias), 0)
        self.assertEqual(ferias[0]['user_id'], 1)
    
    def tearDown(self):
        """Limpar dados de teste"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == '__main__':
    unittest.main()