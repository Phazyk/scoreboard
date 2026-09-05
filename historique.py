import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from utils import charger_donnees

if "show_details_dialog" not in st.session_state:
    st.session_state.show_details_dialog = False
if "dialog_mode" not in st.session_state:
    st.session_state.dialog_mode = "vue"

st.title("📅 Historique des parties")

conn = charger_donnees()
option_joueur = st.session_state.df.columns[3:]

st.page_link("scoreboard.py", label="⬅️ Retour au Score Board", icon="🏠")
st.divider()

# ==========================================================
# Dialog de détails / édition / suppression d'une partie
# ==========================================================
def passer_en_edition():
    st.session_state.dialog_mode = "edition"

def passer_en_suppression():
    st.session_state.dialog_mode = "suppression"

def annuler_action():
    st.session_state.dialog_mode = "vue"

def enregistrer_modification(partie_id, nouveau_score_max, scores_edit, nouveaux_scores=None):
    st.session_state.df.loc[partie_id, "Score_max"] = nouveau_score_max
    for joueur in scores_edit.index:
        st.session_state.df.loc[partie_id, joueur] = scores_edit.loc[joueur, "Score"]
    if nouveaux_scores is not None:
        for joueur in nouveaux_scores.index:
            st.session_state.df.loc[partie_id, joueur] = nouveaux_scores.loc[joueur, "Score"]
    conn.update(worksheet="Feuille1", data=st.session_state.df)
    st.cache_data.clear()
    st.session_state.show_details_dialog = False
    st.session_state.dialog_mode = "vue"

def supprimer_partie(partie_id):
    st.session_state.df = st.session_state.df.drop(index=partie_id)
    conn.update(worksheet="Feuille1", data=st.session_state.df)
    st.cache_data.clear()
    st.session_state.show_details_dialog = False
    st.session_state.dialog_mode = "vue"

def fermer_details():
    st.session_state.show_details_dialog = False
    st.session_state.dialog_mode = "vue"


@st.dialog("Détails de la partie", on_dismiss=fermer_details)
def details_partie(event):
    props = event.get("extendedProps", {})
    partie_id = props.get("id")
    mode = st.session_state.dialog_mode

    if mode == "vue":
        st.subheader(f"{event['title']} ({event['start']})")
        st.write(f"**Score max :** {props.get('score_max')}")
        st.dataframe(props.get("scores_detail"),column_config={"value":"Score"})

        col1, col2 = st.columns(2)
        col1.button("✏️ Modifier", on_click=passer_en_edition, use_container_width=True)
        col2.button("🗑️ Supprimer", on_click=passer_en_suppression, type="primary", use_container_width=True)

    elif mode == "edition":
        st.subheader("Modifier la partie")
        nouveau_score_max = st.number_input("Score max", value=int(props.get("score_max", 0)))
        scores_edit = pd.DataFrame.from_dict(props.get("scores_detail", {}), orient="index", columns=["Score"])
        scores_edit = st.data_editor(scores_edit, key="edit_scores")

        joueurs_dans_partie = list(props.get("scores_detail", {}).keys())
        joueurs_disponibles = [j for j in option_joueur if j not in joueurs_dans_partie]

        nouveaux_joueurs = st.multiselect(
            "Ajouter un(e) joueur/joueuse à cette partie",
            options=joueurs_disponibles,
            key="nouveaux_joueurs_partie",
        )

        nouveaux_scores = None
        if nouveaux_joueurs:
            st.caption("Scores des nouveaux/nouvelles joueurs/joueuses")
            nouveaux_scores = st.data_editor(
                pd.DataFrame(index=nouveaux_joueurs, columns=["Score"]),
                hide_index=False,
                key="nouveaux_scores_partie",
            )

        col1, col2 = st.columns(2)
        col1.button(
            "💾 Enregistrer", type="primary", use_container_width=True,
            on_click=enregistrer_modification, args=(partie_id, nouveau_score_max, scores_edit, nouveaux_scores),
        )
        col2.button("Annuler", on_click=annuler_action, use_container_width=True)

    elif mode == "suppression":
        st.warning(f"Confirmer la suppression de « {event['title']} » ? Cette action est irréversible.")
        col1, col2 = st.columns(2)
        col1.button(
            "✅ Confirmer", type="primary", use_container_width=True,
            on_click=supprimer_partie, args=(partie_id,),
        )
        col2.button("Annuler", on_click=annuler_action, use_container_width=True)


# ==========================================================
# Calendrier
# ==========================================================
calendar_events = []

def ligne_to_event(ligne, n):
    event = {}
    event["title"] = f"Partie {ligne.Id}"
    event["start"] = ligne["Date"].isoformat() if hasattr(ligne["Date"], "isoformat") else str(ligne["Date"])
    event["extendedProps"] = {
        "id": ligne["Id"],
        "score_max": ligne["Score_max"],
        "scores_detail": ligne[3:].dropna().to_dict(),
    }
    return event

for n, ligne in st.session_state.df.iterrows():
    calendar_events.append(ligne_to_event(ligne, n))

calendar_result = calendar(events=calendar_events, key="calendar")

if calendar_result.get("callback") == "eventClick":
    click_id = str(calendar_result["eventClick"])
    if click_id != st.session_state.get("last_click_id"):
        st.session_state.last_click_id = click_id
        st.session_state.event_selectionne = calendar_result["eventClick"]["event"]
        st.session_state.show_details_dialog = True
        st.session_state.dialog_mode = "vue"

if st.session_state.show_details_dialog:
    details_partie(st.session_state.event_selectionne)
