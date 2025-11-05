# Guia de Deploy - Sistema RPONTES

## 🚀 Deploy no Streamlit Cloud

### 1. Preparação
- Sistema já configurado para PostgreSQL (Supabase)
- Arquivo `requirements.txt` atualizado
- Configurações em `.streamlit/secrets.toml` (apenas local)

### 2. Configurar Secrets no Streamlit Cloud
No painel do Streamlit Cloud, adicionar em **Secrets**:

```toml
[connections.postgresql]
dialect = "postgresql"
host = "aws-1-us-east-2.pooler.supabase.com"
port = 5432
database = "postgres"
username = "postgres.nmqhnqhizkxkffrwwwmv"
password = "Rpontes@2026"
```

### 3. Deploy
1. Fazer push do código para GitHub
2. Conectar repositório no Streamlit Cloud
3. Definir `app.py` como arquivo principal
4. Aguardar deploy automático

### 4. Verificações Pós-Deploy
- ✅ Login com admin@rpontes.com / admin123
- ✅ Cadastro de colaboradores
- ✅ Gerenciamento de férias
- ✅ Relatórios funcionando

## 🔧 Configurações de Produção

### Banco de Dados
- **Tipo:** PostgreSQL via Supabase
- **Host:** aws-1-us-east-2.pooler.supabase.com
- **Porta:** 5432
- **Database:** postgres

### Segurança
- Senhas criptografadas com bcrypt
- Conexão SSL com Supabase
- Validação de entrada em todos os formulários

### Performance
- Connection pooling otimizado
- Queries indexadas
- Cache de dados quando apropriado

## 📊 Monitoramento

### Logs Disponíveis
- `logs/sistema_rh.log` - Log geral do sistema
- `logs/operations.log` - Operações de CRUD
- `logs/security.log` - Eventos de segurança
- `logs/audit.log` - Auditoria de alterações

### Métricas Importantes
- Tempo de resposta das queries
- Número de usuários ativos
- Operações de férias por dia
- Erros de conexão com banco

## 🆘 Troubleshooting

### Erro de Conexão com Banco
1. Verificar se Supabase está online
2. Validar credenciais nos secrets
3. Checar logs de conexão

### Performance Lenta
1. Verificar queries no PostgreSQL
2. Analisar logs de performance
3. Otimizar consultas se necessário

### Erro de Autenticação
1. Verificar se admin existe no banco
2. Resetar senha se necessário
3. Validar hash bcrypt

---
**Sistema pronto para produção** ✅