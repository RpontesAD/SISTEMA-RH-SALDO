# Manual Técnico - Sistema de Gestão de Férias RPONTES

## 🏗️ Arquitetura Técnica

### Stack Tecnológico
- **Frontend:** Streamlit 1.28+
- **Backend:** Python 3.8+
- **Banco de Dados:** PostgreSQL (Supabase)
- **Conexão:** psycopg2-binary
- **Autenticação:** bcrypt 4.0+
- **Deploy:** Streamlit Cloud
- **Versionamento:** Git/GitHub

### Padrões Arquiteturais
- **Clean Architecture:** Separação clara de responsabilidades
- **Repository Pattern:** Abstração de acesso a dados
- **Service Layer:** Orquestração de regras de negócio
- **Dependency Injection:** Inversão de dependências

## 📁 Estrutura Detalhada do Código

### Camada de Interface (`src/menus/`)
```python
# Responsabilidades:
# - Renderização de componentes visuais
# - Captura de entrada do usuário
# - Delegação para camada de serviços
# - Exibição de resultados

# Arquivos principais:
- cadastro_colaborador.py    # Interface de cadastro
- gerenciar_colaboradores.py # CRUD de colaboradores
- gerenciar_ferias.py       # Gestão de férias
- dashboard.py              # Relatórios e métricas
```

### Camada de Serviços (`src/services/`)
```python
# Responsabilidades:
# - Orquestração de operações
# - Coordenação entre regras e dados
# - Preparação de dados para UI
# - Tratamento de erros

class ColaboradorService:
    def cadastrar_colaborador(self, dados):
        # 1. Validar dados
        # 2. Aplicar regras de negócio
        # 3. Persistir no banco
        # 4. Retornar resultado
        
class FeriasService:
    def cadastrar_ferias(self, dados):
        # 1. Validar período
        # 2. Verificar saldo
        # 3. Aplicar regras
        # 4. Salvar no banco
```

### Camada de Regras (`src/core/`)
```python
# Responsabilidades:
# - Implementação de regras de negócio
# - Validações específicas do domínio
# - Cálculos e algoritmos
# - Lógica independente de infraestrutura

class RegrasFerias:
    @staticmethod
    def validar_periodo(inicio, fim):
        # Validação de período válido
        
    @staticmethod
    def validar_antecedencia(data_inicio, nivel_usuario):
        # Validação de antecedência mínima
        
class RegrasSaldo:
    @staticmethod
    def calcular_saldo_com_pendentes(saldo_atual, pendentes):
        # Cálculo de saldo considerando pendências
```

### Camada de Dados (`src/database/`)
```python
# Responsabilidades:
# - Acesso ao banco de dados
# - Operações CRUD
# - Transações
# - Mapeamento objeto-relacional

class SimplePsycopg2Database:
    def authenticate_user(self, email, senha):
        # Autenticação com bcrypt via PostgreSQL
        
    def create_user(self, dados):
        # Criação de usuário com ativo=True
        
    def add_ferias(self, dados):
        # Cadastro de férias com validação de saldo
        
    def inativar_usuario(self, user_id):
        # Inativação preservando dados
        
    def create_aviso(self, dados):
        # Sistema de avisos com destinatários
```

## 🗄️ Modelo de Dados

### Diagrama ER
```
usuarios (1) -----> (N) ferias
    |                   |
    id                  usuario_id
    nome                data_inicio
    email               data_fim
    senha_hash          dias_utilizados
    setor               status
    funcao              data_registro
    nivel_acesso
    saldo_ferias
    data_cadastro
    data_admissao
    ativo               -- NOVO: controle inativação

avisos (1) -----> (N) avisos_destinatarios
    |                   |
    id                  aviso_id
    titulo              usuario_id
    conteudo            lido
    autor_id            data_leitura
    data_criacao        oculto
    destinatarios_tipo
    destinatarios_ids
```

### Relacionamentos
- **1:N** - Um usuário pode ter múltiplas férias
- **FK** - ferias.usuario_id referencia usuarios.id
- **Cascade** - Exclusão de usuário remove suas férias

### Índices
```sql
-- Índices para performance PostgreSQL
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_ativo ON usuarios(ativo);
CREATE INDEX idx_ferias_usuario ON ferias(usuario_id);
CREATE INDEX idx_ferias_status ON ferias(status);
CREATE INDEX idx_ferias_data ON ferias(data_inicio, data_fim);
CREATE INDEX idx_avisos_autor ON avisos(autor_id);
CREATE INDEX idx_avisos_dest_usuario ON avisos_destinatarios(usuario_id);
CREATE INDEX idx_avisos_dest_aviso ON avisos_destinatarios(aviso_id);
```

## 🔐 Segurança

### Autenticação
```python
# Hash de senhas com bcrypt
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Controle de Acesso
```python
# Decorador para controle de acesso
def require_level(required_level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_level = st.session_state.get('user', {}).get('nivel_acesso')
            if not has_permission(user_level, required_level):
                st.error("Acesso negado")
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Hierarquia de níveis
NIVEL_HIERARCHY = {
    'colaborador': 1,
    'coordenador': 2,
    'diretoria': 3,
    'master': 4
}
```

### Validação de Entrada
```python
# Sanitização e validação
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    # Remove caracteres perigosos
    return re.sub(r'[<>"\']', '', text.strip())
```

## 📊 Performance e Otimização

### Caching
```python
# Cache de consultas frequentes
@st.cache_data(ttl=300)  # 5 minutos
def get_usuarios_cache():
    return database.get_users()

@st.cache_data(ttl=60)   # 1 minuto
def get_ferias_cache(user_id):
    return database.get_ferias_usuario(user_id)
```

### Paginação
```python
# Paginação para listas grandes
def paginate_results(data, page_size=50, page_num=1):
    start = (page_num - 1) * page_size
    end = start + page_size
    return data[start:end]
```

### Otimização de Queries
```python
# Queries otimizadas com índices
def get_ferias_by_period(start_date, end_date):
    query = """
    SELECT f.*, u.nome 
    FROM ferias f 
    JOIN usuarios u ON f.usuario_id = u.id 
    WHERE f.data_inicio >= ? AND f.data_fim <= ?
    ORDER BY f.data_inicio DESC
    """
    return pd.read_sql_query(query, conn, params=(start_date, end_date))
```

## 🔧 Configuração e Deploy

### Variáveis de Ambiente
```python
# Configurações PostgreSQL (Supabase)
import os
from urllib.parse import quote_plus

# Conexão PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# URL encoding para senhas especiais
def encode_password(password):
    return quote_plus(password)

# Configurações de segurança
SECRET_KEY = os.getenv('SECRET_KEY', 'default-key')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@rpontes.com')
```

### Docker (Opcional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### Streamlit Cloud
```toml
# .streamlit/config.toml
[server]
headless = true
port = 8501

[theme]
base = "dark"
primaryColor = "#ff6b6b"

# secrets.toml (não commitado)
DATABASE_URL = "postgresql://user:pass@host:port/db"
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🧪 Testes

### Estrutura de Testes
```python
# tests/test_regras_ferias.py
import unittest
from src.core.regras_ferias import RegrasFerias

class TestRegrasFerias(unittest.TestCase):
    def test_validar_periodo_valido(self):
        resultado = RegrasFerias.validar_periodo(
            date(2024, 1, 1), 
            date(2024, 1, 10)
        )
        self.assertTrue(resultado['valida'])
    
    def test_validar_periodo_invalido(self):
        resultado = RegrasFerias.validar_periodo(
            date(2024, 1, 10), 
            date(2024, 1, 1)
        )
        self.assertFalse(resultado['valida'])
```

### Testes de Integração
```python
# tests/test_integration.py
class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.db = SimplePsycopg2Database()  # PostgreSQL de teste
        
    def test_fluxo_completo_ferias(self):
        # 1. Criar usuário
        user_id = self.db.create_user(dados_usuario)
        
        # 2. Cadastrar férias
        ferias_id = self.db.add_ferias(user_id, dados_ferias)
        
        # 3. Aprovar férias
        self.db.update_ferias_status(ferias_id, 'Aprovado')
        
        # 4. Verificar saldo
        user = self.db.get_user(user_id)
        self.assertEqual(user['saldo_ferias'], saldo_esperado)
```

### Executar Testes
```bash
# Executar todos os testes
python -m pytest tests/

# Executar com coverage
python -m pytest --cov=src tests/

# Executar testes específicos
python -m pytest tests/test_regras_ferias.py -v
```

## 📈 Monitoramento e Logs

### Sistema de Logs
```python
# src/utils/error_handler.py
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sistema_rh.log'),
        logging.StreamHandler()
    ]
)

# Decorator para log de operações
def log_operation(operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Iniciando: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Sucesso: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Erro em {operation_name}: {str(e)}")
                raise
        return wrapper
    return decorator
```

### Métricas de Performance
```python
# Monitoramento de performance
import time
import psutil

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        if execution_time > 2.0:  # Log operações lentas
            logger.warning(f"Operação lenta: {func.__name__} - {execution_time:.2f}s")
            
        return result
    return wrapper
```

## 🔄 Backup e Recuperação

### Backup Automático
```python
# Backup automático do PostgreSQL
import subprocess
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"backups/rpontes_rh_{timestamp}.sql"
    
    os.makedirs('backups', exist_ok=True)
    
    # pg_dump para PostgreSQL
    cmd = f"pg_dump {DATABASE_URL} > {backup_path}"
    subprocess.run(cmd, shell=True, check=True)
    
    logger.info(f"Backup PostgreSQL criado: {backup_path}")
    return backup_path

# Backup via Supabase (recomendado)
def backup_supabase():
    # Supabase oferece backups automáticos
    # Configurar via dashboard do Supabase
    pass
```

### Recuperação de Dados
```python
def restore_database(backup_path):
    if os.path.exists(backup_path):
        # Restaurar PostgreSQL via psql
        cmd = f"psql {DATABASE_URL} < {backup_path}"
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"PostgreSQL restaurado de: {backup_path}")
        return True
    return False
```

## 🚀 Deploy e CI/CD

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m pytest tests/
```

### Versionamento
```bash
# Semantic Versioning
git tag -a v1.3.0 -m "Release version 1.3.0"
git push origin v1.3.0

# Changelog automático
git log --oneline --since="2024-01-01" > CHANGELOG.md
```

## 🔍 Debug e Troubleshooting

### Debug Mode
```python
# Ativar modo debug
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

if DEBUG_MODE:
    st.write("Debug Info:", {
        'session_state': dict(st.session_state),
        'user_agent': st.context.headers.get('user-agent'),
        'timestamp': datetime.now().isoformat()
    })
```

### Profiling
```python
# Profile de performance
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 funções
        
        return result
    return wrapper
```

### Health Check
```python
def health_check():
    checks = {
        'database': check_database_connection(),
        'disk_space': check_disk_space(),
        'memory': check_memory_usage(),
        'logs': check_log_files()
    }
    
    all_healthy = all(checks.values())
    return {'healthy': all_healthy, 'checks': checks}
```

## 📚 Referências Técnicas

### Documentação das Bibliotecas
- **Streamlit:** https://docs.streamlit.io/
- **Pandas:** https://pandas.pydata.org/docs/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **psycopg2:** https://www.psycopg.org/docs/
- **Supabase:** https://supabase.com/docs
- **bcrypt:** https://pypi.org/project/bcrypt/

### Padrões e Boas Práticas
- **Clean Architecture:** Robert C. Martin
- **Python PEP 8:** Style Guide
- **Git Flow:** Branching model
- **Semantic Versioning:** https://semver.org/

---

**Manual Técnico atualizado em:** Dezembro 2024  
**Versão do Sistema:** 2.0.0