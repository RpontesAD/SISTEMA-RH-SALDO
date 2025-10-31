# Módulo de Debug - Sistema RPONTES RH

## Estrutura da Pasta Debug

```
debug/
├── __init__.py              # Módulo principal com exports
├── debug_system.py          # Sistema central de logging
├── debug_panel.py           # Interface visual Streamlit
├── debug_config.py          # Configurações de debug
├── debug_list_error.py      # Script de diagnóstico
├── DEBUG_SUMMARY.md         # Documentação completa
└── README.md               # Este arquivo
```

## Arquivos Principais

### `debug_system.py`
- **Logger centralizado** com formatação padronizada
- **Classes de debug especializadas**:
  - `DebugManager`: Gerenciamento geral
  - `DatabaseDebugger`: Debug de banco de dados
  - `AuthDebugger`: Debug de autenticação
  - `BusinessLogicDebugger`: Debug de regras de negócio
- **Decorators automáticos** para instrumentação

### `debug_panel.py`
- **Interface visual** no Streamlit
- **Painel na sidebar** com controles
- **Visualização em tempo real** de logs e métricas
- **Exportação de dados** de debug

### `debug_config.py`
- **Configurações centralizadas** de debug
- **Controle por ambiente** (dev/test/prod)
- **Flags específicas** por componente
- **Proteção de dados sensíveis**

## Como Usar

### Importação Básica
```python
from debug import logger, DebugManager, debug_decorator
```

### Importação Completa
```python
from debug import (
    logger,
    DebugManager,
    DatabaseDebugger,
    AuthDebugger,
    debug_decorator,
    show_debug_panel
)
```

### Uso em Funções
```python
@debug_decorator()
def minha_funcao():
    logger.info("Executando função")
    return "resultado"
```

### Uso em Componentes Streamlit
```python
from debug import show_debug_panel, add_debug_to_page

def minha_pagina():
    add_debug_to_page("minha_pagina")
    # ... código da página
    show_debug_panel()  # Na sidebar
```

## Configuração

### Ativar/Desativar Debug
```python
from debug import set_debug_setting

# Desativar completamente
set_debug_setting("ENABLE_DEBUG", False)

# Ativar apenas database
set_debug_setting("DEBUG_DATABASE", True)
set_debug_setting("DEBUG_AUTH", False)
```

### Por Ambiente
```python
import os
os.environ["ENVIRONMENT"] = "production"  # Desativa debug
os.environ["ENVIRONMENT"] = "development"  # Ativa debug completo
```

## Logs Gerados

### Localização
- `logs/debug_sistema.log` - Log principal
- `logs/sistema_rh.log` - Log de operações

### Tipos de Log
- `INFO` - Operações principais
- `DEBUG` - Detalhes técnicos
- `WARNING` - Situações de atenção
- `ERROR` - Erros recuperáveis
- `CRITICAL` - Erros críticos

### Prefixos Especiais
- `DB_CONNECTION:` - Conexões de banco
- `AUTH_LOGIN:` - Tentativas de login
- `USER_ACTION:` - Ações dos usuários
- `STREAMLIT:` - Renderização de componentes

## Segurança

### Dados Protegidos
- ❌ Senhas nunca são logadas
- ❌ Dados sensíveis são mascarados
- ✅ Apenas metadados são capturados
- ✅ Logs podem ser desabilitados

### Controle de Acesso
- Painel visível apenas para usuários logados
- Configuração por ambiente
- Logs armazenados localmente

## Manutenção

### Limpeza de Logs
```python
from debug import show_debug_panel
# Use o botão "Limpar Logs" no painel
```

### Exportação de Debug
```python
from debug import show_debug_panel
# Use o botão "Exportar Debug" no painel
```

### Rotação Automática
- Máximo 50MB por arquivo
- 5 backups mantidos
- Limpeza automática de logs antigos

## Troubleshooting

### Problema: Debug não aparece
**Solução:** Verificar `DEBUG_SETTINGS["ENABLE_DEBUG"] = True`

### Problema: Logs não são salvos
**Solução:** Verificar permissões da pasta `logs/`

### Problema: Performance lenta
**Solução:** Reduzir nível de log ou desativar componentes específicos

### Problema: Imports não funcionam
**Solução:** Verificar se a pasta `debug/` está no Python path

## Desenvolvimento

### Adicionar Novo Debugger
1. Criar classe em `debug_system.py`
2. Adicionar ao `__init__.py`
3. Documentar no `DEBUG_SUMMARY.md`

### Adicionar Nova Configuração
1. Adicionar em `DEBUG_SETTINGS` no `debug_config.py`
2. Usar com `get_debug_setting("NOVA_CONFIG")`

### Adicionar Novo Painel
1. Criar função em `debug_panel.py`
2. Adicionar ao `__init__.py`
3. Integrar na interface principal

## Arquivos de Apoio

- `debug_list_error.py` - Script para diagnosticar erros de importação
- `DEBUG_SUMMARY.md` - Documentação completa do sistema implementado

Este módulo fornece **debug profissional e completo** para toda a aplicação RPONTES RH.