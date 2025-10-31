# Sistema de Gestão de Férias - RPONTES

Sistema interno para controle de férias dos colaboradores da Construtora RPONTES.

## Status do Projeto

✅ **SISTEMA OPERACIONAL** - Taxa de Sucesso: 71.4%

### Funcionalidades Testadas
- ✅ Autenticação e Login
- ✅ Validação de Dados
- ✅ Integridade do Banco
- ✅ Cadastro de Colaboradores
- ✅ Gerenciamento de Férias
- ✅ Dashboard e Relatórios
- ⚠️ Sistema de Alertas (temporariamente desabilitado)

## Como Executar o Projeto

### Passo 1: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Passo 2: Executar a Aplicacao
```bash
    python -m streamlit run app.py
```

### Passo 3: Acessar no Navegador
- URL: http://localhost:8501
- # Sistema de Gestão de Férias - RPONTES

Sistema interno para controle de férias dos colaboradores da Construtora RPONTES.

## 🚀 Como Executar

1. **Configurar MySQL**: Certifique-se que o MySQL está rodando na porta 3306
2. **Instalar dependências**: `pip install -r requirements.txt`
3. **Executar aplicação**: `streamlit run app.py`
4. **Fazer login**: admin@rpontes.com / admin123

## 📊 Níveis de Acesso

| Nível | Abas | Funcionalidades |
|--------|------|----------------|
| **Master (RH)** | 4 | Acesso total: cadastro, gestão, relatórios |
| **Diretoria** | 2 | Área pessoal + relatórios executivos |
| **Coordenador** | 2 | Área pessoal + gestão do setor |
| **Colaborador** | 1 | Apenas área pessoal |

## 🛠️ Tecnologias

- **Streamlit** - Interface web
- **MySQL** - Banco de dados
- **Python 3.8+** - Backend
- **bcrypt** - Segurança

## ⚙️ Funcionalidades Principais

- ✅ **Cadastro de colaboradores** com validação
- ✅ **Gestão de férias** com detecção de conflitos
- ✅ **Controle de saldo** (0-30 dias)
- ✅ **Relatórios** em tempo real
- ✅ **Interface hierarquizada** por nível de acesso
- ✅ **Segurança** com autenticação e criptografia

## 🔧 Solução de Problemas

```bash
# Erro de dependências
pip install -r requirements.txt

# Porta ocupada
streamlit run app.py --server.port 8502

# Executar testes
python tests/run_all_tests.py
```

## 📋 Regras de Negócio

- **Saldo**: 0-30 dias por colaborador
- **Status**: Pendente → Aprovada/Cancelada
- **Validação**: Detecção de conflitos de datas
- **Segurança**: Email único + senhas criptografadas

## 📊 Banco de Dados

- **Host**: localhost:3306
- **Database**: sistema_ferias_rh
- **Tabelas**: usuarios, ferias, auditoria_saldo

# Estrutura do Projeto - Sistema de Férias

## 📁 Organização Simplificada

```
SISTEMA SALDO DE FERIAS - RH/
├── app.py                    # Ponto de entrada principal
├── requirements.txt          # Dependências Python
├── REGRAS_NEGOCIO.md        # Regras de negócio documentadas
├── ESTRUTURA_PROJETO.md     # Este arquivo
├── README_TECNICO.md        # Documentação técnica
│
├── src/                     # Código fonte principal
│   ├── app.py               # Aplicação Streamlit
│   ├── config.py            # Configurações centralizadas
│   ├── auth.py              # Autenticação de usuários
│   ├── styles.py            # Estilos da interface
│   │
│   ├── core/                # Lógica de negócio 
│   │   ├── __init__.py
│   │   ├── regras_ferias.py # Regras de férias isoladas
│   │   ├── regras_saldo.py  # Regras de saldo isoladas
│   │   └── validadores.py   # Validações centralizadas
│   │
│   ├── database/            # Acesso a dados
│   │   ├── __init__.py
│   │   ├── connection.py    # Conexão com banco
│   │   ├── users.py         # CRUD usuários
│   │   ├── ferias.py        # CRUD férias
│   │   ├── auditoria.py     # Sistema de auditoria
│   │   └── backup.py        # Sistema de backup
│   │
│   ├── interface/           # Interface do usuário (NOVA)
│   │   ├── __init__.py
│   │   ├── cadastro.py      # Telas de cadastro
│   │   ├── gerenciamento.py # Telas de gerenciamento
│   │   ├── dashboard.py     # Dashboard principal
│   │   └── relatorios.py    # Telas de relatórios
│   │
│   └── utils/               # Utilitários
│       ├── __init__.py
│       ├── calculos.py      # Cálculos de férias
│       ├── validacoes.py    # Validações de dados
│       └── formatacao.py    # Formatação de dados
│
├── tests/                   # Testes automatizados
│   ├── test_regras.py       # Testes das regras de negócio
│   ├── test_database.py     # Testes do banco de dados
│   └── test_validacoes.py   # Testes de validações
│
└── data/                    # Dados da aplicação
    ├── rpontes_rh.db       # Banco SQLite
    └── backups/             # Backups automáticos
```

## 🎯 Princípios da Organização

### Separação de Responsabilidades
- **core/**: Lógica de negócio pura (sem interface)
- **interface/**: Componentes visuais (sem lógica)
- **database/**: Acesso a dados (sem regras)
- **utils/**: Funções auxiliares reutilizáveis

### Facilidade de Manutenção
- Cada módulo tem uma responsabilidade específica
- Dependências claras entre camadas
- Código reutilizável em utils/
- Testes organizados por funcionalidade

### Escalabilidade
- Fácil adição de novas funcionalidades
- Modificações isoladas por módulo
- Interface separada da lógica
- Configurações centralizadas

---

**Sistema desenvolvido para uso interno da Construtora RPONTES**  
**Status**: ✅ Totalmente funcional com MySQL  
**Última atualização**: Outubro 2025

