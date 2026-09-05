import streamlit as st
import pandas as pd
from utils import charger_donnees

st.title("Score Board FlipSeven du CARISM")

conn = charger_donnees()
df_normalize = pd.DataFrame(st.session_state.df.columns[3:], columns=["Player"])
for _, partie in st.session_state.df.iterrows():
    coef = 200 / partie["Score_max"]
    scores = pd.to_numeric(partie[3:], errors="coerce")  # convertit en nombre, "" et texte invalide -> NaN
    df_normalize[partie["Id"]] = (scores * coef).values

df_normalize["Somme"] = df_normalize[df_normalize.columns[1:]].sum(axis=1)
df_normalize["nb_partie"] = df_normalize[df_normalize.columns[1:-1]].notna().sum(axis=1)
df_normalize["Moyenne"] = df_normalize["Somme"]/df_normalize["nb_partie"] 
by = st.segmented_control("Affichage",options=["Moyenne","Somme"],default="Moyenne")
st.bar_chart(df_normalize[["Player",by]],x="Player",x_label=by,sort=f"-{by}",horizontal=True)
if st.button("➕ Ajouter une partie"):
    st.switch_page("add_partie.py")

st.title("Dernières parties")
st.page_link("historique.py", label="Voir l'historique des parties")
def partie_score(raw):
    result = raw.dropna()
    name = f"Partie {raw['Id']} ({raw['Date']})"
    result = result.rename("Score")
    result = result.drop(["Score_max",'Id','Date'])
    return name, result

name_last1, last1 = partie_score(st.session_state.df.iloc[-1])
name_last2, last2 = partie_score(st.session_state.df.iloc[-2])
name_last3, last3 = partie_score(st.session_state.df.iloc[-3])

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader(name_last3)
    st.dataframe(last3)
with col2:
    st.subheader(name_last2)
    st.dataframe(last2)
with col3:
    st.subheader(name_last1)
    st.dataframe(last1)

