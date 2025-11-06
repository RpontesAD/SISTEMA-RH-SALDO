# Renovação Anual de Saldo - Documentação

## 📋 Visão Geral

A funcionalidade de **Renovação Anual de Saldo** permite que o RH defina um novo saldo padrão de férias para todos os colaboradores uma vez por ano, zerando saldos não utilizados.

## 🎯 Objetivo

- **Renovar saldos** de todos os colaboradores simultaneamente
- **Evitar acúmulo** de férias não utilizadas
- **Padronizar** saldo anual conforme política da empresa
- **Manter histórico** de todas as renovações

## 🔧 Como Funciona

### 1. **Acesso**
- Disponível apenas para usuários **Master (RH)**
- Menu: `Painel RH` → `Renovação Anual`

### 2. **Processo de Renovação**

#### **Passo 1: Verificações Automáticas**
- ✅ Conexão com banco de dados
- ✅ Número de colaboradores
- ⚠️ Férias pendentes (não afeta renovação)

#### **Passo 2: Definir Parâmetros**
- **Ano:** Ano da renovação (padrão: ano atual)
- **Novo Saldo:** Dias de férias padrão (0-30 dias)

#### **Passo 3: Prévia da Operação**
- Total de colaboradores afetados
- Saldo médio atual vs novo saldo
- Diferença total de dias

#### **Passo 4: Modo de Execução**
- **🧪 Simulação:** Testa sem alterar dados
- **🔄 Execução Real:** Aplica mudanças definitivas

## 🛡️ Proteções de Segurança

### **Validações**
- ❌ **Uma renovação por ano:** Impede múltiplas renovações
- ❌ **Saldo válido:** Entre 0 e 30 dias
- ❌ **Ano válido:** Entre 2024 e 2030

### **Backup Automático**
- 💾 **Backup antes da operação:** Salva saldos atuais
- 🔙 **Rollback de emergência:** Desfaz renovação do mesmo dia
- 📊 **Histórico completo:** Registra todas as operações

### **Confirmação Dupla**
- ✅ Confirmar entendimento do impacto
- ✅ Confirmar execução da renovação

## 🧪 Estratégia de Teste

### **1. Dados de Teste**
```
Colaboradores Fictícios:
- João Teste Silva (TI)
- Maria Teste Santos (RH)  
- Pedro Teste Costa (Financeiro)
- Ana Teste Lima (Comercial)
- Carlos Teste Souza (Engenharia)
```

### **2. Cenários de Teste**

#### **Teste 1: Simulação**
1. Ativar "Modo Simulação"
2. Definir novo saldo (ex: 8 dias)
3. Verificar prévia sem alterar dados

#### **Teste 2: Dados Fictícios**
1. Criar colaboradores de teste
2. Executar renovação real nos dados de teste
3. Verificar se saldos foram atualizados

#### **Teste 3: Rollback**
1. Executar renovação
2. Testar função "Desfazer" no mesmo dia
3. Verificar se saldos voltaram ao original

#### **Teste 4: Validações**
1. Tentar renovar o mesmo ano duas vezes
2. Testar saldos inválidos (negativos, >30)
3. Verificar mensagens de erro

## 📊 Histórico e Auditoria

### **Informações Registradas**
- 📅 **Ano da renovação**
- 🔢 **Saldo padrão aplicado**
- 👤 **Usuário responsável**
- ⏰ **Data/hora da operação**
- 💾 **Backup dos dados anteriores**

### **Relatórios Disponíveis**
- Lista de todas as renovações
- Comparativo ano a ano
- Impacto por renovação

## ⚠️ Regras de Negócio

### **Política de Férias**
- 🔄 **Renovação anual obrigatória**
- ❌ **Sem acúmulo de saldos**
- 📅 **Uma renovação por ano**
- 🏢 **Aplicação para todos os colaboradores**

### **Preservação de Dados**
- ✅ **Histórico de férias mantido**
- ✅ **Aprovações/rejeições preservadas**
- ✅ **Dados pessoais inalterados**
- 🔄 **Apenas saldo_ferias é alterado**

## 🚨 Situações de Emergência

### **Desfazer Renovação**
- ⏰ **Prazo:** Apenas no mesmo dia
- 🔙 **Processo:** Restaura backup automático
- 👤 **Acesso:** Apenas usuário Master
- 📝 **Log:** Operação registrada

### **Recuperação de Dados**
- 💾 **Backup automático:** Antes de cada renovação
- 🔍 **Auditoria completa:** Histórico de mudanças
- 📞 **Suporte:** Logs detalhados para análise

## 📈 Exemplo Prático

### **Cenário: Renovação 2025 → 2026**

**Situação Atual (2025):**
- 15 colaboradores
- Saldo médio: 8.5 dias
- Total em uso: 127 dias

**Após Renovação (2026):**
- Novo saldo padrão: 12 dias
- Todos colaboradores: 12 dias
- Total após renovação: 180 dias
- **Diferença:** +53 dias

**Resultado:**
- ✅ Todos colaboradores com 12 dias
- ❌ Saldos anteriores zerados
- 📊 Operação registrada no histórico

## 🔧 Manutenção

### **Limpeza de Dados**
- 🗑️ **Dados de teste:** Removíveis a qualquer momento
- 📊 **Histórico:** Mantido permanentemente
- 💾 **Backups:** Armazenados por segurança

### **Monitoramento**
- 📈 **Estatísticas em tempo real**
- 🔍 **Verificações automáticas**
- ⚠️ **Alertas de inconsistência**

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Consultar histórico de renovações
3. Usar dados de teste para validação
4. Contatar suporte técnico se necessário

**Sistema desenvolvido para Construtora RPONTES**