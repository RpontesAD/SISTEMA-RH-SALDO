# Sistema de Gestão de Férias - RPONTES

## 📋 Visão Geral

Sistema web desenvolvido em Python/Streamlit para controle e gestão de férias dos colaboradores da Construtora RPONTES. O sistema oferece interface intuitiva, controle de acesso por níveis e gestão completa do ciclo de vida das férias.

## 🚀 Tecnologias Utilizadas

- **Frontend:** Streamlit 
- **Backend:** Python 3.8+
- **Banco de Dados:** SQLite
- **Autenticação:** bcrypt
- **Deploy:** Streamlit Cloud

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
Gestão RH/
├── app.py                    # Ponto de entrada principal
├── requirements.txt          # Dependências Python
├── packages.txt             # Pacotes do sistema
├── .streamlit/              # Configurações Streamlit
│   └── config.toml         # Tema e configurações
├── src/                     # Código fonte
│   ├── app.py              # Aplicação principal
│   ├── auth.py             # Autenticação
│   ├── config.py           # Configurações básicas
│   ├── config_secure.py    # Configurações seguras
│   ├── core/               # Regras de negócio
│   │   ├── regras_ferias.py
│   │   └── regras_saldo.py
│   ├── database/           # Acesso a dados
│   │   └── sqlite_database.py
│   ├── menus/              # Interfaces de usuário
│   │   ├── cadastro_colaborador.py
│   │   ├── gerenciar_colaboradores.py
│   │   ├── gerenciar_ferias.py
│   │   └── dashboard.py
│   ├── services/           # Camada de serviços
│   │   ├── colaborador_service.py
│   │   └── ferias_service.py
│   └── utils/              # Utilitários
│       ├── constants.py
│       ├── validators.py
│       ├── formatters.py
│       └── error_handler.py
├── data/                   # Banco de dados
│   └── rpontes_rh.db      # SQLite
└── docs/                  # Documentação
    └── README.md          # Este arquivo
```

### Padrão Arquitetural

O sistema segue o padrão **Clean Architecture** com separação clara de responsabilidades:

1. **Camada de Interface (UI)** - `src/menus/`
2. **Camada de Serviços** - `src/services/`
3. **Camada de Regras de Negócio** - `src/core/`
4. **Camada de Dados** - `src/database/`

## 👥 Níveis de Acesso

### 🔑 Master (RH)
- **Permissões:** Acesso total ao sistema
- **Funcionalidades:**
  - Cadastrar/editar/excluir colaboradores
  - Gerenciar férias de todos os colaboradores
  - Aprovar/cancelar férias
  - Ajustar saldos manualmente
  - Visualizar relatórios completos

### 🏢 Diretoria
- **Permissões:** Visualização executiva
- **Funcionalidades:**
  - Dashboard executivo
  - Relatórios consolidados por setor
  - Métricas gerais do sistema

### 👨‍💼 Coordenador
- **Permissões:** Gestão do próprio setor
- **Funcionalidades:**
  - Visualizar colaboradores do setor
  - Acompanhar férias da equipe
  - Relatórios do setor

### 👤 Colaborador
- **Permissões:** Dados pessoais
- **Funcionalidades:**
  - Visualizar próprios dados
  - Histórico pessoal de férias
  - Consultar saldo disponível

## 📊 Funcionalidades Principais

### ✅ Gestão de Colaboradores
- **Cadastro completo** com dados pessoais e profissionais
- **Definição automática** de nível de acesso baseado na função
- **Controle de saldo** de férias individual
- **Filtros avançados** por nome, setor, função e saldo
- **Edição e exclusão** com confirmação

### ✅ Gestão de Férias
- **Cadastro sempre como "Pendente"** para posterior aprovação
- **Aprovação/Cancelamento** com ajuste automático de saldo
- **Exclusão** com devolução de dias se necessário
- **Histórico completo** de todas as férias
- **Validação de conflitos** de datas
- **Cálculo automático** de dias úteis

### ✅ Dashboard e Relatórios
- **Métricas em tempo real** de saldo e utilização
- **Relatórios por setor** e colaborador
- **Gráficos interativos** de distribuição
- **Exportação** de dados

### ✅ Controle de Saldo
- **Saldo padrão:** 12 dias por colaborador
- **Limites:** 0 a 30 dias
- **Ajuste automático** baseado no status das férias
- **Histórico de alterações**

## 🔐 Segurança

### Autenticação
- **Senhas criptografadas** com bcrypt
- **Email único** por colaborador
- **Sessões seguras** via Streamlit

### Validações
- **Campos obrigatórios** em todos os formulários
- **Validação de email** com regex
- **Controle de acesso** por nível de usuário
- **Sanitização** de entradas

### Auditoria
- **Logs detalhados** de operações críticas
- **Rastreamento** de alterações de saldo
- **Registro** de aprovações/cancelamentos

## 🗄️ Banco de Dados

### Estrutura SQLite

#### Tabela `usuarios`
```sql
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
```

#### Tabela `ferias`
```sql
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

## ⚙️ Regras de Negócio

### Férias
1. **Cadastro:** Sempre como "Pendente"
2. **Aprovação:** Desconta automaticamente do saldo
3. **Cancelamento:** Devolve dias ao saldo
4. **Exclusão:** Remove registro e ajusta saldo se necessário
5. **Conflitos:** Não permite sobreposição de períodos aprovados

### Saldo
1. **Padrão:** 12 dias por colaborador
2. **Mínimo:** 0 dias
3. **Máximo:** 30 dias
4. **Desconto:** Apenas férias "Aprovadas" descontam do saldo
5. **Ajuste:** Manual apenas por usuários Master

### Validações
1. **Antecedência:** 30 dias mínimos (exceto RH)
2. **Período:** Data fim deve ser posterior à data início
3. **Saldo:** Deve ter saldo suficiente para aprovação
4. **Email:** Deve ser único no sistema

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes)

### Instalação Local
```bash
# 1. Clonar repositório
git clone https://github.com/SEU_USUARIO/rpontes-rh.git
cd rpontes-rh

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar aplicação
streamlit run app.py
```

### Deploy no Streamlit Cloud
1. **Fork** do repositório no GitHub
2. Acesse https://share.streamlit.io/
3. **Conecte** sua conta GitHub
4. **Novo app:** selecione o repositório
5. **Configure:** Branch `main`, arquivo `app.py`

### Configuração de Secrets (Opcional)
```toml
USE_MYSQL = false
SQLITE_PATH = "data/rpontes_rh.db"
```

## 🎯 Como Usar

### Primeiro Acesso
1. **Acesse** a aplicação via navegador
2. **Faça login** com: admin@rpontes.com / admin123
3. **Cadastre colaboradores** na aba correspondente
4. **Configure** níveis de acesso conforme necessário

### Fluxo de Férias
1. **Cadastre férias** (sempre como Pendente)
2. **Aprove/Cancele** na aba "Gerenciar Status"
3. **Monitore saldos** no Dashboard
4. **Ajuste saldos** se necessário (apenas Master)

### Relatórios
1. **Acesse** a aba Dashboard
2. **Filtre** por setor ou período
3. **Visualize** métricas em tempo real
4. **Exporte** dados se necessário

## 🔧 Manutenção

### Backup
- **Automático:** Sistema mantém backup do SQLite
- **Manual:** Copiar arquivo `data/rpontes_rh.db`

### Logs
- **Localização:** `logs/sistema_rh.log`
- **Rotação:** Automática por tamanho
- **Níveis:** INFO, WARNING, ERROR, CRITICAL

### Monitoramento
- **Performance:** Logs de operações lentas
- **Erros:** Rastreamento completo de exceções
- **Uso:** Métricas de acesso e operações

## 🐛 Solução de Problemas

### Problemas Comuns

#### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Porta Ocupada
```bash
streamlit run app.py --server.port 8502
```

#### Banco Corrompido
1. Parar aplicação
2. Renomear `data/rpontes_rh.db`
3. Reiniciar aplicação (criará novo banco)
4. Restaurar dados do backup

### Logs de Debug
```python
# Ativar logs detalhados
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📈 Métricas e KPIs

### Indicadores Principais
- **Taxa de utilização** de férias por setor
- **Saldo médio** por colaborador
- **Tempo médio** de aprovação
- **Distribuição** de férias por mês

### Relatórios Disponíveis
- **Por Colaborador:** Histórico individual completo
- **Por Setor:** Consolidado departamental
- **Por Período:** Análise temporal
- **Executivo:** Visão geral da empresa

## 🔄 Versionamento

### Histórico de Versões
- **v1.0.0** - Sistema base com MySQL
- **v1.1.0** - Migração para SQLite
- **v1.2.0** - Deploy Streamlit Cloud
- **v1.3.0** - Melhorias de UX e performance

### Roadmap
- [ ] Notificações por email
- [ ] Integração com calendário
- [ ] App mobile
- [ ] API REST
- [ ] Relatórios avançados

## 👨‍💻 Desenvolvimento

### Contribuição
1. **Fork** do projeto
2. **Crie** branch para feature
3. **Implemente** com testes
4. **Submeta** pull request

### Padrões de Código
- **PEP 8** para Python
- **Docstrings** em todas as funções
- **Type hints** quando possível
- **Testes unitários** para regras críticas

### Estrutura de Commits
```
tipo(escopo): descrição

feat(auth): adicionar autenticação 2FA
fix(ferias): corrigir cálculo de dias úteis
docs(readme): atualizar documentação
```

## 📞 Suporte

### Contato
- **Email:** suporte@rpontes.com
- **Documentação:** `/docs`
- **Logs:** `/logs`

### FAQ
**P: Como resetar senha de usuário?**
R: Apenas usuários Master podem alterar senhas via interface de gerenciamento.

**P: Como fazer backup dos dados?**
R: Copie o arquivo `data/rpontes_rh.db` para local seguro.

**P: Sistema suporta quantos usuários?**
R: SQLite suporta até 1000 usuários simultâneos confortavelmente.

---

**Sistema desenvolvido para uso interno da Construtora RPONTES**  
**Versão:** 1.3.0 | **Última atualização:** Novembro 2024