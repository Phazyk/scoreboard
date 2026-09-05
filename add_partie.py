import streamlit as st
import pandas as pd
from utils import charger_donnees

if "score" not in st.session_state:
    st.session_state.score = dict()
if "show_score_step" not in st.session_state:
    st.session_state.show_score_step = False

st.title("Ajouter des parties ou des joueuses/joueurs")

conn = charger_donnees()
option_joueur = st.session_state.df.columns[3:]
nb_game = len(st.session_state.df)

st.page_link("scoreboard.py", label="⬅️ Retour au Score Board", icon="🏠")

# ==========================================================
# Ajout d'un(e) joueur/joueuse
# ==========================================================
with st.expander("Ajouter un(e) joueur/joueuse"):
    with st.form("nouveau_joueur", clear_on_submit=True):
        nouveau_nom = st.text_input("Nom du/de la nouveau/nouvelle joueur/joueuse")
        submitted = st.form_submit_button("➕ Ajouter la colonne")

        if submitted:
            if not nouveau_nom:
                st.warning("Merci de saisir un nom.")
            elif nouveau_nom in st.session_state.df.columns:
                st.warning("Cette personne existe déjà.")
            else:
                st.session_state.df[nouveau_nom] = pd.NA
                conn.update(worksheet="Feuille1", data=st.session_state.df)
                st.success(f"{nouveau_nom} rejoins la compétition !")
                st.cache_data.clear()
                st.rerun()

# ==========================================================
# Ajout d'une nouvelle partie
# ==========================================================
with st.expander("➕ Ajouter une nouvelle partie", expanded=st.session_state.show_score_step):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date")
    with col2:
        Joueur = st.multiselect("Joueuses/Joueurs", options=option_joueur)
    with col3:
        Score_max = st.number_input("Score max", value=200)

    if Joueur and st.button("Passez aux scores !"):
        st.session_state.show_score_step = True

    if st.session_state.show_score_step and Joueur:
        st.divider()
        Score = st.data_editor(
            pd.DataFrame(index=Joueur, columns=["Score"]),
            hide_index=False,
            key="score_editor",
        )
        if st.button("✅ Valider la partie"):
            st.session_state.score = dict(Score["Score"])
            st.session_state.show_score_step = False
            nouvelle_ligne = pd.DataFrame(st.session_state.score, index=[nb_game])
            nouvelle_ligne["Date"] = date.isoformat()
            nouvelle_ligne["Score_max"] = Score_max
            nouvelle_ligne["Id"] = nb_game + 1
            df_maj = pd.concat([st.session_state.df, nouvelle_ligne], ignore_index=True)
            conn.update(worksheet="Feuille1", data=df_maj)
            st.session_state.df = df_maj
            st.success(f"Ligne ajoutée pour le {date} !")
            st.cache_data.clear()
            st.rerun()
