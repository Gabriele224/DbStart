from fpdf import FPDF
import streamlit as st
import pandas as pd
import numpy as np
import gspread
import json

# 🔑 Carico credenziali dal secrets
sa_info = json.loads(st.secrets["gcp_service_account"])
gc = gspread.service_account_from_dict(sa_info)

# 📒 Apri i 3 fogli separati
SPREADSHEET_ID_UTENTE="1UgYZJ3zos9eGukjfZI0ALZY8rHoJaRdbs0OnE8uQCLE"    # <--- sostituisci con ID foglio UtenteCentro
SPREADSHEET_ID_PASTO="1d2919LVkliCn7NozU96ozhac1B8tiBhlHWS8_B49hlc" #<-- id pasto-->
SPREADSHEET_ID_PESO ="1Dd1jz668WTiR1gR7DjL23oebMzQ_SEQmytQoE3lxQcg"             # <--- sostituisci con ID foglio Peso E Massa
#SPREADSHEET_ID_PROFILEMICRO= ""  # ID foglio ProfileMicro

ws_utente= gc.open_by_key(SPREADSHEET_ID_UTENTE).sheet1
ws_pasto= gc.open_by_key(SPREADSHEET_ID_PASTO).sheet1
ws_peso = gc.open_by_key(SPREADSHEET_ID_PESO).sheet1
#ws_profilemicro= gc.open_by_key(SPREADSHEET_ID_PROFILEMICRO).sheet1

# Funzione helper per leggere worksheet → DataFrame
def ws_to_df(ws):
    data = ws.get_all_records()
    return pd.DataFrame(data)

# Carica dati iniziali
db_utente= ws_to_df(ws_utente)
db_Pasto=ws_to_df(ws_pasto)
db_pesoPersonale = ws_to_df(ws_peso)
#db_profile= ws_to_df(ws_profilemicro)

"""def genera_pdf(df_combined):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page("landscape")
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Report Dashboard Alimentare", ln=True, align="C")
    pdf.ln(10)

    pdf.set_fill_color(255, 100, 0)  # Colore di riempimento intestazione
    pdf.set_text_color(255, 255, 255)  # Colore testo intestazione
    col_widths = [20, 25, 25, 15, 45, 35, 25, 25, 25, 15]  # Larghezze delle colonne
    headers = ["Data", "glicemia", "Pasto", "orario", "note", "Alimento", "TotPeso", "TotCho", "TotKcal", "Insulina"]

    # Raggruppa per data
    gruppi = df_combined.groupby("data")

    for data, gruppo in gruppi:
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 0, 128)
        pdf.cell(0, 10, f"Data: {data}", ln=True)
        pdf.set_text_color(0, 0, 0)
        # Aggiungi i dati alla tabella
        pdf.set_font("Helvetica", "", 5)
        pdf.set_text_color(0, 0, 0)  # Colore testo dati
        pdf.set_fill_color(224, 235, 255)  # Colore delle celle alternate
        # Intestazioni
        pdf.set_font("Arial", style="B", size=10)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 5, header, border="L", align="C", fill=True)
        pdf.ln()

    
        # Riga dei dati
        pdf.set_font("Helvetica", size=8)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(224, 235, 255)  # Colore delle celle alternate
        fill = False
        gruppo["totKcal"] = pd.to_numeric(gruppo["totKcal"], errors="coerce")
        gruppo["totPeso"] = pd.to_numeric(gruppo["totPeso"], errors="coerce")
        gruppo["totCho"] = pd.to_numeric(gruppo["totCho"], errors="coerce")
        gruppo["insulina"]= pd.to_numeric(gruppo["insulina"], errors="coerce")
        gruppo["glicemia"] = pd.to_numeric(gruppo["glicemia"], errors="coerce")

        totKcal= gruppo["totKcal"].sum()

        totPeso= gruppo["totPeso"].sum()

        totCho= gruppo["totCho"].sum()
        
        totInsulina=gruppo["insulina"].sum()

        mediaGlicemia = gruppo["glicemia"].mean()

        emogloglicata = (mediaGlicemia + 47.6) / 27.6 if not np.isnan(mediaGlicemia) else 0
        
        for idx, record in gruppo.iterrows():
            pdf.cell(col_widths[0], 8, str(record.get("data", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[1], 8, str(record.get("glicemia", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[2], 8, str(record.get("tipoPasto", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[3], 8, str(record.get("orario", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[4], 8, str(record.get("note", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[5], 8, str(record.get("nomeAlimento", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[6], 8, str(record.get("totPeso", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[7], 8, str(record.get("totCho", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[8], 8, str(record.get("totKcal", "")), border=1, align="C", fill=fill)
            pdf.cell(col_widths[9], 8, str(record.get("insulina", "")), border=1, align="C", fill=fill)
            pdf.ln()
            fill = not fill
        
        pdf.cell(col_widths[6], 8, f"Tot Kcal:{totKcal:.0f}",border=1,align="L",fill=fill)
        pdf.cell(col_widths[7], 8, f"Tot Peso:{totPeso:.0f}",border=1,align="L",fill=fill)
        pdf.cell(col_widths[8], 8, f"Tot Cho:{totCho:.0f}",border=1,align="L",fill=fill)
        pdf.cell(col_widths[9], 8, f"Insulina:{totInsulina:.0f}",border=1,align="L",fill=fill)
        pdf.cell(col_widths[1], 8, f"M.Glicemia:{mediaGlicemia:.0f}",border=1,align="L",fill=fill)
        pdf.cell(col_widths[0], 8, f"HBA1C:{emogloglicata:.0f}",border=1,align="L",fill=fill)
        pdf.ln(10)

    return bytes(pdf.output(dest="S"))


#PDF COMPLETO
st.subheader("PDF")

view_pdf= st.selectbox("Visualizza PDF\n",["PDF"])
if view_pdf:
    if view_pdf=="PDF":

        date_inizio=st.date_input("Data D'Inizio")
        date_fine=st.date_input("Data Di Fine")
            
        lista_utents = db_utente["username"].tolist()
        username_list = st.selectbox("User", lista_utents)

        # Controlliamo che le colonne chiave esistano
        if "id_pasto" not in db_Pasto.columns:
            st.warning("⚠️ La tabella 'DiarioPasti' non contiene 'id_pasto'. Controlla il Google Sheet.")
        if "id_pasto_sel" not in db_alimento.columns:
            st.warning("⚠️ La tabella 'AlimentoConsumato' non contiene 'id_pasto_sel'. Controlla il Google Sheet.")
    
        # Rinomina id_pasto_sel → id_pasto per la join
        if "id_pasto_sel" in db_alimento.columns:
            db_alimento = db_alimento.rename(columns={"id_pasto_sel": "id_pasto"})

        db_Pasto["data"]=pd.to_datetime(db_Pasto["data"])
        
        df_filtrato=db_Pasto[
            (db_Pasto["data"] >= pd.to_datetime(date_inizio)) &
            (db_Pasto["data"] <= pd.to_datetime(date_fine))
        ]
        
        # 🔥 TOGLIE L'ORA DALLA DATA
        df_filtrato["data"] = df_filtrato["data"].dt.strftime("%Y-%m-%d")
        # Esegui join tra DiarioPasti e AlimentoConsumato
        try:
            df_filtrato = pd.merge(df_filtrato, db_alimento, on="id_pasto", how="outer")
        except Exception as e:
            st.error(f"❌ Errore nella join: {e}")
            st.stop()
    
        data_inizio_str = date_inizio.strftime("%Y-%m-%d")
        data_fine_str = date_fine.strftime("%Y-%m-%d")

        pdf_bytes = genera_pdf(df_filtrato)
        st.download_button(
            label="📄 Scarica PDF",
            data=pdf_bytes,
            file_name=f"{username_list} - {data_inizio_str} e {data_fine_str}.pdf",
            mime="application/pdf"
        )
else:
    st.success("Nessun errore")"""
# --------------------- INSERIMENTO DATI ---------------------

st.subheader("Aggiungere L'UtenteCentro Nel DB")

with st.form("form_utente"):
    username = st.text_input("Username")
    NomeUtente = st.text_input("NomeUtente")
    CognomeUtente = st.text_input("Cognome")
    dataNascita = st.date_input("Data")
    CittaUtente= st.text_input("CittaUtente")
    CfUtente= st.text_input("CfUtente")
    CentroDiabetologico= st.text_input("CentroDiabetologico")

    try:

        invia_utente = st.form_submit_button("Salva Utente")
        if invia_utente:
            nuovoUtente = [username, NomeUtente, CognomeUtente, dataNascita.strftime("%Y-%m-%d"), CittaUtente, CfUtente, CentroDiabetologico]
            ws_utente.append_row(nuovoUtente)
            st.success(f"✅ Nuovo Utente salvato!\n{nuovoUtente}")
            
    except Exception as e:
        st.error(f"Utente Mancante.\nAggiungere prima l'utente la tabella è ancora vuota!\n{e}")

st.subheader("Aggiungere Il Pasto Nel DB")

with st.form("form_pasto"):
    glicemia = st.number_input("Glicemia", max_value=1000)
    tipoPasto = st.selectbox("TipoPasto",["PrimaDiColazione","Colazione","DopoColazione","Spuntino1","DopoSpuntino1","Pranzo","DopoPranzo","Spuntino2","DopoSpuntino2","PrimaDiCena","Cena","DopoCena","Notte"])
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
            nuovoPasto = [id_pasto, glicemia, tipoPasto, orario, data.strftime("%Y-%m-%d"), note, username_sel]
            ws_pasto.append_row(nuovoPasto)
            st.success(f"✅ Nuovo pasto salvato!\n{nuovoPasto}")

    except Exception as e:
        st.error(f"Username Mancante.\nAggiungere prima l'user, la tabella è ancora vuota!\n{e}")

st.subheader("Aggiungere I Dati Peso e Altezza Nel DB")

with st.form("form_pesoPersonale"):
    pesoPersonale = st.number_input("Peso",max_value=100.0,format="%.2f")
    altezza = st.number_input("Altezza",max_value=2.40,format="%.2f")
    data = st.date_input("Data")

    try:
        altezza=float(altezza)
        massaCorporea= pesoPersonale / (altezza ** 2)
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
        nuovoPeso = [id_peso, pesoPersonale, massaCorporea, data.strftime("%Y-%m-%d"), username_sel]
        ws_peso.append_row(nuovoPeso)
        st.success(f"✅ Nuovo peso salvato!\n{nuovoPeso}")