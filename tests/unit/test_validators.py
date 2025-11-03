"""
Testes para validadores centralizados
"""
import unittest
from src.utils.validators import validar_email, validar_senha, validar_nome

class TestValidators(unittest.TestCase):
    
    def test_validar_email_validos(self):
        """Testa emails válidos"""
        emails_validos = [
            "admin@rpontes.com",
            "usuario@empresa.com.br",
            "test.user@domain.org"
        ]
        for email in emails_validos:
            self.assertTrue(validar_email(email), f"Email {email} deveria ser válido")
    
    def test_validar_email_invalidos(self):
        """Testa emails inválidos"""
        emails_invalidos = [
            "email_sem_arroba",
            "@dominio.com",
            "usuario@",
            "usuario@dominio",
            ""
        ]
        for email in emails_invalidos:
            self.assertFalse(validar_email(email), f"Email {email} deveria ser inválido")
    
    def test_validar_senha_valida(self):
        """Testa senhas válidas"""
        senhas_validas = ["123456", "admin123", "senhaSegura"]
        for senha in senhas_validas:
            valido, msg = validar_senha(senha)
            self.assertTrue(valido, f"Senha {senha} deveria ser válida")
    
    def test_validar_senha_invalida(self):
        """Testa senhas inválidas"""
        senhas_invalidas = ["", "123", "ab"]
        for senha in senhas_invalidas:
            valido, msg = validar_senha(senha)
            self.assertFalse(valido, f"Senha {senha} deveria ser inválida")
            self.assertIn("6 caracteres", msg)
    
    def test_validar_nome_valido(self):
        """Testa nomes válidos"""
        nomes_validos = ["João", "Maria Silva", "José da Silva"]
        for nome in nomes_validos:
            valido, msg = validar_nome(nome)
            self.assertTrue(valido, f"Nome {nome} deveria ser válido")
    
    def test_validar_nome_invalido(self):
        """Testa nomes inválidos"""
        nomes_invalidos = ["", "A", " "]
        for nome in nomes_invalidos:
            valido, msg = validar_nome(nome)
            self.assertFalse(valido, f"Nome {nome} deveria ser inválido")

if __name__ == '__main__':
    unittest.main()