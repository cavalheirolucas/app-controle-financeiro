import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_client():

    url = os.getenv("SUPABASE_URL")
    token = os.getenv("SUPABASE_TOKEN")

    Client = create_client(url, token)
    

    if "session" in st.session_state:
        Client.auth.set_session(
            st.session_state["session"].access_token,
            st.session_state["session"].refresh_token)
    
    return Client