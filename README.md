# Sistema de Gestão de Férias - RPONTES

Sistema interno para controle de férias dos colaboradores da Construtora RPONTES.

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação
```bash
streamlit run app.py
```

### 3. Acessar no Navegador
- **URL:** http://localhost:8501
- **Login:** admin@rpontes.com
- **Senha:** admin123

## 📋 Funcionalidades

### ✅ **Cadastro de Colaboradores**
- Cadastro completo com dados pessoais e profissionais
- Definição automática de nível de acesso baseado na função
- Controle de saldo de férias 

### ✅ **Gerenciamento de Férias**
- **Cadastro:** Sempre como "Pendente" para posterior aprovação
- **Validação de saldo:** Não permite cadastrar férias acima do saldo disponível
- **Aprovação:** Desconta automaticamente do saldo do colaborador
- **Cancelamento:** Devolve dias ao saldo 
- **Exclusão:** Remove registro e ajusta saldo se necessário
- **Histórico:** Visualização completa de todas as férias

### ✅ **Gerenciamento de Colaboradores**
- Edição de dados pessoais e profissionais
- Ajuste manual de saldo de férias
- **Inativação de colaboradores:** Preserva dados sem permitir acesso
- **Reativação:** Restaura acesso de colaboradores inativos
- Exclusão de colaboradores (com confirmação)
- Filtros avançados por nome, setor, função e saldo

### ✅ **Relatórios**
- Relatórios por setor e colaborador
- Informações de saldo em tempo real

## 👥 Níveis de Acesso

### 🔑 **Master (RH)**
- Acesso completo ao sistema
- Pode gerenciar todos os colaboradores
- Aprovação de férias sem restrições
- Relatórios gerais

### 🏢 **Diretoria**
- Visualização de relatórios consolidados
- Dashboard executivo
- Acesso somente leitura

### 👨‍💼 **Coordenador**
- Visualização do próprio setor
- Acompanhamento da equipe
- Acesso restrito

### 👤 **Colaborador**
- Visualização dos próprios dados
- Histórico pessoal de férias
- Saldo disponível

## 🏢 Setores Disponíveis

- Administração
- Assistência Técnica
- Gestão de Pessoas (RH)
- Financeiro
- Suprimentos
- Engenharia
- Marketing
- TI
- Análise de Dados
- Comercial

## ⚙️ Regras de Negócio

### 📅 **Férias**
- Cadastro sempre como "Pendente"
- Aprovação desconta do saldo automaticamente
- Cancelamento devolve dias ao saldo
- Cálculo automático de dias úteis (exclui fins de semana e feriados)

### 💰 **Saldo**
- Saldo padrão: 12 dias por colaborador
- Saldo mínimo: 0 dias
- Saldo máximo: 30 dias
- Apenas férias "Aprovadas" descontam do saldo

### 🔐 **Segurança**
- Senhas criptografadas com bcrypt
- Email único por colaborador
- Auditoria de alterações
- Backup automático do banco

## 🛠️ Tecnologias

- **Frontend:** Streamlit
- **Backend:** Python 3.8+
- **Banco de Dados:** PostgreSQL (Supabase)
- **Criptografia:** bcrypt
- **Análise de Dados:** Pandas
- **Conexão:** psycopg2

## 📁 Estrutura do Projeto

```
Gestão RH/
├── app.py                    # Ponto de entrada
├── requirements.txt          # Dependências
├── README.md                # Este arquivo
├── .env                     # Configurações
├── src/                     # Código fonte
│   ├── core/                # Regras de negócio
│   ├── database/            # Acesso a dados
│   ├── menus/               # Interfaces
│   ├── services/            # Camada de serviços
│   └── utils/               # Utilitários
├── data/                    # Dados locais
│   └── .keep                # Manter diretório
├── logs/                    # Logs do sistema
├── tests/                   # Testes automatizados
├── docs/                    # Documentação
└── renovacao_anual_backup/  # Backup da renovação anual
```

## 🔧 Solução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Porta Ocupada
```bash
streamlit run app.py --server.port 8502
```

### Problemas de Banco
O sistema usa PostgreSQL (Supabase) como banco persistente. Se houver problemas:
1. Verifique se as credenciais do Supabase estão configuradas em `.streamlit/secrets.toml`
2. Confirme se a conexão com o Supabase está ativa
3. Verifique os logs do sistema em `logs/`
4. Use as credenciais padrão: admin@rpontes.com / admin123

## 📊 Status do Sistema

✅ **Sistema Operacional e Testado**

- ✅ Autenticação e Login
- ✅ Cadastro de Colaboradores  
- ✅ Gerenciamento de Férias
- ✅ Aprovação/Cancelamento de Férias
- ✅ Dashboard e Relatórios
- ✅ Controle de Saldo
- ✅ **Validação de Saldo** (NOVO)
- ✅ **Inativação de Colaboradores** (NOVO)
- ✅ **Painéis Melhorados** (NOVO)
- ✅ Backup Automático

## 🎯 Guia de Uso Rápido

1. **Faça login** com as credenciais de administrador
2. **Cadastre colaboradores** na aba "Cadastrar Colaborador"
3. **Registre férias** na aba "Gerenciar Férias" (sempre como Pendente)
4. **Aprove/Cancele férias** na aba "Gerenciar Férias" > "Gerenciar Status"
5. **Ajuste saldos** na aba "Gerenciar Colaboradores" se necessário
6. **Visualize relatórios** na aba "Dashboard"

## Sistema desenvolvido para uso interno da **Construtora RPONTES**.

Para suporte técnico, consulte a documentação em `docs/` ou verifique os logs em `logs/`.

## 💾 Backup de Funcionalidades

### **Renovação Anual de Saldo (Removida)**
Funcionalidade completa de renovação anual foi desenvolvida e está disponível em:
- **Pasta:** `renovacao_anual_backup/`
- **Status:** Backup completo e funcional
- **Pode ser reativada:** A qualquer momento

---

**Última atualização:** Dezembro 2025 - Implementadas melhorias: validação de saldo, painéis detalhados e inativação de colaboradores 