import streamlit as st
import pandas as pd
from utils.classificador import CATEGORIAS, classificar_lote
from utils.supabase_client import get_client
from utils.auth import check_auth, log_out


st.set_page_config(page_title="Upload File", page_icon="📂", layout="centered")
check_auth()

col_title, col_logout = st.columns([4, 1])


st.title("📂 Upload File")

if st.button("Sair"):
    log_out()

st.caption(f"Logado como: {st.session_state['user'].email}")
st.divider()

# Upload file ----------------------------------

file = st.file_uploader("Escolha um arquivo para upload", type=["csv"])

tipo_arquivo = st.radio("Selecione o tipo de arquivo", options=["Extrato bancário", "Fatura Cartão de crédito"], horizontal=True)

if file:
    try:
        df = pd.read_csv(file, sep=None, engine="python")
    except Exception:
        st.error("Erro ao ler o arquivo. Verifique se é um CSV válido.")
        st.stop()

    st.subheader("Visualização do arquivo")
    st.dataframe(df.head(5), use_container_width=True)

#---------------------------

    st.subheader("Mapeie as colunas")
    st.caption("Selecione as colunas correspondentes para cada campo")

    colunas = df.columns.tolist()

    coluna1, coluna2, coluna3 = st.columns(3)
    col_data = coluna1.selectbox("📅 Coluna de Data", options=colunas, key="col_data")
    col_descricao = coluna2.selectbox("📝 Coluna de Descrição", options=colunas, key="col_descricao")
    col_valor = coluna3.selectbox("💲Coluna de Valor", options=colunas, key="col_valor")

    st.divider()

#-----------------------------

    if st.button("Classificar transações"):
        
        df = df[[col_data, col_descricao, col_valor]].copy()
        df.columns = ["data", "descricao", "valor"]

        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce').dt.strftime("%Y-%m-%d")
        df['valor'] = pd.to_numeric(df['valor'].astype(str).str.replace(",", "."), errors="coerce")
        df = df.dropna(subset=['data', 'valor'])
        
        if tipo_arquivo == "Fatura Cartão de crédito":
            df['tipo'] = 'despesa'
            df = df[df['valor'] > 0]
        else:
            df['tipo'] = df['valor'].apply(lambda x: 'despesa' if x < 0 else 'receita')
    
        df['user_id'] = st.session_state['user'].id


        with st.spinner("Classificando transações..."):
            descricoes = df['descricao'].unique().tolist()
            resultado = classificar_lote(descricoes)
            df['categoria'] = df['descricao'].map(resultado)

        st.session_state['df_processado'] = df

    #--------------------------------

    if 'df_processado' in st.session_state:

        df = st.session_state['df_processado']

        st.subheader("Revise as classificações")

        df_editado = st.data_editor(df[["data", "descricao", "valor", "tipo", "categoria"]],
                                    column_config={ "tipo": st.column_config.SelectboxColumn("Tipo", options=["despesa", "receita"]),
                                                "categoria": st.column_config.SelectboxColumn("Categoria", options=CATEGORIAS)
                                    },
                                    use_container_width=True,
                                    hide_index=True)
        
        st.divider()


        if st.button("Salvar", use_container_width=True, type="primary"):
            supabase = get_client()
            df['tipo'] = df_editado['tipo'].values
            df['categoria'] = df_editado['categoria'].values


            existentes = supabase.table("transacoes_financeiras").select("data", "descricao", "valor").eq("user_id", st.session_state['user'].id).execute()
            hashes_existentes = {f"{r['descricao']}_{r['data']}_{r['valor']}" for r in existentes.data}

            df['hash'] = df.apply(lambda row: f"{row['descricao']}_{row['data']}_{row['valor']}", axis=1)
            df = df[~df['hash'].isin(hashes_existentes)].drop(columns=["hash"])

            if df.empty:
                st.warning("Nenhuma transação nova para salvar.")
            else:
                data_to_insert = df[["data","descricao","valor","tipo","categoria","user_id"]].to_dict(orient='records')
                supabase.table("transacoes_financeiras").insert(data_to_insert).execute()

                data_classificao = df[['descricao', 'categoria']].drop_duplicates(subset='descricao').to_dict(orient='records')
                supabase.table("classificacoes_financeiras").upsert(data_classificao).execute()

                st.success("Transações salvas com sucesso!")
                del st.session_state["df_processado"]