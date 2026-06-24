import streamlit as st
import pandas as pd
import plotly.express as px
from utils.supabase_client import get_client
from utils.auth import check_auth, log_out




st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
check_auth()

#HEADER-------------------------

col1, col2 = st.columns([4, 1])

col1.title("📊 Dashboard")

if col2.button("Sair"):
    log_out()

st.caption(f"Logado como: {st.session_state['user'].email}")
st.divider()



#---------------------------------

supabase = get_client()
user_id = st.session_state['user'].id

res = supabase.table("transacoes_financeiras").select("*").eq("user_id", user_id).order("data", desc = True).execute()
df = pd.DataFrame(res.data)

if df.empty:
    st.info("Nenhuma Transação encontrada no arquivo")
    st.page_link('pages/upload.py', label='Ir para Upload', icon = "📂")
    st.stop()

df["data"] = pd.to_datetime(df["data"])

#------------------------------

meses_disponiveis = sorted(df["data"].dt.to_period('M').astype('str').unique(), reverse = True)
meses_selecionados = st.multiselect('Selecione o período', options = meses_disponiveis, default = meses_disponiveis[:3])


if meses_selecionados:
    df["mes"] = df["data"].dt.to_period('M').astype(str)
    df = df[df["mes"].isin(meses_selecionados)]

st.divider()
#---------------------------------

receitas = df[df['tipo'] == 'receita']['valor'].sum()
despesas = df[df['tipo'] == 'despesa']['valor'].sum()
saldos = receitas - despesas


col1, col2, col3 = st.columns(3)

col1.metric('Receita Total', f"R$ {receitas:,.2f}")
col2.metric('Despesa Total', f"R$ {despesas:,.2f}")
col3.metric('Saldo Total', f"R$ {saldos:,.2f}")

st.divider()
#--------------------------------
col_dir, col_esq = st.columns(2)


with col_esq:
    st.subheader("Gastos por Categoria")
    desp = df[df['tipo'] == 'despesa']

    if not desp.empty:
        por_cat = desp.groupby("categoria")["valor"].sum().reset_index()
        fig1 = px.pie(
            por_cat,
            values = 'Valor',
            names = 'Categoria',
            hole = 0.45,
            color_discrete_sequence=px.colors.qualitative.Set
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info('Sem despesas no período selecionado')


with col_dir:
     st.subheader("Gastos Mensais")
     desp = df[df['tipo'] == 'despesa']


     if not desp.empty:
        desp["mes"] = desp["data"].dt.to_period('M').astype('str')
        por_mes = desp.groupby("mes")["valor"].sum().reset_index()
        fig2 = px.bar(
            por_mes,
            x="mes",
            y="valor",
            labels={"mes":"Mês", "valor":"R$"},
        )
        st.plotly_chart(fig2, use_container_width=True)
     else:
        st.info('Sem despesas no período selecionado')


st.divider()
#-------------------------------

st.subheader("Extrato Consolidado")
st.dataframe(df[["data","descricao","categoria", "valor", "tipo"]]
             .sort_values("data",ascending=False)
             .rename(columns= {
                     "data" : "Data",
                     "descricao" : "Descrição",
                     "categoria" : "Categoria",
                     "valor" : "Valor (R$)", 
                     "tipo" : "Tipo"}),
             use_container_width = True,
             hide_index = True
             )
