# Manual do Usuário - Sistema de Gestão de Férias RPONTES

## 🎯 Guia Rápido de Uso

### 1. Acesso ao Sistema
1. **Abra** o navegador e acesse a URL do sistema
2. **Digite** seu email e senha corporativos
3. **Clique** em "Entrar"

### 2. Interface Principal
- **Sidebar esquerda:** Informações do usuário e logout
- **Área central:** Funcionalidades baseadas no seu nível de acesso
- **Abas superiores:** Navegação entre módulos

## 👥 Funcionalidades por Nível de Acesso

### 🔑 Gestão de Pessoas (Master) - Acesso Total

#### Cadastrar Colaborador
1. **Acesse** a aba "Cadastrar Colaborador"
2. **Preencha** todos os campos obrigatórios:
   - Nome completo
   - Email corporativo (único)
   - Senha inicial
   - Confirmação de senha
   - Setor
   - Função
   - Data de admissão
3. **Defina** saldo inicial de férias (padrão: 12 dias)
4. **Clique** em "Cadastrar Colaborador"

#### Gerenciar Colaboradores
1. **Acesse** a aba "Gerenciar Colaboradores"
2. **Use filtros** para encontrar colaboradores:
   - Por nome
   - Por setor
   - Por função
   - Por saldo de férias
3. **Ações disponíveis:**
   - **Editar:** Alterar dados pessoais e profissionais
   - **Ajustar Saldo:** Modificar saldo de férias
   - **Excluir:** Remover colaborador (com confirmação)

#### Gerenciar Férias
1. **Selecione** o colaborador no dropdown
2. **Visualize** informações de saldo:
   - Saldo atual
   - Dias pendentes
   - Saldo após aprovações
   - Dias já gozados

**Cadastrar Férias:**
1. **Escolha** datas de início e fim
2. **Verifique** se não há conflitos
3. **Clique** em "Cadastrar Férias" (sempre como Pendente)

**Gerenciar Status:**
1. **Acesse** a aba "Gerenciar Status"
2. **Para cada período de férias:**
   - **Aprovar:** Desconta automaticamente do saldo
   - **Cancelar:** Devolve dias ao saldo se estava aprovado
   - **Excluir:** Remove registro completamente

#### Dashboard
1. **Visualize** métricas gerais:
   - Total de colaboradores
   - Férias pendentes
   - Distribuição por setor
2. **Analise** gráficos interativos
3. **Filtre** por período ou setor

### 🏢 Diretoria - Relatórios Executivos

#### Dashboard Executivo
1. **Acesse** automaticamente ao fazer login
2. **Visualize** métricas consolidadas:
   - Utilização de férias por setor
   - Tendências mensais
   - Indicadores de performance
3. **Use filtros** para análises específicas

### 👨💼 Coordenador - Gestão do Setor

#### Visualizar Equipe
1. **Acesse** a lista de colaboradores do seu setor
2. **Monitore** saldos e férias da equipe
3. **Acompanhe** status das solicitações

#### Relatórios do Setor
1. **Visualize** dados consolidados do setor
2. **Analise** distribuição de férias
3. **Monitore** tendências da equipe

### 👤 Colaborador - Dados Pessoais

#### Consultar Dados Pessoais
1. **Visualize** suas informações:
   - Dados pessoais
   - Saldo atual de férias
   - Histórico completo

#### Histórico de Férias
1. **Acesse** seu histórico completo
2. **Visualize** todas as férias:
   - Períodos aprovados
   - Férias pendentes
   - Férias canceladas
3. **Acompanhe** status das solicitações

## 📋 Fluxos de Trabalho

### Fluxo de Solicitação de Férias

#### Para RH (cadastrando para colaborador):
1. **Selecione** o colaborador
2. **Verifique** saldo disponível
3. **Cadastre** as férias (status: Pendente)
4. **Aprove** imediatamente se apropriado

#### Para Colaborador (solicitação externa):
1. **Solicite** férias ao RH via email/telefone
2. **Aguarde** cadastro no sistema pelo RH
3. **Acompanhe** status no sistema

### Fluxo de Aprovação

#### Processo Padrão:
1. **Férias cadastradas** como "Pendente"
2. **RH analisa** disponibilidade e regras
3. **Aprovação:** Desconta automaticamente do saldo
4. **Cancelamento:** Devolve dias se necessário

### Fluxo de Ajuste de Saldo

#### Apenas RH pode ajustar:
1. **Acesse** "Gerenciar Colaboradores"
2. **Clique** em "Ajustar Saldo" para o colaborador
3. **Defina** novo saldo (0-30 dias)
4. **Confirme** a alteração

## ⚠️ Regras Importantes

### Cadastro de Férias
- ✅ **Sempre** cadastradas como "Pendente"
- ✅ **Data fim** deve ser posterior à data início
- ✅ **Não pode** haver sobreposição com férias aprovadas
- ✅ **Antecedência mínima** de 30 dias (exceto RH)

### Saldo de Férias
- ✅ **Padrão:** 12 dias por colaborador
- ✅ **Mínimo:** 0 dias
- ✅ **Máximo:** 30 dias
- ✅ **Desconto:** Apenas férias aprovadas descontam

### Aprovação/Cancelamento
- ✅ **Aprovar:** Desconta dias do saldo automaticamente
- ✅ **Cancelar:** Devolve dias ao saldo se estava aprovado
- ✅ **Excluir:** Remove registro e ajusta saldo conforme necessário

## 🔍 Dicas de Uso

### Navegação Eficiente
- **Use filtros** para encontrar informações rapidamente
- **Ordene** listas clicando nos cabeçalhos
- **Monitore** métricas no Dashboard regularmente

### Gestão de Saldo
- **Verifique** saldo antes de cadastrar férias
- **Monitore** férias pendentes que afetam saldo futuro
- **Ajuste** saldos apenas quando necessário

### Relatórios
- **Filtre** por período para análises específicas
- **Compare** dados entre setores
- **Exporte** dados quando necessário

### Segurança
- **Faça logout** ao terminar de usar
- **Não compartilhe** credenciais
- **Reporte** problemas ao RH imediatamente

## 🚨 Solução de Problemas

### Problemas de Login
**Erro:** "Email ou senha incorretos"
- **Verifique** se digitou corretamente
- **Confirme** com RH se conta está ativa
- **Tente** fazer logout e login novamente

### Problemas de Cadastro
**Erro:** "Email já existe"
- **Use** email único para cada colaborador
- **Verifique** se colaborador já está cadastrado

**Erro:** "Saldo insuficiente"
- **Verifique** saldo atual do colaborador
- **Considere** férias pendentes
- **Ajuste** saldo se necessário (apenas RH)

### Problemas de Férias
**Erro:** "Período conflita com férias aprovadas"
- **Verifique** histórico do colaborador
- **Escolha** datas diferentes
- **Cancele** férias conflitantes se necessário

**Erro:** "Antecedência mínima não atendida"
- **Cadastre** férias com pelo menos 30 dias de antecedência
- **RH** pode cadastrar sem antecedência mínima

### Performance Lenta
- **Recarregue** a página
- **Limpe** cache do navegador
- **Verifique** conexão com internet
- **Contate** suporte se persistir

## 📞 Suporte

### Contatos
- **Gestão de Pessoas:** gp@rpontes.com
- **TI:** ti@rpontes.com
- **Telefone:** (XX) XXXX-XXXX

### Horário de Suporte
- **Segunda a Sexta:** 8h às 18h
- **Emergências:** Conforme política interna

### Informações para Suporte
Ao reportar problemas, informe:
- **Seu nome** e email
- **Ação** que estava tentando fazer
- **Mensagem de erro** (se houver)
- **Navegador** utilizado
- **Horário** do problema

---

**Manual atualizado em:** Dezembro 2024  
**Versão do Sistema:** 2.0.0