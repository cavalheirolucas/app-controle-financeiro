import streamlit as st
from utils.supabase_client import get_client


st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="centered")


if "user" in st.session_state:
    st.switch_page("pages/dashboard.py")


st.title("💰 Controle Financeiro")
st.caption("Gerencie suas finanças de forma simples e eficiente")

supabase = get_client()

aba_login, aba_cadastro = st.tabs(["Login", "Cadastro"])

# -----------login--------------

with aba_login:
    st.subheader("Faça login para acessar suas finanças")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state["user"]    = res.user
            st.session_state["session"] = res.session
            st.rerun()
            st.success("Login bem-sucedido!")
            # Redirecionar para a página principal do controle financeiro
        except Exception:
            st.error("Email ou senha incorretos. Tente novamente.")



# -----------cadastro--------------

with aba_cadastro:
    st.subheader("Crie uma conta para começar a gerenciar suas finanças")
    email_cadastro = st.text_input("Email", key="email_cadastro")
    senha_cadastro = st.text_input("Senha", type="password", key="senha_cadastro")
    if st.button("Cadastrar"):
        if supabase.auth.sign_up(email_cadastro, senha_cadastro):
            st.success("Cadastro bem-sucedido! Faça login para acessar suas finanças.")
            # Redirecionar para a página de login
        else:
            st.error("Erro ao cadastrar. Tente novamente.")