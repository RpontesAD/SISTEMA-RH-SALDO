# 🚀 Deploy no Streamlit Cloud - RPONTES Sistema RH

## Pré-requisitos

### 1. Banco MySQL Remoto
Você precisa de um banco MySQL acessível pela internet. Opções:

**🔹 Gratuitas:**
- [PlanetScale](https://planetscale.com) - 5GB gratuito
- [Railway MySQL](https://railway.app) - $5/mês
- [Aiven MySQL](https://aiven.io) - Trial gratuito

**🔹 Pagas:**
- AWS RDS MySQL
- Google Cloud SQL
- Azure Database for MySQL

### 2. Configurar Banco Remoto

```sql
-- Criar banco e usuário
CREATE DATABASE sistema_ferias_rh;
CREATE USER 'rpontes_user'@'%' IDENTIFIED BY 'senha_super_forte_123';
GRANT ALL PRIVILEGES ON sistema_ferias_rh.* TO 'rpontes_user'@'%';
FLUSH PRIVILEGES;
```

## Passos do Deploy

### 1. Preparar Repositório GitHub

```bash
# 1. Criar repositório no GitHub
# 2. Fazer push do projeto

git init
git add .
git commit -m "Deploy inicial - Sistema RH RPONTES"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/rpontes-sistema-rh.git
git push -u origin main
```

### 2. Deploy no Streamlit Cloud

1. **Acesse:** https://share.streamlit.io
2. **Login** com GitHub
3. **New app** → **From existing repo**
4. **Selecione** seu repositório
5. **Main file path:** `app.py`
6. **Advanced settings** → **Secrets**

### 3. Configurar Secrets (IMPORTANTE!)

No Streamlit Cloud, adicione estas variáveis em **Secrets**:

```toml
# .streamlit/secrets.toml (será criado automaticamente)

[mysql]
host = "seu-host-mysql.com"
port = 3306
database = "sistema_ferias_rh"
user = "rpontes_user"
password = "senha_super_forte_123"

[app]
secret_key = "chave-secreta-256-bits-muito-segura"
admin_email = "admin@rpontes.com"
admin_password = "senha_admin_muito_forte"
debug_mode = false
```

### 4. Atualizar Código para Secrets

O código já está preparado para usar `st.secrets` automaticamente quando detectar o ambiente Streamlit Cloud.

### 5. Testar Deploy

Após o deploy:
1. **Aguarde** build completar (2-5 minutos)
2. **Acesse** URL fornecida
3. **Teste login:** admin@rpontes.com / sua_senha_admin
4. **Verifique** todas as funcionalidades

## Troubleshooting

### ❌ Erro de Conexão MySQL
- Verifique se o host MySQL permite conexões externas
- Confirme usuário/senha nos secrets
- Teste conexão local primeiro

### ❌ Erro de Dependências
- Verifique `requirements.txt`
- Remova versões específicas se necessário
- Use `pip freeze > requirements.txt` local

### ❌ Erro de Secrets
- Secrets devem estar em formato TOML
- Não use aspas duplas aninhadas
- Reinicie app após alterar secrets

## Monitoramento

### Logs
- Acesse logs pelo painel Streamlit Cloud
- Monitore erros de conexão
- Verifique performance

### Backup
- Configure backup automático do MySQL
- Exporte dados regularmente
- Mantenha cópia local de desenvolvimento

## Próximos Passos

1. **Domínio Personalizado** (opcional)
2. **SSL Certificate** (automático)
3. **Monitoramento** com alertas
4. **Backup Automático** configurado

## Suporte

- **Streamlit Docs:** https://docs.streamlit.io/streamlit-cloud
- **MySQL Docs:** https://dev.mysql.com/doc/
- **Suporte:** Verifique logs primeiro, depois GitHub Issues