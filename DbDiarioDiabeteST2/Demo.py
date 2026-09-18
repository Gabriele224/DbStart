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
SPREADSHEET_ID_PESO = "1Dd1jz668WTiR1gR7DjL23oebMzQ_SEQmytQoE3lxQcg"

# Apri i fogli
ws_utente = gc.open_by_key(SPREADSHEET_ID_UTENTE).sheet1
ws_pasto = gc.open_by_key(SPREADSHEET_ID_PASTO).sheet1
ws_peso = gc.open_by_key(SPREADSHEET_ID_PESO).sheet1


# Funzione per leggere il foglio
def ws_to_df(ws):
    data = ws.get_all_records()
    return pd.DataFrame(data)


# Carica i dati
db_utente = ws_to_df(ws_utente)
db_Pasto = ws_to_df(ws_pasto)
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

st.subheader("Media Glicemia")

username = st.selectbox("Utente", db_Pasto["username"].unique())

data_inizio = st.date_input("Data inizio")
data_fine = st.date_input("Data fine")

df = db_Pasto[
    (db_Pasto["username"] == username)
    & (pd.to_datetime(db_Pasto["data"]).dt.date >= data_inizio)
    & (pd.to_datetime(db_Pasto["data"]).dt.date <= data_fine)
]

st.write("Media glicemia:", df["glicemia"].mean())

st.dataframe(df)
