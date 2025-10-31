"""
Testes de integração para ColaboradoresService
"""
import unittest
from datetime import datetime, date
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.colaboradores_service import ColaboradoresService
from database.connection import get_connection


class TestColaboradoresServiceIntegration(unittest.TestCase):
    
    def setUp(self):
        self.service = ColaboradoresService()
        # Usar banco de teste em memória
        self.conn = get_connection(":memory:")
        self._setup_test_data()
    
    def _setup_test_data(self):
        """Configurar dados de teste"""
        cursor = self.conn.cursor()
        
        # Criar tabela necessária
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE,
                saldo_ferias INTEGER DEFAULT 30,
                data_admissao DATE,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def test_cadastrar_colaborador_valido(self):
        """Teste de integração para cadastro de colaborador válido"""
        dados = {
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        
        resultado = self.service.cadastrar_colaborador(dados)
        
        self.assertTrue(resultado['sucesso'])
        self.assertIn('cadastrado com sucesso', resultado['mensagem'])
    
    def test_cadastrar_colaborador_email_duplicado(self):
        """Teste de integração para cadastro com email duplicado"""
        dados1 = {
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        
        dados2 = {
            'nome': 'Maria Silva',
            'email': 'joao@teste.com',  # Email duplicado
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        
        # Primeiro cadastro deve funcionar
        resultado1 = self.service.cadastrar_colaborador(dados1)
        self.assertTrue(resultado1['sucesso'])
        
        # Segundo cadastro deve falhar
        resultado2 = self.service.cadastrar_colaborador(dados2)
        self.assertFalse(resultado2['sucesso'])
        self.assertIn('email já existe', resultado2['mensagem'].lower())
    
    def test_atualizar_saldo_valido(self):
        """Teste de integração para atualização de saldo válido"""
        # Primeiro cadastrar colaborador
        dados = {
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        self.service.cadastrar_colaborador(dados)
        
        # Depois atualizar saldo
        resultado = self.service.atualizar_saldo(1, 25)
        
        self.assertTrue(resultado['sucesso'])
        self.assertIn('atualizado com sucesso', resultado['mensagem'])
    
    def test_atualizar_saldo_invalido(self):
        """Teste de integração para atualização de saldo inválido"""
        # Primeiro cadastrar colaborador
        dados = {
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        self.service.cadastrar_colaborador(dados)
        
        # Tentar atualizar com saldo inválido
        resultado = self.service.atualizar_saldo(1, 35)  # Acima do limite
        
        self.assertFalse(resultado['sucesso'])
        self.assertIn('limite máximo', resultado['mensagem'].lower())
    
    def test_listar_colaboradores(self):
        """Teste de integração para listagem de colaboradores"""
        # Cadastrar alguns colaboradores
        dados1 = {
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 30
        }
        
        dados2 = {
            'nome': 'Maria Santos',
            'email': 'maria@teste.com',
            'data_admissao': '2024-01-01',
            'saldo_ferias': 25
        }
        
        self.service.cadastrar_colaborador(dados1)
        self.service.cadastrar_colaborador(dados2)
        
        # Listar colaboradores
        colaboradores = self.service.listar_colaboradores()
        
        self.assertGreaterEqual(len(colaboradores), 2)
        nomes = [c['nome'] for c in colaboradores]
        self.assertIn('João Silva', nomes)
        self.assertIn('Maria Santos', nomes)
    
    def tearDown(self):
        """Limpar dados de teste"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == '__main__':
    unittest.main()