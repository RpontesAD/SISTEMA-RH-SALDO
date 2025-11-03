# Deploy no Streamlit Cloud

## Passos para Deploy

### 1. Preparar Repositório Git
```bash
git init
git add .
git commit -m "Sistema RH RPONTES - Deploy inicial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/rpontes-rh.git
git push -u origin main
```

### 2. Configurar Streamlit Cloud
1. Acesse https://share.streamlit.io/
2. Conecte sua conta GitHub
3. Clique em "New app"
4. Selecione o repositório: `SEU_USUARIO/rpontes-rh`
5. Branch: `main`
6. Main file path: `app.py`

### 3. Configurar Secrets (Opcional)
No painel do Streamlit Cloud, adicione em "Secrets":
```toml
USE_MYSQL = false
SQLITE_PATH = "data/rpontes_rh.db"

[app]
secret_key = "sua-chave-secreta-aqui"
admin_email = "admin@rpontes.com"
admin_password = "admin123"
```

## Arquivos Importantes para Deploy

- ✅ `requirements.txt` - Dependências Python
- ✅ `packages.txt` - Pacotes do sistema (vazio para SQLite)
- ✅ `.streamlit/config.toml` - Configurações do Streamlit
- ✅ `.streamlit/secrets.toml` - Secrets locais (não commitado)
- ✅ `app.py` - Arquivo principal

## Credenciais Padrão
- **Email:** admin@rpontes.com
- **Senha:** admin123

## Banco de Dados
- **Tipo:** SQLite (arquivo local)
- **Localização:** `data/rpontes_rh.db`
- **Backup:** Automático no sistema

## URL do Deploy
Após o deploy, a URL será: `https://SEU_APP_NAME.streamlit.app`