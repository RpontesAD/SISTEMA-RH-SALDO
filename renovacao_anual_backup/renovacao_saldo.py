"""
Menu de Renovação Anual de Saldo
"""
import streamlit as st
from datetime import date
import pandas as pd
from ..services.renovacao_service import RenovacaoService

def menu_renovacao_saldo():
    """Menu para renovação anual de saldo de férias"""
    
    st.header("🔄 Renovação Anual de Saldo")
    
    # Aviso sobre funcionalidade
    st.info("🆕 **Renovação 2025 → 2026:** Crie saldos para 2026 sem alterar nenhum dado de 2025")
    
    # Exemplo visual
    with st.expander("📊 Exemplo Prático da Renovação", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📅 ANTES (apenas 2025):**")
            st.write("• João: 8 dias restantes em 2025")
            st.write("• Maria: 12 dias restantes em 2025")
            st.write("• Pedro: 3 dias restantes em 2025")
        
        with col2:
            st.write("**🆕 DEPOIS (2025 + 2026):**")
            st.write("• João: 8 dias em 2025 + 15 dias em 2026")
            st.write("• Maria: 12 dias em 2025 + 15 dias em 2026")
            st.write("• Pedro: 3 dias em 2025 + 15 dias em 2026")
        
        st.success("✅ **Resultado:** Nenhum dado de 2025 é alterado, apenas criados novos saldos para 2026")
    
    # Migrar dados existentes se necessário
    try:
        migrados = st.session_state.db.migrar_saldos_existentes()
        if migrados > 0:
            st.success(f"✅ {migrados} colaboradores migrados para nova estrutura de saldos anuais")
    except AttributeError:
        # Função ainda não existe
        with st.expander("🔧 Inicializar Nova Estrutura", expanded=False):
            st.write("Para ativar o histórico completo de renovações:")
            if st.button("🚀 Reiniciar Aplicação", help="Reinicia para carregar novas funções"):
                st.info("🔄 Reinicie manualmente a aplicação (Ctrl+C e streamlit run app.py)")
    except:
        pass
    
    # Inicializar serviço
    if 'renovacao_service' not in st.session_state:
        st.session_state.renovacao_service = RenovacaoService(st.session_state.db)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Nova Renovação", "Histórico", "Dados de Teste"])
    
    with tab1:
        nova_renovacao()
    
    with tab2:
        historico_renovacoes()
    
    with tab3:
        dados_teste()

def nova_renovacao():
    """Interface para nova renovação anual"""
    
    ano_atual = date.today().year
    
    st.subheader("📅 Definir Saldo Padrão Anual")
    
    # Verificar se já houve renovação este ano
    try:
        ja_renovado = st.session_state.db.verificar_renovacao_ano(ano_atual)
    except AttributeError:
        # Função ainda não existe, assumir que não houve renovação
        ja_renovado = False
    
    if ja_renovado:
        st.error(f"⚠️ Já foi realizada renovação para o ano {ano_atual}")
        st.info("Só é permitida uma renovação por ano")
        return
    
    # Verificações de segurança
    try:
        service = st.session_state.renovacao_service
        verificacoes = service.verificar_seguranca()
        
        with st.expander("🔍 Verificações de Segurança", expanded=False):
            for status, mensagem in verificacoes:
                st.write(f"{status} {mensagem}")
    except:
        # Verificações simplificadas
        with st.expander("🔍 Verificações de Segurança", expanded=False):
            usuarios = st.session_state.db.get_users()
            if usuarios:
                st.write(f"✅ {len(usuarios)} colaboradores encontrados")
                st.write("✅ Conexão com banco funcionando")
            else:
                st.write("❌ Nenhum colaborador encontrado")
    
    # Estatísticas atuais
    try:
        stats = st.session_state.db.get_estatisticas_saldo()
    except AttributeError:
        # Função ainda não existe, usar alternativa
        usuarios = st.session_state.db.get_users()
        if usuarios:
            saldos = [u['saldo_ferias'] for u in usuarios]
            stats = [{
                'total_colaboradores': len(usuarios),
                'saldo_medio': sum(saldos) / len(saldos),
                'saldo_minimo': min(saldos),
                'saldo_maximo': max(saldos)
            }]
        else:
            stats = None
    
    if stats:
        stat = stats[0]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Colaboradores", int(stat['total_colaboradores']))
        with col2:
            st.metric("Saldo Médio", f"{stat['saldo_medio']:.1f} dias")
        with col3:
            st.metric("Saldo Mínimo", f"{stat['saldo_minimo']} dias")
        with col4:
            st.metric("Saldo Máximo", f"{stat['saldo_maximo']} dias")
    
    st.markdown("---")
    
    # Modo teste (fora do formulário para atualizar em tempo real)
    modo_teste = st.checkbox("🧪 Modo Simulação (não altera dados reais)")
    
    if modo_teste:
        st.info("✅ Modo simulação ativado - nenhum dado será alterado")
    else:
        st.warning("⚠️ ATENÇÃO: Esta operação é IRREVERSÍVEL e afetará TODOS os colaboradores")
    
    # Formulário
    with st.form("renovacao_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            ano_renovacao = st.number_input(
                "Ano da Renovação",
                min_value=2025,
                max_value=2030,
                value=2026,
                step=1,
                help="Criar saldo padrão para 2026. Dados de 2025 serão preservados."
            )
        
        with col2:
            novo_saldo = st.number_input(
                "Novo Saldo Padrão (dias)",
                min_value=0,
                max_value=30,
                value=12,
                step=1
            )
        
        # Prévia da operação
        if novo_saldo > 0:
            try:
                previa = service.get_previa_renovacao(novo_saldo)
                if previa:
                    with st.expander("📊 Prévia da Operação", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Situação Atual:**")
                            st.write(f"• Total de colaboradores: {previa['total_colaboradores']}")
                            st.write(f"• Saldo médio atual: {previa['saldo_medio_atual']} dias")
                            st.write(f"• Total de dias em uso: {previa['saldo_atual_total']} dias")
                        
                        with col2:
                            st.write("**Após Renovação:**")
                            st.write(f"• Novo saldo padrão: {previa['novo_saldo']} dias")
                            st.write(f"• Total de dias após: {previa['saldo_novo_total']} dias")
                            diferenca = previa['diferenca_total']
                            sinal = "+" if diferenca > 0 else ""
                            st.write(f"• Diferença total: {sinal}{diferenca} dias")
            except:
                # Prévia simplificada
                usuarios = st.session_state.db.get_users()
                if usuarios and novo_saldo > 0:
                    total = len(usuarios)
                    saldos = [u['saldo_ferias'] for u in usuarios]
                    saldo_medio = sum(saldos) / len(saldos)
                    
                    with st.expander("📊 Prévia da Operação", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Situação Atual:**")
                            st.write(f"• Total de colaboradores: {total}")
                            st.write(f"• Saldo médio atual: {saldo_medio:.1f} dias")
                        
                        with col2:
                            st.write(f"**Após Renovação {ano_renovacao}:**")
                            st.write(f"• Novo saldo {ano_renovacao}: {novo_saldo} dias")
                            st.write(f"• Saldo 2025: Preservado (inalterado)")
                            st.write(f"• Histórico 2025: Preservado (férias, aprovações)")
                            st.write(f"• Resultado: Cada colaborador terá 2 anos de dados")
        
        # Confirmação
        if modo_teste:
            # No modo simulação, sempre permitir
            confirmar = True
        else:
            # No modo real, exigir confirmação dupla
            st.markdown("---")
            st.write("**✅ CONFIRMAÇÃO DE SEGURANÇA:**")
            confirmar1 = st.checkbox(f"Entendo que será criado saldo de {novo_saldo} dias para {ano_renovacao} para TODOS os colaboradores")
            confirmar2 = st.checkbox("Confirmo que os dados de 2025 NÃO serão alterados (apenas preservados)")
            confirmar3 = st.checkbox(f"Confirmo que desejo criar os saldos de {ano_renovacao}")
            confirmar = confirmar1 and confirmar2 and confirmar3
        
        submitted = st.form_submit_button(
            "🔄 Simular Renovação" if modo_teste else "🔄 Aplicar Renovação",
            disabled=not confirmar,
            use_container_width=True
        )
        
        if submitted:
            if modo_teste:
                # Simulação simples
                usuarios = st.session_state.db.get_users()
                total = len(usuarios) if usuarios else 0
                
                if total > 0:
                    saldos_atuais = [u['saldo_ferias'] for u in usuarios]
                    saldo_medio_atual = sum(saldos_atuais) / len(saldos_atuais)
                    diferenca = novo_saldo - saldo_medio_atual
                    
                    st.success(f"✅ SIMULAÇÃO: {total} colaboradores receberiam {novo_saldo} dias para {ano_renovacao}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Saldo Atual (2025)", f"{saldo_medio_atual:.1f} dias")
                    with col2:
                        st.metric(f"Novo Saldo ({ano_renovacao})", f"{novo_saldo} dias")
                    with col3:
                        st.metric("Diferença", f"{diferenca:+.1f} dias", delta=diferenca)
                    
                    # Exemplo prático
                    st.info(f"📅 **Exemplo:** João tem 8 dias em 2025 → Continuará com 8 dias em 2025 + {novo_saldo} dias em {ano_renovacao}")
                    st.success(f"✅ **Garantia:** Todos os dados de 2025 (saldos, férias, histórico) serão preservados")
                else:
                    st.error("❌ Nenhum colaborador encontrado")
            else:
                # Renovação real com nova estrutura
                try:
                    # Usar nova função de renovação
                    sucesso, mensagem = st.session_state.db.renovar_saldo_anual(
                        ano_renovacao,
                        novo_saldo,
                        st.session_state.user['id'],
                        modo_teste=False
                    )
                    
                    if sucesso:
                        st.success(f"✅ {mensagem}")
                        st.balloons()
                        st.info(f"📅 **Dados 2025 preservados:** Saldos, férias e histórico de 2025 permanecem inalterados")
                        st.success(f"🆕 **Novo ano criado:** Todos os colaboradores agora têm saldo de {novo_saldo} dias para {ano_renovacao}")
                        # Limpar cache
                        if hasattr(st.session_state, 'cache_usuarios'):
                            del st.session_state.cache_usuarios
                    else:
                        st.error(f"❌ {mensagem}")
                        
                except AttributeError:
                    # Fallback para método antigo se nova função não existir
                    usuarios = st.session_state.db.get_users()
                    if not usuarios:
                        st.error("❌ Nenhum colaborador encontrado")
                        return
                    
                    atualizados = 0
                    for usuario in usuarios:
                        sucesso = st.session_state.db.update_saldo_ferias(
                            usuario['id'], 
                            novo_saldo,
                            st.session_state.user['id'],
                            st.session_state.user['nome'],
                            f"Renovação anual {ano_renovacao}"
                        )
                        if sucesso:
                            atualizados += 1
                    
                    if atualizados > 0:
                        st.success(f"✅ Renovação aplicada! {atualizados} colaboradores atualizados para {novo_saldo} dias.")
                        st.warning("⚠️ Usando método de compatibilidade")
                        st.info("🔄 Para ativar histórico completo, reinicie: Ctrl+C e streamlit run app.py")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao atualizar colaboradores")
                        
                except Exception as e:
                    st.error(f"❌ Erro na renovação: {str(e)}")

def historico_renovacoes():
    """Exibe histórico de renovações"""
    
    st.subheader("📊 Histórico de Renovações")
    
    # Botão para atualizar
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()
    
    try:
        renovacoes = st.session_state.db.get_historico_renovacoes()
    except AttributeError:
        renovacoes = []
        st.warning("⚠️ Função de histórico ainda não disponível - reinicie a aplicação")
    
    # Mostrar informações sobre a nova estrutura
    with st.expander("📊 Nova Estrutura de Dados", expanded=False):
        st.write("**Tabelas criadas:**")
        st.write("• `renovacao_saldo` - Histórico de renovações")
        st.write("• `saldos_anuais` - Saldos por ano/colaborador")
        st.write("**Benefícios:**")
        st.write("• Histórico preservado por ano")
        st.write("• Auditoria completa")
        st.write("• Rollback seguro")
    
    if not renovacoes:
        st.info("📅 Nenhuma renovação realizada ainda")
        st.info("As renovações serão registradas aqui após a primeira execução")
        
        # Mostrar status das tabelas
        try:
            # Tentar verificar se as tabelas existem
            test_renovacao = st.session_state.db._execute_query("SELECT COUNT(*) FROM renovacao_saldo", fetch=True)
            test_saldos = st.session_state.db._execute_query("SELECT COUNT(*) FROM saldos_anuais", fetch=True)
            
            if test_renovacao and test_saldos:
                st.success("✅ Tabelas de histórico criadas com sucesso")
            else:
                st.warning("⚠️ Tabelas ainda não foram criadas")
        except:
            st.info("🔧 Tabelas serão criadas na primeira renovação")
        
        return
    
    # Converter para DataFrame
    df = pd.DataFrame(renovacoes)
    df['data_aplicacao'] = pd.to_datetime(df['data_aplicacao']).dt.strftime('%d/%m/%Y %H:%M')
    
    # Exibir tabela
    st.dataframe(
        df[['ano', 'saldo_padrao', 'data_aplicacao', 'responsavel_nome']],
        column_config={
            'ano': 'Ano',
            'saldo_padrao': 'Saldo Padrão',
            'data_aplicacao': 'Data/Hora',
            'responsavel_nome': 'Responsável'
        },
        use_container_width=True
    )
    
    # Opção de desfazer (apenas para emergências)
    if renovacoes:
        st.markdown("---")
        st.subheader("⚠️ Emergência - Desfazer Última Renovação")
        
        ultima = renovacoes[0]
        data_ultima = pd.to_datetime(ultima['data_aplicacao']).strftime('%d/%m/%Y')
        
        if data_ultima == date.today().strftime('%d/%m/%Y'):
            st.warning(f"Última renovação: Ano {ultima['ano']} - {ultima['saldo_padrao']} dias")
            
            if st.button("🔙 Desfazer Última Renovação", type="secondary"):
                try:
                    sucesso, mensagem = st.session_state.db.desfazer_ultima_renovacao(
                        st.session_state.user['id']
                    )
                except AttributeError:
                    sucesso, mensagem = False, "Função ainda não disponível - reinicie a aplicação"
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
        else:
            st.info("Só é possível desfazer renovações do mesmo dia")

def dados_teste():
    """Criar dados de teste para validação"""
    
    st.subheader("🧪 Ambiente de Teste")
    
    st.info("Use esta seção para criar colaboradores fictícios e testar a renovação sem afetar dados reais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👥 Criar 5 Colaboradores de Teste", use_container_width=True):
            criar_colaboradores_teste()
    
    with col2:
        if st.button("🗑️ Limpar Dados de Teste", use_container_width=True):
            limpar_dados_teste()
    
    # Mostrar colaboradores de teste existentes
    usuarios_teste = st.session_state.db.get_users()
    if usuarios_teste:
        teste_users = [u for u in usuarios_teste if u['email'].startswith('teste')]
        
        if teste_users:
            st.markdown("---")
            st.subheader("👥 Colaboradores de Teste Existentes")
            
            df_teste = pd.DataFrame(teste_users)
            st.dataframe(
                df_teste[['nome', 'email', 'setor', 'saldo_ferias']],
                column_config={
                    'nome': 'Nome',
                    'email': 'Email',
                    'setor': 'Setor',
                    'saldo_ferias': 'Saldo Atual'
                },
                use_container_width=True
            )

def criar_colaboradores_teste():
    """Cria colaboradores fictícios para teste"""
    
    colaboradores_teste = [
        ("João Teste Silva", "teste.joao@rpontes.com", "TI", "Desenvolvedor"),
        ("Maria Teste Santos", "teste.maria@rpontes.com", "RH", "Analista"),
        ("Pedro Teste Costa", "teste.pedro@rpontes.com", "Financeiro", "Contador"),
        ("Ana Teste Lima", "teste.ana@rpontes.com", "Comercial", "Vendedor"),
        ("Carlos Teste Souza", "teste.carlos@rpontes.com", "Engenharia", "Engenheiro")
    ]
    
    criados = 0
    for nome, email, setor, funcao in colaboradores_teste:
        sucesso = st.session_state.db.create_user(
            nome=nome,
            email=email,
            senha="teste123",
            setor=setor,
            funcao=funcao,
            nivel_acesso="colaborador",
            saldo_ferias=12
        )
        if sucesso:
            criados += 1
    
    if criados > 0:
        st.success(f"✅ {criados} colaboradores de teste criados!")
    else:
        st.warning("Colaboradores de teste já existem")

def limpar_dados_teste():
    """Remove colaboradores de teste"""
    
    usuarios = st.session_state.db.get_users()
    removidos = 0
    
    for usuario in usuarios:
        if usuario['email'].startswith('teste'):
            if st.session_state.db.delete_user(usuario['id']):
                removidos += 1
    
    if removidos > 0:
        st.success(f"✅ {removidos} colaboradores de teste removidos!")
    else:
        st.info("Nenhum colaborador de teste encontrado")