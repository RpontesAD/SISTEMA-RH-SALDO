# API Reference - Sistema de Gestão de Férias RPONTES

## 📋 Visão Geral da API Interna

Este documento descreve as interfaces internas do sistema, incluindo classes, métodos e estruturas de dados utilizadas.

## 🗄️ Database Layer

### SQLiteDatabase

Classe principal para acesso ao banco de dados SQLite.

#### Inicialização
```python
from src.database.sqlite_database import SQLiteDatabase

db = SQLiteDatabase(db_path="data/rpontes_rh.db")
```

#### Métodos de Usuários

##### `authenticate_user(email: str, senha: str) -> dict | None`
Autentica usuário no sistema.

**Parâmetros:**
- `email` (str): Email do usuário
- `senha` (str): Senha em texto plano

**Retorno:**
```python
{
    'id': int,
    'nome': str,
    'email': str,
    'setor': str,
    'funcao': str,
    'nivel_acesso': str,
    'saldo_ferias': int
}
```

**Exemplo:**
```python
user = db.authenticate_user("admin@rpontes.com", "admin123")
if user:
    print(f"Login realizado: {user['nome']}")
```

##### `create_user(...) -> bool`
Cria novo usuário no sistema.

**Parâmetros:**
- `nome` (str): Nome completo
- `email` (str): Email único
- `senha` (str): Senha em texto plano
- `setor` (str): Setor do colaborador
- `funcao` (str): Função/cargo
- `nivel_acesso` (str, opcional): Nível de acesso (padrão: "colaborador")
- `saldo_ferias` (int, opcional): Saldo inicial (padrão: 12)
- `data_admissao` (date, opcional): Data de admissão

**Retorno:** `bool` - True se criado com sucesso

##### `get_users(setor: str = None) -> pandas.DataFrame`
Obtém lista de usuários.

**Parâmetros:**
- `setor` (str, opcional): Filtrar por setor específico

**Retorno:** DataFrame com colunas:
- `id`, `nome`, `email`, `setor`, `funcao`, `nivel_acesso`, `saldo_ferias`, `data_cadastro`, `data_admissao`

##### `update_user(user_id: int, ...) -> bool`
Atualiza dados do usuário.

##### `delete_user(user_id: int) -> bool`
Exclui usuário do sistema.

##### `update_saldo_ferias(user_id: int, novo_saldo: int, ...) -> bool`
Atualiza saldo de férias do usuário.

#### Métodos de Férias

##### `add_ferias(...) -> bool`
Adiciona período de férias.

**Parâmetros:**
- `usuario_id` (int): ID do usuário
- `data_inicio` (date): Data de início
- `data_fim` (date): Data de fim
- `status` (str, opcional): Status inicial (padrão: "Pendente")
- `usuario_nivel` (str, opcional): Nível do usuário

##### `get_ferias_usuario(usuario_id: int) -> pandas.DataFrame`
Obtém férias de um usuário específico.

##### `get_all_ferias(...) -> pandas.DataFrame`
Obtém todas as férias do sistema.

##### `update_ferias_status(ferias_id: int, novo_status: str, ...) -> bool`
Atualiza status das férias.

##### `delete_ferias(ferias_id: int, ...) -> bool`
Exclui período de férias.

## 🔧 Services Layer

### ColaboradorService

Serviço para operações relacionadas a colaboradores.

#### Inicialização
```python
from src.services.colaborador_service import ColaboradorService

service = ColaboradorService(users_db, ferias_db)
```

#### Métodos Principais

##### `cadastrar_colaborador(dados: dict) -> dict`
Cadastra novo colaborador com validações.

**Parâmetros:**
```python
dados = {
    'nome': str,
    'email': str,
    'senha': str,
    'setor': str,
    'funcao': str,
    'data_admissao': date,
    'saldo_ferias': int
}
```

**Retorno:**
```python
{
    'sucesso': bool,
    'mensagem': str,
    'erro': str,  # se sucesso = False
    'tipo': str   # tipo do erro
}
```

##### `obter_colaboradores_filtrados(filtros: dict) -> dict`
Obtém colaboradores com filtros aplicados.

##### `atualizar_colaborador(user_id: int, dados: dict) -> dict`
Atualiza dados do colaborador.

##### `excluir_colaborador(user_id: int) -> dict`
Exclui colaborador do sistema.

### FeriasService

Serviço para operações de férias.

#### Métodos Principais

##### `cadastrar_ferias(...) -> dict`
Cadastra férias com validações completas.

**Parâmetros:**
- `usuario_id` (int): ID do usuário
- `data_inicio` (date): Data de início
- `data_fim` (date): Data de fim
- `status` (str): Status das férias
- `usuario_nivel` (str): Nível do usuário

**Retorno:**
```python
{
    'sucesso': bool,
    'mensagem': str,
    'dias_uteis': int,  # se sucesso = True
    'erro': str,        # se sucesso = False
    'tipo': str,        # tipo do erro
    'detalhes': dict    # detalhes específicos
}
```

##### `obter_informacoes_saldo(user_id: int) -> dict`
Obtém informações completas de saldo.

**Retorno:**
```python
{
    'sucesso': bool,
    'saldo_atual': int,
    'dias_pendentes': int,
    'saldo_se_aprovadas': int,
    'tem_pendencias': bool,
    'saldo_suficiente': bool
}
```

##### `aprovar_ferias(ferias_id: int) -> dict`
Aprova período de férias específico.

##### `cancelar_ferias(ferias_id: int) -> dict`
Cancela período de férias específico.

##### `excluir_ferias(ferias_id: int) -> dict`
Exclui período de férias.

## 🧠 Core Layer

### RegrasFerias

Classe com regras de negócio para férias.

#### Métodos Estáticos

##### `validar_periodo(data_inicio: date, data_fim: date) -> dict`
Valida se o período de férias é válido.

**Retorno:**
```python
{
    'valida': bool,
    'mensagem': str,
    'dias_corridos': int,
    'data_inicio': date,
    'data_fim': date
}
```

##### `validar_antecedencia(data_inicio: date, usuario_nivel: str) -> dict`
Valida antecedência mínima para férias.

##### `validar_saldo_suficiente(saldo_atual: int, dias_solicitados: int, status: str) -> dict`
Valida se há saldo suficiente.

##### `calcular_impacto_aprovacao(saldo_atual: int, dias_utilizados: int) -> dict`
Calcula impacto da aprovação no saldo.

### RegrasSaldo

Classe com regras de saldo de férias.

##### `calcular_saldo_com_pendentes(saldo_atual: int, pendentes: list) -> dict`
Calcula saldo considerando férias pendentes.

**Retorno:**
```python
{
    'saldo_atual': int,
    'dias_pendentes': int,
    'saldo_se_aprovadas': int,
    'tem_pendencias': bool,
    'saldo_suficiente_para_pendentes': bool,
    'detalhes_pendentes': list
}
```

##### `validar_limites_saldo(novo_saldo: int) -> dict`
Valida se o saldo está dentro dos limites permitidos.

##### `calcular_ajuste_necessario(saldo_atual: int, operacao: str, dias: int) -> dict`
Calcula ajuste necessário no saldo.

## 🛠️ Utils Layer

### Validators

Funções de validação de dados.

##### `validar_email(email: str) -> bool`
Valida formato de email.

##### `validar_senha(senha: str) -> dict`
Valida força da senha.

**Retorno:**
```python
{
    'valida': bool,
    'mensagem': str,
    'pontuacao': int,
    'requisitos': {
        'tamanho': bool,
        'maiuscula': bool,
        'minuscula': bool,
        'numero': bool,
        'especial': bool
    }
}
```

##### `validar_nome(nome: str) -> bool`
Valida formato do nome.

### Formatters

Funções de formatação de dados.

##### `formatar_data_brasileira(data: date) -> str`
Formata data no padrão brasileiro (DD/MM/AAAA).

##### `formatar_periodo_ferias(data_inicio: date, data_fim: date) -> str`
Formata período de férias para exibição.

##### `formatar_saldo_ferias(saldo: int) -> str`
Formata saldo de férias com unidade.

### Constants

Constantes do sistema.

```python
SETORES = [
    "ASSISTÊNCIA TÉCNICA",
    "GESTÃO DE PESSOAS (RH)",
    "FINANCEIRO",
    # ...
]

FUNCOES = [
    "Analista",
    "Assistente",
    # ...
]

STATUS_FERIAS = {
    "APROVADA": "Aprovada",
    "PENDENTE": "Pendente",
    "CANCELADA": "Cancelada",
    "REJEITADA": "Rejeitada"
}

NIVEIS_ACESSO = {
    "master": "RH - Acesso Total",
    "diretoria": "Diretoria - Relatórios Executivos",
    "coordenador": "Coordenador - Gestão do Setor",
    "colaborador": "Colaborador - Visualização Pessoal"
}
```

## 🔍 Error Handling

### Exceções Customizadas

##### `SystemError`
Erro base do sistema.

##### `DatabaseError`
Erro de banco de dados.

##### `ValidationError`
Erro de validação de dados.

##### `AuthenticationError`
Erro de autenticação.

##### `BusinessRuleError`
Erro de regra de negócio.

### Decorators

##### `@handle_critical_operation(operation_name: str)`
Decorator para operações críticas com tratamento de erro.

##### `@safe_execute`
Execução segura de funções com captura de exceções.

## 📊 Data Structures

### User Object
```python
{
    'id': int,
    'nome': str,
    'email': str,
    'setor': str,
    'funcao': str,
    'nivel_acesso': str,  # 'master', 'diretoria', 'coordenador', 'colaborador'
    'saldo_ferias': int,
    'data_cadastro': datetime,
    'data_admissao': date
}
```

### Ferias Object
```python
{
    'id': int,
    'usuario_id': int,
    'data_inicio': date,
    'data_fim': date,
    'dias_utilizados': int,
    'status': str,  # 'Pendente', 'Aprovado', 'Rejeitado'
    'data_registro': datetime
}
```

### Service Response
```python
{
    'sucesso': bool,
    'mensagem': str,        # mensagem de sucesso
    'erro': str,           # mensagem de erro (se sucesso = False)
    'tipo': str,           # tipo do erro
    'detalhes': dict,      # detalhes específicos
    'dados': any           # dados retornados (se aplicável)
}
```

## 🔧 Configuration

### Environment Variables
```python
# Banco de dados
USE_MYSQL = bool           # Usar MySQL (False = SQLite)
SQLITE_PATH = str          # Caminho do arquivo SQLite

# Segurança
SECRET_KEY = str           # Chave secreta da aplicação
ADMIN_EMAIL = str          # Email do administrador
ADMIN_PASSWORD = str       # Senha do administrador

# Sistema
DEBUG_MODE = bool          # Modo debug
APP_TITLE = str           # Título da aplicação
```

### Database Schema
```sql
-- Tabela de usuários
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    setor TEXT NOT NULL,
    funcao TEXT NOT NULL,
    nivel_acesso TEXT DEFAULT 'colaborador',
    saldo_ferias INTEGER DEFAULT 12,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_admissao DATE
);

-- Tabela de férias
CREATE TABLE ferias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    dias_utilizados INTEGER NOT NULL,
    status TEXT DEFAULT 'Pendente',
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

## 📝 Usage Examples

### Exemplo Completo: Cadastrar e Aprovar Férias
```python
from src.database.sqlite_database import SQLiteDatabase
from src.services.ferias_service import FeriasService
from datetime import date

# Inicializar
db = SQLiteDatabase()
service = FeriasService(db, db)

# 1. Cadastrar férias
resultado = service.cadastrar_ferias(
    usuario_id=1,
    data_inicio=date(2024, 12, 20),
    data_fim=date(2024, 12, 30),
    status="Pendente",
    usuario_nivel="colaborador"
)

if resultado['sucesso']:
    print(f"Férias cadastradas: {resultado['mensagem']}")
    
    # 2. Aprovar férias
    ferias_id = 1  # ID das férias cadastradas
    aprovacao = service.aprovar_ferias(ferias_id)
    
    if aprovacao['sucesso']:
        print(f"Férias aprovadas: {aprovacao['mensagem']}")
    else:
        print(f"Erro na aprovação: {aprovacao['erro']}")
else:
    print(f"Erro no cadastro: {resultado['erro']}")
```

### Exemplo: Consultar Saldo
```python
# Obter informações de saldo
saldo_info = service.obter_informacoes_saldo(user_id=1)

if saldo_info['sucesso']:
    print(f"Saldo atual: {saldo_info['saldo_atual']} dias")
    print(f"Dias pendentes: {saldo_info['dias_pendentes']} dias")
    print(f"Saldo após aprovações: {saldo_info['saldo_se_aprovadas']} dias")
else:
    print(f"Erro: {saldo_info['erro']}")
```

---

**API Reference atualizada em:** Novembro 2024  
**Versão do Sistema:** 1.3.0