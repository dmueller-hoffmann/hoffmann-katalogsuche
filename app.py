import streamlit as st
import pandas as pd
import os

# --- Passwortschutz (vor dem Rest der App!) ---
def check_password():
    def password_entered():
        if st.session_state["pw"] == "karton2025":
            st.session_state["pw_correct"] = True
            del st.session_state["pw"]  # optional: entfernt das PW aus dem Session State
        else:
            st.session_state["pw_correct"] = False

    if "pw_correct" not in st.session_state:
        st.text_input("Passwort", type="password", on_change=password_entered, key="pw")
        st.stop()
    elif not st.session_state["pw_correct"]:
        st.text_input("Passwort", type="password", on_change=password_entered, key="pw")
        st.error("Falsches Passwort")
        st.stop()

check_password()

st.set_page_config(page_title="Kartons im Katalog und im Internet", layout="wide")

# Logo oben rechts, 300px breit
st.markdown(
    """
    <div style="width:100%; display: flex; justify-content: flex-end;">
        <img src="https://www.hoffmann-verpackung.de/media/vector/17/59/b3/Hoffmann_Logo.svg" width="300" />
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Kartons im Katalog und im Internet")

EXCEL_PATH = "karton.xlsx"

def load_catalog_excel(filepath):
    if not os.path.exists(filepath):
        st.error(f"Die Datei {filepath} wurde nicht gefunden.")
        st.stop()
    df = pd.read_excel(filepath)
    return df

def filter_boxes(df, length, width, height, tolerance):
    matches = []
    tol_values = []
    for _, row in df.iterrows():
        karton_l = row['Länge']
        karton_b = row['Breite']
        karton_h = row['Höhe']
        tolerance_factor = 1 + tolerance / 100.0
        abweichungen = [
            abs(karton_l - length) / max(1, length) * 100,
            abs(karton_b - width) / max(1, width) * 100,
            abs(karton_h - height) / max(1, height) * 100
        ]
        maxabweichung = max(abweichungen)
        if (karton_l >= length and karton_b >= width and karton_h >= height and
            karton_l <= length * tolerance_factor and karton_b <= width * tolerance_factor and karton_h <= height * tolerance_factor):
            matches.append(row)
            tol_values.append(round(maxabweichung, 2))
    if matches:
        df_res = pd.DataFrame(matches)
        df_res["%"] = tol_values
        df_res = df_res.sort_values("%", ascending=True, ignore_index=True)
        return df_res
    else:
        return pd.DataFrame(columns=df.columns.tolist() + ["%"])

def create_link(url, text):
    if pd.isna(url) or not str(url).startswith("http"):
        return ""
    return f'<a href="{url}" target="_blank">{text}</a>'

def create_directlink(nr):
    if pd.isna(nr):
        return ""
    url = f"https://www.hoffmann-verpackung.de/search?sSearch={nr}"
    return f'<a href="{url}" target="_blank">Direktlink</a>'

def enrich_links(df):
    df = df.copy()
    if "KATALOG" in df.columns and "Katalogseite" not in df.columns:
        df["Katalogseite"] = df["KATALOG"].apply(lambda url: create_link(url, "zur Katalogseite"))
    elif "Katalog-URL" in df.columns and "Katalogseite" not in df.columns:
        df["Katalogseite"] = df["Katalog-URL"].apply(lambda url: create_link(url, "zur Katalogseite"))
    if "URL" in df.columns and "Webshop" not in df.columns:
        df["Webshop"] = df["URL"].apply(lambda url: create_link(url, "zum Webshop"))
    if "Nr." in df.columns and "Direktlink" not in df.columns:
        df["Direktlink"] = df["Nr."].apply(create_directlink)
    if "KATALOG" in df.columns:
        df = df.drop(columns=["KATALOG"])
    return df

def format_int_columns(df):
    df = df.copy()
    for col in ["Länge", "Breite", "Höhe", "Seite"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df

# --- CSS für Tabellen-Layout und Toleranzfeld ---
st.markdown("""
    <style>
    .centered-wrapper {
        display: flex;
        justify-content: center;
        margin: 0;
        width: 100%;
    }
    .table-80 {
        width: 80vw !important;
        margin: 0 auto;
    }
    .table-80 table {
        width: 100% !important;
        table-layout: auto !important;
        white-space: nowrap;
        border-collapse: collapse;
        margin: 0 auto;
    }
    .table-80 th, .headline-blue {
        text-align: center !important;
        vertical-align: middle !important;
        background: #f0f0ff;
        font-weight: bold;
        font-size: 18px !important;
        color: #003366 !important;
    }
    .search-results tr:nth-child(even) {
        background-color: #e6ffe6 !important;
    }
    .search-results tr:nth-child(odd) {
        background-color: white !important;
    }
    .karton-table tr:nth-child(even) {
        background-color: #e6f0ff !important;
    }
    .karton-table tr:nth-child(odd) {
        background-color: white !important;
    }
    .toleranz-div {
        width: 10vw !important;
        min-width: 100px;
        display: block;
        margin-top: 8px;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

df = load_catalog_excel(EXCEL_PATH)
df = enrich_links(df)
df = format_int_columns(df)

spalten = df.columns.tolist()

if "run_search" not in st.session_state:
    st.session_state["run_search"] = True

if "toleranz" not in st.session_state:
    st.session_state["toleranz"] = 50

def trigger_search():
    st.session_state["run_search"] = True

# --- Eingabefelder ---
st.header("Kartonmaße eingeben")
col1, col2, col3 = st.columns(3)
with col1:
    length = st.number_input("Länge (mm)", min_value=0, value=300, key="length", on_change=trigger_search)
with col2:
    width = st.number_input("Breite (mm)", min_value=0, value=300, key="width", on_change=trigger_search)
with col3:
    height = st.number_input("Höhe (mm)", min_value=0, value=300, key="height", on_change=trigger_search)

# Toleranzfeld unter die drei Abmessungen, 10% Breite
st.markdown('<div class="toleranz-div">', unsafe_allow_html=True)
tolerance = st.number_input(
    "Toleranz (%)", min_value=0, max_value=100,
    value=st.session_state["toleranz"], key="toleranz",
    help="Abweichung in %", step=1, on_change=trigger_search
)
st.markdown('</div>', unsafe_allow_html=True)

st.write(f"Aktuelle Toleranz: {st.session_state['toleranz']}%")

if st.button("Suchen"):
    st.session_state["run_search"] = True

if st.session_state["run_search"]:
    results = filter_boxes(
        df,
        st.session_state["length"],
        st.session_state["width"],
        st.session_state["height"],
        st.session_state["toleranz"]
    )
    results = enrich_links(results)
    results = format_int_columns(results)
    treffer = len(results)
    if "%" in results.columns:
        ordered_cols = [col for col in spalten if col in results.columns] + ["%"]
        results = results[ordered_cols]
    if not results.empty:
        st.markdown(
            f"<div class='headline-blue' style='text-align:center;margin-bottom:10px'>{treffer} Ergebnis{'se' if treffer != 1 else ''} gefunden</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="centered-wrapper"><div class="table-80 search-results">{results.to_html(escape=False, index=False, classes="table-80 search-results")}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Keine passenden Kartons gefunden.")
    st.session_state["run_search"] = False

st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)  # etwas Abstand

st.subheader("Alle verfügbaren Kartons")
st.markdown(
    f'<div class="centered-wrapper"><div class="table-80 karton-table">{df.to_html(escape=False, index=False, classes="table-80 karton-table")}</div></div>',
    unsafe_allow_html=True
)
