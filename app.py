import streamlit as st

st.set_page_config(page_title="Score board", layout="wide")

pages = [
    st.Page("scoreboard.py",title="Socre Board", default=True),
    st.Page("add_partie.py", title="Ajouter une partie", icon="➕"),
    st.Page("historique.py", title="Historique", icon="📅"),
]

pg = st.navigation(pages)
pg.run()
