# Backup - Funcionalidade de Renovação Anual de Saldo

## 📋 Conteúdo do Backup

Este diretório contém todos os arquivos relacionados à funcionalidade de **Renovação Anual de Saldo** que foi desenvolvida e posteriormente removida do projeto principal.

### 📁 Arquivos Incluídos:

1. **`renovacao_saldo.py`** - Menu completo da renovação anual
2. **`renovacao_service.py`** - Serviço especializado para renovação
3. **`renovacao_anual.md`** - Documentação completa da funcionalidade
4. **`database_functions.sql`** - Funções do banco de dados (ver abaixo)

## 🔧 Funcionalidades Implementadas

### ✅ **Renovação Anual Completa:**
- Renovação de saldos por ano (2025 → 2026)
- Preservação de histórico por ano
- Backup automático antes da operação
- Rollback de emergência

### ✅ **Modo de Teste Seguro:**
- Simulação sem alterar dados
- Dados de teste fictícios
- Prévia detalhada da operação
- Verificações de segurança

### ✅ **Estrutura de Banco:**
- Tabela `renovacao_saldo` - Histórico de renovações
- Tabela `saldos_anuais` - Saldos por ano/colaborador
- Políticas RLS para Supabase
- Migração automática de dados

## 🗄️ Funções do Banco de Dados

As seguintes funções foram adicionadas ao `simple_psycopg2.py`:

```python
# Funções relacionadas à renovação anual:
- verificar_renovacao_ano()
- backup_saldos_usuarios()
- renovar_saldo_anual()
- get_historico_renovacoes()
- desfazer_ultima_renovacao()
- get_estatisticas_saldo()
- get_saldo_usuario_ano()
- get_historico_saldos_usuario()
- get_anos_disponiveis()
- migrar_saldos_existentes()
```

## 📊 Estrutura das Tabelas

### Tabela `renovacao_saldo`:
```sql
CREATE TABLE renovacao_saldo (
    id SERIAL PRIMARY KEY,
    ano INTEGER UNIQUE NOT NULL,
    saldo_padrao INTEGER NOT NULL,
    data_aplicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_responsavel_id INTEGER REFERENCES usuarios(id),
    backup_dados TEXT
);
```

### Tabela `saldos_anuais`:
```sql
CREATE TABLE saldos_anuais (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    ano INTEGER NOT NULL,
    saldo_inicial INTEGER NOT NULL,
    saldo_atual INTEGER NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, ano)
);
```

## 🔄 Como Reativar (Se Necessário)

### 1. **Restaurar Arquivos:**
```bash
# Copiar arquivos de volta
copy renovacao_anual_backup\renovacao_saldo.py src\menus\
copy renovacao_anual_backup\renovacao_service.py src\services\
```

### 2. **Atualizar Menu Principal:**
```python
# Em src/menus/__init__.py
from .renovacao_saldo import menu_renovacao_saldo

# Adicionar aba no menu_rh():
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Cadastrar Colaborador",
    "Gerenciar Férias", 
    "Gerenciar Colaboradores",
    "Renovação Anual",  # <- Adicionar
    "Relatórios"
])

with tab4:
    menu_renovacao_saldo()  # <- Adicionar
```

### 3. **Restaurar Funções do Banco:**
Adicionar as funções listadas acima ao arquivo `src/database/simple_psycopg2.py`

## 📅 Data de Remoção
**Dezembro 2025** - Funcionalidade removida a pedido do usuário

## 💡 Observações
- Funcionalidade estava 100% operacional
- Testes completos realizados
- Estrutura de dados segura implementada
- Pode ser reativada a qualquer momento

---

**Desenvolvido para:** Construtora RPONTES  
**Status:** Backup completo e funcional
