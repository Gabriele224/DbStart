from fpdf import FPDF
import streamlit as st
import pandas as pd
import numpy as np
import gspread

# 🔑 Carico credenziali dal secrets
sa_info = dict(st.secrets["gcp_service_account"])

# Converte eventuali \n scritti letteralmente in ritorni a capo
sa_info["private_key"] = sa_info["private_key"].replace("\\n", "\n")

# Collegamento Google Sheets
gc = gspread.service_account_from_dict(sa_info)

# ID dei tre fogli
SPREADSHEET_ID_UTENTE = "1UgYZJ3zos9eGukjfZI0ALZY8rHoJaRdbs0OnE8uQCLE"
SPREADSHEET_ID_PASTO = "1d2919LVkliCn7NozU96ozhac1B8tiBhlHWS8_B49hlc"
SPREADSHEET_ID_ALIMENTO = "1gL4ADLoJJq2E0lJ9DAa_v9cLXKGWX8UAIDJTizOI6Sk"  # <--- sostituisci con ID foglio AlimentoConsumato
SPREADSHEET_ID_PESO = "1Dd1jz668WTiR1gR7DjL23oebMzQ_SEQmytQoE3lxQcg"

# Apri i fogli
ws_utente = gc.open_by_key(SPREADSHEET_ID_UTENTE).sheet1
ws_pasto = gc.open_by_key(SPREADSHEET_ID_PASTO).sheet1
ws_alimento = gc.open_by_key(SPREADSHEET_ID_ALIMENTO).sheet1
ws_peso = gc.open_by_key(SPREADSHEET_ID_PESO).sheet1


# Funzione per leggere il foglio
def ws_to_df(ws):
    data = ws.get_all_records()
    return pd.DataFrame(data)


# Carica i dati
db_utente = ws_to_df(ws_utente)
db_Pasto = ws_to_df(ws_pasto)
db_alimento = ws_to_df(ws_alimento)
db_pesoPersonale = ws_to_df(ws_peso)

# --------------------- INSERIMENTO DATI ---------------------

st.subheader("Aggiungere L'UtenteCentro Nel DB")

with st.form("form_utente"):
    username = st.text_input("Username")
    NomeUtente = st.text_input("NomeUtente")
    CognomeUtente = st.text_input("Cognome")
    dataNascita = st.date_input("Data")
    CittaUtente = st.text_input("CittaUtente")
    CfUtente = st.text_input("CfUtente")
    CentroDiabetologico = st.text_input("CentroDiabetologico")

    try:

        invia_utente = st.form_submit_button("Salva Utente")
        if invia_utente:
            nuovoUtente = [
                username,
                NomeUtente,
                CognomeUtente,
                dataNascita.strftime("%Y-%m-%d"),
                CittaUtente,
                CfUtente,
                CentroDiabetologico,
            ]
            ws_utente.append_row(nuovoUtente)
            st.success(f"✅ Nuovo Utente salvato!\n{nuovoUtente}")

    except Exception as e:
        st.error(
            f"Utente Mancante.\nAggiungere prima l'utente la tabella è ancora vuota!\n{e}"
        )

st.subheader("Aggiungere Il Pasto Nel DB")

with st.form("form_pasto"):
    glicemia = st.number_input("Glicemia", max_value=1000)
    tipoPasto = st.selectbox(
        "TipoPasto",
        [
            "PrimaDiColazione",
            "Colazione",
            "DopoColazione",
            "Spuntino1",
            "DopoSpuntino1",
            "Pranzo",
            "DopoPranzo",
            "Spuntino2",
            "DopoSpuntino2",
            "PrimaDiCena",
            "Cena",
            "DopoCena",
            "Notte",
        ],
    )
    orario = st.text_input("Orario")
    data = st.date_input("Data")
    note = st.text_input("Note")

    try:

        # Seleziona utente da lista utenti reali
        if db_utente.empty:
            st.warning("⚠️ Nessun utente registrato.")
            st.stop()

        lista_utenti = db_utente["username"].dropna().astype(str).tolist()
        username_sel = st.selectbox("Seleziona Username", lista_utenti)

        # esempio per DiarioPasti
        if len(db_Pasto) == 0:
            id_pasto = 1
        else:
            id_pasto = max(db_Pasto["id_pasto"].astype(int)) + 1

        invia = st.form_submit_button("Salva Pasto")
        if invia:
            nuovoPasto = [
                id_pasto,
                glicemia,
                tipoPasto,
                orario,
                data.strftime("%Y-%m-%d"),
                note,
                username_sel,
            ]
            ws_pasto.append_row(nuovoPasto)
            st.success(f"✅ Nuovo pasto salvato!\n{nuovoPasto}")

    except Exception as e:
        st.error(
            f"Username Mancante.\nAggiungere prima l'user, la tabella è ancora vuota!\n{e}"
        )

st.subheader("Aggiungere L'Alimento Nel DB")

with st.form("form_alimento"):
    nomeAlimento = st.text_input("Alimento")
    totPeso = st.number_input("TotPeso", max_value=1000.0, format="%.2f")
    totCho = st.number_input("TotCho", max_value=1000.0, format="%.2f")
    totKcal = st.number_input("TotKcal", max_value=1000.0, format="%.2f")
    insulina = st.number_input("Insulina", max_value=100.0, format="%.2f")

    try:
        data_scelta = st.date_input("Seleziona data pasto")
        data_scelta = data_scelta.strftime("%Y-%m-%d")
        db_filtrato = db_Pasto[db_Pasto["data"] == data_scelta]

        if db_filtrato.empty:
            st.warning("⚠️ Nessun pasto per la data selezionata.")

        opzioni_pasto = (
            db_filtrato["id_pasto"].astype(str)
            + " - "
            + db_filtrato["tipoPasto"].astype(str)
            + " ("
            + db_filtrato["data"].astype(str)
            + ")"
            + " ("
            + db_filtrato["usernameId"].astype(str)
            + ")"
        )

        scelta = st.selectbox("Scegli il pasto", opzioni_pasto)
        id_pasto_sel = int(scelta.split(" - ")[0])

        # esempio per DiarioPasti
        if len(db_alimento) == 0:
            id_alimento = 1
        else:
            id_alimento = max(db_alimento["id_alimento"].astype(int)) + 1

        invia_alimento = st.form_submit_button("Salva Alimento")
        if invia_alimento:
            nuovoAlimento = [
                id_alimento,
                nomeAlimento,
                totPeso,
                totCho,
                totKcal,
                insulina,
                id_pasto_sel,
            ]
            ws_alimento.append_row(nuovoAlimento)
            st.success(f"✅ Nuovo alimento salvato!\n{nuovoAlimento}")

    except Exception as e:
        st.error(
            f"Pasto Mancante.\nAggiungere prima il pasto la tabella è ancora vuota!\n{e}"
        )
st.subheader("Aggiungere I Dati Peso e Altezza Nel DB")

with st.form("form_pesoPersonale"):
    pesoPersonale = st.number_input("Peso", max_value=100.0, format="%.2f")
    altezza = st.number_input("Altezza", max_value=2.40, format="%.2f")
    data = st.date_input("Data")

    try:
        altezza = float(altezza)
        massaCorporea = pesoPersonale / (altezza**2)
        st.success(f"Massa Corporea Calcolata:{massaCorporea:.2f}")

    except ZeroDivisionError as e:
        st.error(f"Impossibile dividere per zero!\n{e}")

    # Seleziona utente da lista utenti reali
    if db_utente.empty:
        st.warning("⚠️ Nessun utente registrato.")
        st.stop()

    lista_utenti = db_utente["username"].tolist()
    username_sel = st.selectbox("Seleziona Username", lista_utenti)

    if len(db_pesoPersonale) == 0:
        id_peso = 1
    else:
        id_peso = max(db_pesoPersonale["id_peso"].astype(int)) + 1

    invia_PesoPersonale = st.form_submit_button("Salva Peso")
    if invia_PesoPersonale:
        nuovoPeso = [
            id_peso,
            pesoPersonale,
            massaCorporea,
            data.strftime("%Y-%m-%d"),
            username_sel,
        ]
        ws_peso.append_row(nuovoPeso)
        st.success(f"✅ Nuovo peso salvato!\n{nuovoPeso}")

# <---Ottenimento meida glicemica--->
st.subheader("Media Glicemia")

username_pasto = st.selectbox(
    "Utente", db_Pasto["usernameId"].unique(), key="utente_glicemia"
)

data_inizio_glice = st.date_input("Data inizio")
data_fine_glice = st.date_input("Data fine")

df_glice = db_Pasto[
    (db_Pasto["usernameId"] == username)
    & (pd.to_datetime(db_Pasto["data"]).dt.date >= data_inizio_glice)
    & (pd.to_datetime(db_Pasto["data"]).dt.date <= data_fine_glice)
]

st.write("Media glicemia:", df_glice["glicemia"].mean())

# <---Ottenimento media peso e massa--->
st.subheader("Media Peso e Massa")

username_pesomassa = st.selectbox(
    "Utente", db_pesoPersonale["username"].unique(), key="utente_pesomassa"
)

data_inizio_pm = st.date_input("Data inizio PM", key="data inizio pm")
data_fine_pm = st.date_input("Data fine PM", key="data fine pm")

df_pm = db_pesoPersonale[
    (db_pesoPersonale["username"] == username_pesomassa)
    & (pd.to_datetime(db_pesoPersonale["data"]).dt.date >= data_inizio_pm)
    & (pd.to_datetime(db_pesoPersonale["data"]).dt.date <= data_fine_pm)
]

st.write("Media Peso:", df_pm["pesoPersonale"].mean())
st.write("Media Massa:", df_pm["massaCorporea"].mean())

st.subheader("Media Carb,peso,kcal")

username_alimento = st.selectbox(
    "Utente", db_Pasto["usernameId"].unique(), key="utente_alimento"
)

data_inizio_alimento = st.date_input("Data inizio Ali", key="data inizio Ali")
data_fine_alimento = st.date_input("Data fine Ali", key="data fine Ali")

df_pasti = db_Pasto[
    (db_Pasto["usernameId"] == username_alimento)
    & (pd.to_datetime(db_Pasto["data"]).dt.date >= data_inizio_alimento)
    & (pd.to_datetime(db_Pasto["data"]).dt.date <= data_fine_alimento)
]

df_alimento=db_alimento[

    db_alimento["pastoId"].isin(db_Pasto["id_pasto"])
]
st.write("Tot Peso:", df_alimento["totPeso"].sum())
st.write("Tot Cho:", df_alimento["totCho"].sum())
st.write("Tot Kcal:", df_alimento["totKcal"].sum())
st.write("Tot insulina:", df_alimento["insulina"].sum())
