import streamlit as st

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            "<h3 style='text-align: center;'>Login</h3>", unsafe_allow_html=True
        )

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="seu.email@rpontes.com")
            senha = st.text_input(
                "Senha", type="password", placeholder="Digite sua senha"
            )

            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                if not email or not senha:
                    st.error("Email e senha são obrigatórios!")
                else:
                    # Verificar se o banco foi inicializado
                    if "users_db" not in st.session_state:
                        st.error("Sistema não inicializado. Recarregue a página.")
                        return
                    
                    user = st.session_state.users_db.authenticate_user(email, senha)
                    if user:
                        st.session_state.user = user
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Email ou senha incorretos!")

        st.info("**Acesso padrão:** admin@rpontes.com / admin123")
