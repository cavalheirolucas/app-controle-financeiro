import streamlit as st

def check_auth():
    if "user" not in st.session_state:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.page_link("app.py", label='Ir para o login', icon="🔐")
        st.stop()


def log_out():
    for key in ['user', 'session']:
        st.session_state.pop(key, None)
    st.rerun()