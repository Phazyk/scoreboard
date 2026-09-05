import streamlit as st
from streamlit_gsheets import GSheetsConnection


def charger_donnees():
    """Connecte à Google Sheets et charge le DataFrame dans session_state s'il n'y est pas déjà."""
    conn = st.connection("gsheets", type=GSheetsConnection)
    if "df" not in st.session_state:
        df = conn.read(worksheet="Feuille1", ttl=0)
        df["Id"] = df["Id"].astype(int)
        df = df.set_index("Id", drop=False)
        df = df.dropna(how="all")
        st.session_state.df = df
    return conn
