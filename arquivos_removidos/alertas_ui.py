"""
Alertas de Interface - Componentes de alerta e notificação

Este módulo contém funções para exibir alertas e notificações na interface,
usando as regras de negócio do módulo core.
"""

import streamlit as st
from datetime import date
from ..core.regras_ferias import RegrasFerias


def mostrar_alerta_antecedencia(data_inicio: date, usuario_nivel: str = "colaborador") -> bool:
    """
    Mostra alerta sobre antecedência e retorna se é válida.
    
    Args:
        data_inicio: Data de início das férias
        usuario_nivel: Nível do usuário
        
    Returns:
        True se antecedência é válida, False caso contrário
    """
    try:
        validacao = RegrasFerias.validar_antecedencia(data_inicio, usuario_nivel)
        
        if validacao["eh_rh"]:
            st.info("ℹ️ **RH**: Pode cadastrar sem antecedência mínima")
            return True
        
        if validacao["valida"]:
            if validacao["dias_antecedencia"] < 15:
                st.warning(f"⚠️ Antecedência baixa: {validacao['dias_antecedencia']} dias")
            else:
                st.success(f"✅ Antecedência adequada: {validacao['dias_antecedencia']} dias")
            return True
        else:
            st.error(f"❌ {validacao['mensagem']}")
            st.error(f"📅 Antecedência atual: {validacao['dias_antecedencia']} dias")
            return False
            
    except Exception as e:
        st.error(f"Erro ao validar antecedência: {e}")
        return False


def mostrar_alerta_feriados(data_inicio: date, data_fim: date):
    """
    Mostra alertas sobre feriados no período.
    
    Args:
        data_inicio: Data de início
        data_fim: Data de fim
    """
    try:
        from .feriados import obter_feriados_no_periodo, contar_feriados_periodo
        
        feriados = obter_feriados_no_periodo(data_inicio, data_fim)
        feriados_uteis = contar_feriados_periodo(data_inicio, data_fim)
        
        if feriados:
            st.info(f"🎉 **{len(feriados)} feriado(s) encontrado(s) no período**")
            
            if feriados_uteis > 0:
                st.success(f"✅ {feriados_uteis} feriado(s) em dias úteis não serão descontados!")
            
            with st.expander("📅 Ver feriados no período"):
                for feriado in feriados:
                    data_str = feriado['data'].strftime('%d/%m/%Y')
                    dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][feriado['dia_semana']]
                    st.write(f"• **{data_str}** ({dia_semana}) - {feriado['nome']}")
        else:
            st.info("ℹ️ Nenhum feriado nacional no período")
            
    except Exception as e:
        st.warning(f"Não foi possível verificar feriados: {e}")


def mostrar_alertas_sistema():
    """
    Mostra alertas gerais do sistema.
    """
    # Placeholder para alertas do sistema
    pass


def mostrar_painel_alertas():
    """
    Mostra painel de alertas para administradores.
    """
    st.markdown("### 🚨 Painel de Alertas")
    
    # Placeholder para painel de alertas
    st.info("Nenhum alerta no momento")


def mostrar_alerta_saldo_baixo(saldo_atual: int, limite: int = 3):
    """
    Mostra alerta se saldo está baixo.
    
    Args:
        saldo_atual: Saldo atual do colaborador
        limite: Limite para considerar saldo baixo
    """
    if saldo_atual <= limite:
        if saldo_atual == 0:
            st.error("🚨 **Saldo esgotado!** Não é possível aprovar mais férias.")
        else:
            st.warning(f"⚠️ **Saldo baixo:** {saldo_atual} dia(s) restante(s)")


def mostrar_alerta_periodo_longo(dias: int, limite: int = 15):
    """
    Mostra alerta se período de férias é muito longo.
    
    Args:
        dias: Número de dias solicitados
        limite: Limite para considerar período longo
    """
    if dias > limite:
        st.warning(f"⚠️ **Período longo:** {dias} dias (considere dividir em períodos menores)")


def mostrar_confirmacao_operacao(titulo: str, detalhes: str, key: str) -> bool:
    """
    Mostra confirmação para operações importantes.
    
    Args:
        titulo: Título da operação
        detalhes: Detalhes da operação
        key: Chave única para o componente
        
    Returns:
        True se confirmado, False caso contrário
    """
    st.warning(f"⚠️ **{titulo}**")
    st.write(detalhes)
    
    return st.checkbox("Confirmo que desejo realizar esta operação", key=f"confirm_{key}")


def mostrar_sucesso_operacao(mensagem: str):
    """
    Mostra mensagem de sucesso padronizada.
    
    Args:
        mensagem: Mensagem de sucesso
    """
    st.success(f"✅ {mensagem}")


def mostrar_erro_operacao(mensagem: str):
    """
    Mostra mensagem de erro padronizada.
    
    Args:
        mensagem: Mensagem de erro
    """
    st.error(f"❌ {mensagem}")