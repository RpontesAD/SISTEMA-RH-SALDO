# Changelog - Sistema de Gestão de Férias RPONTES

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.3.0] - 2024-11-03

### ✨ Adicionado
- **Deploy no Streamlit Cloud** com SQLite
- **Documentação completa** do projeto (README, Manual do Usuário, Manual Técnico, API Reference)
- **Arquivo .gitignore** para deploy limpo
- **Script de inicialização** do banco de dados
- **Configuração de secrets** para Streamlit Cloud
- **Checklist de deploy** com instruções detalhadas

### 🔧 Alterado
- **Removida mensagem** "Banco: SQLite" do sidebar
- **Removida mensagem** de conexão SQLite bem-sucedida
- **Removida mensagem** de acesso padrão da tela de login
- **Otimizado requirements.txt** para compatibilidade com Streamlit Cloud
- **Corrigido error_handler.py** para criar diretório logs automaticamente

### 🐛 Corrigido
- **Erro de sintaxe SQL** no gerenciamento de férias (MySQL → SQLite)
- **Importação do pandas** faltando em gerenciar_ferias.py
- **Problema de autenticação** com índices incorretos no SQLite
- **Erro de encoding** em scripts de teste
- **Problema de packages.txt** com comentários em português

### 🗑️ Removido
- **Dependência do MySQL** para deploy gratuito
- **Mensagens de debug** desnecessárias na interface
- **Arquivos de teste** temporários

## [1.2.0] - 2024-11-02

### ✨ Adicionado
- **Migração completa para SQLite** como banco padrão
- **Interface SQLite** compatível com MySQL existente
- **Configuração automática** de banco baseada no ambiente
- **Backup automático** do banco SQLite
- **Usuário admin padrão** criado automaticamente

### 🔧 Alterado
- **Priorização do SQLite** sobre MySQL nas configurações
- **Detecção automática** do tipo de banco no app.py
- **Configurações seguras** com fallback para SQLite

### 🐛 Corrigido
- **Problemas de conexão** com banco de dados
- **Autenticação bcrypt** funcionando corretamente
- **Criação automática** de tabelas no primeiro uso

## [1.1.0] - 2024-11-01

### ✨ Adicionado
- **Campo de confirmação de senha** no cadastro de colaboradores
- **Validação de senhas** coincidentes na interface
- **Centralização de constantes** em utils/constants.py
- **Centralização de validadores** em utils/validators.py
- **Centralização de formatadores** em utils/formatters.py
- **Melhoria na UX** do cadastro com feedback visual

### 🔧 Alterado
- **Eliminação de código duplicado** (~200 linhas removidas)
- **Arquitetura mais limpa** com separação de responsabilidades
- **Validações centralizadas** para melhor manutenibilidade

### 🐛 Corrigido
- **Duplicação de constantes** em múltiplos arquivos
- **Inconsistências** nas validações entre módulos
- **Problemas de importação** circular

## [1.0.0] - 2024-10-30

### ✨ Adicionado - Versão Inicial
- **Sistema completo de gestão de férias**
- **Autenticação segura** com bcrypt
- **4 níveis de acesso** (Master, Diretoria, Coordenador, Colaborador)
- **Cadastro de colaboradores** com dados completos
- **Gerenciamento de férias** com aprovação/cancelamento
- **Dashboard interativo** com métricas em tempo real
- **Controle de saldo** automático
- **Relatórios por setor** e colaborador
- **Tema dark nativo** do Streamlit
- **Validações robustas** de dados
- **Sistema de logs** detalhado
- **Tratamento de erros** abrangente

### 🏗️ Arquitetura
- **Clean Architecture** com separação de camadas
- **Repository Pattern** para acesso a dados
- **Service Layer** para regras de negócio
- **Dependency Injection** para flexibilidade

### 🔐 Segurança
- **Senhas criptografadas** com bcrypt
- **Controle de acesso** por níveis
- **Validação de entrada** sanitizada
- **Sessões seguras** via Streamlit

### 📊 Funcionalidades Core
- **Cadastro de Colaboradores**
  - Dados pessoais e profissionais
  - Definição automática de nível de acesso
  - Controle de saldo de férias

- **Gerenciamento de Férias**
  - Cadastro sempre como "Pendente"
  - Aprovação com desconto automático
  - Cancelamento com devolução de dias
  - Histórico completo

- **Dashboard e Relatórios**
  - Métricas em tempo real
  - Gráficos interativos
  - Filtros avançados
  - Exportação de dados

- **Controle de Saldo**
  - Saldo padrão de 12 dias
  - Limites configuráveis (0-30 dias)
  - Ajuste automático por status
  - Histórico de alterações

### 🗄️ Banco de Dados
- **MySQL** como banco principal
- **Estrutura normalizada** com relacionamentos
- **Índices otimizados** para performance
- **Backup automático** configurado

### ⚙️ Regras de Negócio
- **Férias sempre cadastradas como Pendente**
- **Aprovação desconta do saldo automaticamente**
- **Cancelamento devolve dias ao saldo**
- **Antecedência mínima de 30 dias** (exceto RH)
- **Validação de conflitos** de datas
- **Cálculo automático** de dias úteis

### 🎨 Interface
- **Design responsivo** com Streamlit
- **Tema dark** nativo
- **Navegação intuitiva** por abas
- **Feedback visual** para ações
- **Formulários validados** em tempo real

### 📈 Performance
- **Cache inteligente** para consultas frequentes
- **Paginação** para listas grandes
- **Queries otimizadas** com índices
- **Monitoramento** de operações lentas

---

## 🏷️ Tipos de Mudanças

- **✨ Adicionado** - para novas funcionalidades
- **🔧 Alterado** - para mudanças em funcionalidades existentes
- **🐛 Corrigido** - para correção de bugs
- **🗑️ Removido** - para funcionalidades removidas
- **🔒 Segurança** - para correções de vulnerabilidades
- **📚 Documentação** - para mudanças na documentação
- **🏗️ Arquitetura** - para mudanças estruturais
- **⚡ Performance** - para melhorias de performance

## 📋 Roadmap Futuro

### v1.4.0 - Planejado
- [ ] **Notificações por email** para aprovações
- [ ] **Integração com calendário** corporativo
- [ ] **Relatórios avançados** com gráficos personalizados
- [ ] **Exportação para Excel/PDF**
- [ ] **Auditoria completa** de alterações

### v1.5.0 - Planejado
- [ ] **API REST** para integrações
- [ ] **App mobile** responsivo
- [ ] **Workflow de aprovação** multi-nível
- [ ] **Integração com AD/LDAP**
- [ ] **Dashboard executivo** avançado

### v2.0.0 - Futuro
- [ ] **Microserviços** com Docker
- [ ] **Banco PostgreSQL** para alta performance
- [ ] **Cache Redis** para sessões
- [ ] **Monitoramento** com Prometheus
- [ ] **Deploy Kubernetes** para escalabilidade

---

**Mantido por:** Equipe de Desenvolvimento RPONTES  
**Última atualização:** 03 de Novembro de 2024