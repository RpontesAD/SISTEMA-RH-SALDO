import streamlit as st
from .config import (
    APP_TITLE,
    PAGE_LAYOUT,
)
from .utils.constants import SETORES, FUNCOES, NIVEIS_ACESSO  
from .utils.ui_components import create_header  
from .auth import login_page  
from .menus import menu_rh, menu_diretoria, menu_coordenador, menu_colaborador
import sys
import os
import base64

def _get_base64_image(image_path):
    """Converte imagem para base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""  


# CSS customizado removido - usando tema nativo dark do Streamlit


def main():
    import os

    logo_path = "assets/LOGORPONTES-1.png"


    create_header("CONSTRUTORA RPONTES", "Sistema de Gestão de Férias - RH", logo_path)

    if "user" not in st.session_state:

        login_page()
    else:
        user = st.session_state.user


        # Sidebar
        if os.path.exists(logo_path):

            st.sidebar.markdown(
                f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{_get_base64_image(logo_path)}" width="120"></div>',
                unsafe_allow_html=True
            )
        else:

            st.sidebar.markdown(
                """
            <div style="text-align: center; margin-bottom: 20px;">
                <h2>RPONTES</h2>
                <p style="font-size: 12px; color: #888;">Sistema RH</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.sidebar.markdown("---")

        st.sidebar.markdown(f"**Usuário:** {user['nome']}")
        st.sidebar.markdown(f"**Setor:** {user['setor']}")
        st.sidebar.markdown(f"**Função:** {user['funcao']}")

        st.sidebar.markdown("---")

        if st.sidebar.button("Logout", use_container_width=True):

            del st.session_state.user
            # Tema nativo mantém cores após rerun
            st.rerun()

        # Renderizar menu baseado no nível de acesso
        nivel_acesso = user["nivel_acesso"]
        
        if nivel_acesso == "master":
            menu_rh()
        elif nivel_acesso == "diretoria":
            menu_diretoria()
        elif nivel_acesso == "coordenador":
            menu_coordenador()
        else:
            menu_colaborador()


if __name__ == "__main__":
    main()
