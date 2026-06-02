import streamlit as st
import pandas as pd


def mostrar_alertas_sistema():
    """Função vazia para manter compatibilidade"""
    pass


def mostrar_painel_alertas():
    """Função vazia para manter compatibilidade"""
    pass


def menu_dashboard():
    """Relatórios principal com métricas e alertas"""
    st.markdown("#### Relatórios")

    mostrar_alertas_sistema()
    _mostrar_metricas_gerais()

    user_nivel = st.session_state.get("user", {}).get("nivel_acesso", "")
    if user_nivel == "master":
        st.markdown("---")
        mostrar_painel_alertas()


def _formatar_data(valor):
    """Formata datas para dd/mm/aaaa"""
    if pd.isna(valor) or valor in ["", None]:
        return ""

    try:
        data = pd.to_datetime(valor, errors="coerce")
        if pd.isna(data):
            return ""
        return data.strftime("%d/%m/%Y")
    except Exception:
        return str(valor)


def _mostrar_metricas_gerais():
    """Mostra métricas gerais do sistema"""
    try:
        users_list = st.session_state.users_db.get_users()

        if users_list is None:
            st.error("Erro ao carregar dados dos colaboradores")
            return

        if isinstance(users_list, list):
            if not users_list:
                st.info("Nenhum dado disponível")
                return
            users_df = pd.DataFrame(users_list)
        else:
            users_df = users_list.copy()
            if users_df.empty:
                st.info("Nenhum dado disponível")
                return

        # Garantir colunas necessárias
        colunas_necessarias = [
            "nome",
            "setor",
            "funcao",
            "nivel_acesso",
            "saldo_ferias",
            "data_admissao",
        ]

        for coluna in colunas_necessarias:
            if coluna not in users_df.columns:
                users_df[coluna] = ""

        users_df["saldo_ferias"] = pd.to_numeric(
            users_df["saldo_ferias"],
            errors="coerce"
        ).fillna(0)

        # Filtro por setor
        from ..utils.constants import SETORES

        setores_disponiveis = ["Todos"] + SETORES
        setor_selecionado = st.selectbox(
            "Filtrar por Setor:",
            setores_disponiveis
        )

        if setor_selecionado != "Todos":
            users_filtered = users_df[
                users_df["setor"] == setor_selecionado
            ].copy()
        else:
            users_filtered = users_df.copy()

        # Métricas principais
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Colaboradores", len(users_filtered))

        with col2:
            saldo_medio = users_filtered["saldo_ferias"].mean()
            if pd.isna(saldo_medio):
                saldo_medio = 0
            st.metric("Saldo Médio", f"{saldo_medio:.1f} dias")

        with col3:
            saldo_total = users_filtered["saldo_ferias"].sum()
            st.metric("Saldo Total", f"{saldo_total:.0f} dias")

        st.markdown("----")

        # Tabela Distribuição por Setor
        if setor_selecionado == "Todos":
            st.markdown("##### Distribuição por Setor")

            relatorio = users_df[
                [
                    "setor",
                    "nivel_acesso",
                    "nome",
                    "funcao",
                    "saldo_ferias",
                    "data_admissao",
                ]
            ].copy()

            relatorio["data_admissao"] = relatorio["data_admissao"].apply(
                _formatar_data
            )

            relatorio = relatorio.rename(
                columns={
                    "setor": "Setor",
                    "nivel_acesso": "Hierarquia",
                    "nome": "Colaborador",
                    "funcao": "Função",
                    "saldo_ferias": "Saldo de Férias",
                    "data_admissao": "Admissão",
                }
            )

            relatorio = relatorio.sort_values(
                by=["Setor", "Hierarquia", "Colaborador"],
                na_position="last"
            )

            st.dataframe(
                relatorio,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.markdown(f"##### Distribuição por Setor: {setor_selecionado}")

            if users_filtered.empty:
                st.info(
                    f"Nenhum colaborador cadastrado no setor {setor_selecionado}"
                )
                return

            relatorio = users_filtered[
                [
                    "nivel_acesso",
                    "nome",
                    "funcao",
                    "saldo_ferias",
                    "data_admissao",
                ]
            ].copy()

            relatorio["data_admissao"] = relatorio["data_admissao"].apply(
                _formatar_data
            )

            relatorio = relatorio.rename(
                columns={
                    "nivel_acesso": "Hierarquia",
                    "nome": "Colaborador",
                    "funcao": "Função",
                    "saldo_ferias": "Saldo de Férias",
                    "data_admissao": "Admissão",
                }
            )

            relatorio = relatorio.sort_values(
                by=["Hierarquia", "Colaborador"],
                na_position="last"
            )

            st.dataframe(
                relatorio,
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        st.error(f"Erro ao carregar métricas: {str(e)}")