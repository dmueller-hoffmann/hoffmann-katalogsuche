# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Katalogsuche – Hoffmann Verpackung", layout="wide")

st.markdown(
    "<div style='background-color:#00549F; color:white; padding:4px 10px; font-size:8pt; text-align:left;'>"
    "Stand April 2025 / Katalog 2024 – Rückfragen an dmueller@hoffmann-verpackung.de"
    "</div>",
    unsafe_allow_html=True
)


# Logo
st.markdown(
    '<a href="https://www.hoffmann-verpackung.de" target="_blank"><img src="https://www.hoffmann-verpackung.de/media/vector/17/59/b3/Hoffmann_Logo.svg" width="300" style="float:left;"/></a>',
    unsafe_allow_html=True
)

st.markdown("## 📦 Kartonsuche im Hauptkatalog")

# Daten laden
df = pd.read_csv("karton_lookup.csv")
pdf_url = "https://www.hoffmann-verpackung.de/media/pdf/3d/56/10/Hoffmann-Verpackung-Hauptkatalog.pdf"
toleranz = 0.3

# Style
st.markdown("""
    <style>
    .stTextInput input {
        width: 6em !important;
    }
    .stButton > button {
        background-color: #00549F;
        color: white;
        font-weight: bold;
    }
    table td, table th {
        text-align: center !important;
    }
    .stNumberInput input {
        max-width: 100px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Eingabe
with st.form(key="suche_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([1, 1, 1])
    l_input = col1.text_input("Länge", max_chars=4)
    b_input = col2.text_input("Breite", max_chars=4)
    h_input = col3.text_input("Höhe", max_chars=4)
    submit = st.form_submit_button("Suchen")

def make_link(text, url):
    return f'<a href="{url}" target="_blank">{text}</a>'

df_result = pd.DataFrame()

if submit:
    l, b, h = int(l_input), int(b_input), int(h_input)
    st.write("Eingegeben:", l, b, h)

    def berechne_ähnlichkeit(row):
        try:
            abw_l = abs(l - row['Länge']) / l if l else 1
            abw_b = abs(b - row['Breite']) / b if b else 1
            abw_h = abs(h - row['Höhe']) / h if h else 1
            return round((1 - min((abw_l + abw_b + abw_h) / 3, 1)) * 100)
        except:
            return 0

    df["Ähnlichkeit (%)"] = df.apply(berechne_ähnlichkeit, axis=1)
    df_result = df[
        (abs(df["Länge"] - l) / l <= toleranz) &
        (abs(df["Breite"] - b) / b <= toleranz) &
        (abs(df["Höhe"] - h) / h <= toleranz)
    ].sort_values(by="Ähnlichkeit (%)", ascending=False)

if not df_result.empty:
    st.markdown("""
<style>
table.dataframe tbody tr:nth-child(even) {
    background-color: #f2f2f2;
}
</style>
""", unsafe_allow_html=True)

    st.markdown(f"### ✅ {len(df_result)} passende Verpackungen gefunden:")
    df_result["zum Katalog"] = df_result["Seite"].apply(
        lambda s: make_link("zum Katalog", f"{pdf_url}#page={int(float(s))}") if pd.notna(s) and str(s).replace('.0','').isdigit() else "-"
    )
    df_result["Google"] = df_result["Nr."].apply(
        lambda a: make_link("Google", f"https://www.google.com/search?q={urllib.parse.quote(str(a))}+Hoffmann+Verpackung") if pd.notna(a) else "-"
    )
    df_result = df_result.rename(columns={"Nr.": "Artikelnummer"})
    df_result["Länge"] = df_result["Länge"].fillna(0).astype(int)
    df_result["Breite"] = df_result["Breite"].fillna(0).astype(int)
    df_result["Höhe"] = df_result["Höhe"].fillna(0).astype(int)
    df_result["Seite"] = df_result["Seite"].fillna(0).astype(int)

    st.write(
        df_result[["Artikelnummer", "Beschreibung", "Länge", "Breite", "Höhe", "Qualität", "Seite",
                   "Ähnlichkeit (%)", "zum Katalog", "Google"]]
        .to_html(escape=False, index=False), unsafe_allow_html=True
    )
elif submit:
    st.info("Keine passenden Artikel gefunden.")

# Gesamtliste
st.markdown("### 📋 Gesamte Artikelliste")
df["zum Katalog"] = df["Seite"].apply(
    lambda s: make_link("zum Katalog", f"{pdf_url}#page={int(float(s))}") if pd.notna(s) and str(s).replace('.0','').isdigit() else "-"
)
df["Google"] = df["Nr."].apply(
    lambda a: make_link("Google", f"https://www.google.com/search?q={urllib.parse.quote(str(a))}+Hoffmann+Verpackung") if pd.notna(a) else "-"
)
df = df.rename(columns={"Nr.": "Artikelnummer"})
df["Länge"] = df["Länge"].fillna(0).astype(int)
df["Breite"] = df["Breite"].fillna(0).astype(int)
df["Höhe"] = df["Höhe"].fillna(0).astype(int)
df["Seite"] = df["Seite"].fillna(0).astype(int)
st.write(
    df[["Artikelnummer", "Beschreibung", "Länge", "Breite", "Höhe", "Qualität", "Seite",
        "zum Katalog", "Google"]].to_html(escape=False, index=False), unsafe_allow_html=True
)
