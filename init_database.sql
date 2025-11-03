-- Script de inicialização do banco MySQL para produção
-- Execute este script no seu banco MySQL remoto

-- Criar banco (se não existir)
CREATE DATABASE IF NOT EXISTS sistema_ferias_rh;
USE sistema_ferias_rh;

-- Criar usuário para produção (substitua pela sua senha forte)
-- CREATE USER 'rpontes_user'@'%' IDENTIFIED BY 'SUA_SENHA_FORTE_AQUI';
-- GRANT ALL PRIVILEGES ON sistema_ferias_rh.* TO 'rpontes_user'@'%';
-- FLUSH PRIVILEGES;

-- As tabelas serão criadas automaticamente pelo sistema
-- quando ele inicializar pela primeira vez

-- Verificar se as tabelas foram criadas
-- SHOW TABLES;