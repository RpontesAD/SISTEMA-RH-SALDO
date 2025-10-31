import mysql.connector
from mysql.connector import Error
import pandas as pd
import re
from .sql_security import SQLSecurity, secure_execute
from ..utils.resource_manager import managed_connection, managed_cursor, resource_tracker

class MySQLConnection:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def get_connection(self):
        """Retorna conexão MySQL"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
                resource_tracker.track_resource(self.connection, 'mysql_connection')
            return self.connection
        except Error as e:
            print(f"Erro ao conectar MySQL: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False):
        """Executa query MySQL de forma segura"""
        # Validar parâmetros antes da execução
        if params and not SQLSecurity.validate_params(params):
            raise ValueError("Parâmetros contêm conteúdo perigoso")
        
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(prepared=True)  # Usar prepared statements
            resource_tracker.track_resource(cursor, 'mysql_cursor')
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                return result
            
            conn.commit()
            return cursor.lastrowid
            
        except Error as e:
            print(f"Erro ao executar query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                resource_tracker.untrack_resource(cursor)
                try:
                    cursor.close()
                except:
                    pass
    
    def init_database(self):
        """Inicializa banco e tabelas MySQL"""
        temp_conn = None
        cursor = None
        try:
            # Primeiro conectar sem especificar database para criar se não existir
            temp_conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            resource_tracker.track_resource(temp_conn, 'mysql_temp_connection')
            
            cursor = temp_conn.cursor()
            resource_tracker.track_resource(cursor, 'mysql_temp_cursor')
            
            # Criar database se não existir (usando parâmetros seguros)
            # Nota: Nome do database deve ser validado antes da chamada
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.database):
                raise ValueError(f"Nome de database inválido: {self.database}")
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE `{self.database}`")
            
            # Criar tabelas
            self._create_tables(cursor)
            
            temp_conn.commit()
            
        except Error as e:
            print(f"Erro ao inicializar database: {e}")
            raise
        finally:
            if cursor:
                resource_tracker.untrack_resource(cursor)
                try:
                    cursor.close()
                except:
                    pass
            if temp_conn:
                resource_tracker.untrack_resource(temp_conn)
                try:
                    temp_conn.close()
                except:
                    pass
            
            print("Database MySQL inicializado com sucesso")
    
    def _create_tables(self, cursor):
        """Cria todas as tabelas necessárias"""
        
        # Tabela usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                setor VARCHAR(100) NOT NULL,
                funcao VARCHAR(100) NOT NULL,
                nivel_acesso VARCHAR(100) NOT NULL,
                saldo_ferias INT DEFAULT 12,
                data_cadastro DATE DEFAULT (CURRENT_DATE),
                data_admissao DATE DEFAULT (CURRENT_DATE),
                ultima_renovacao DATE DEFAULT (CURRENT_DATE),
                INDEX idx_email (email),
                INDEX idx_setor (setor)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabela ferias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                dias_utilizados INT NOT NULL,
                status VARCHAR(50) DEFAULT 'Aprovada',
                data_registro DATE DEFAULT (CURRENT_DATE),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_data_inicio (data_inicio),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabela auditoria_saldo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_saldo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                usuario_id INT NOT NULL,
                usuario_responsavel_id INT,
                usuario_responsavel_nome VARCHAR(255),
                motivo TEXT NOT NULL,
                valor_anterior INT NOT NULL,
                valor_novo INT NOT NULL,
                tipo_operacao VARCHAR(100) NOT NULL,
                detalhes_adicionais TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_data_hora (data_hora),
                INDEX idx_tipo_operacao (tipo_operacao)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        print("Tabelas MySQL criadas com sucesso")
    
    def close(self):
        """Fecha conexão MySQL"""
        if self.connection and self.connection.is_connected():
            resource_tracker.untrack_resource(self.connection)
            self.connection.close()
            self.connection = None
            print("Conexão MySQL fechada")