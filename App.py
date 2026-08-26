import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

#TEST TEST ETST test 3

# 1. Page Config MUST be the first Streamlit command
st.set_page_config(page_title="Squad Minutes Tracker", layout="wide")

# 2. Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to read live data from Google Sheets
def load_data():
    try:
        # ttl=0 bypasses caching to fetch live data
        return conn.read(ttl=0)
    except Exception:
        # Returns an empty DataFrame with proper columns if the sheet is fresh/empty
        return pd.DataFrame(columns=["Date", "Opponent", "Competition", "Speler", "Position", "Starter", "Minutes", "Notes"])

# App Navigation
tab_entry, tab_dashboard = st.tabs(["Data Entry", "Data dashboard"])

# Default Squad Roster
squad = [
    {"Speler": "Aron", "Position": "FW"},
    {"Speler": "Jesse S", "Position": "FW"},
    {"Speler": "Jort", "Position": "MF"},
    {"Speler": "Justin", "Position": "MF"},
    {"Speler": "Owen", "Position": "MF"},
    {"Speler": "Rob", "Position": "DF"},
    {"Speler": "Ruben", "Position": "DF"},
    {"Speler": "Sam", "Position": "DF"},
    {"Speler": "Tygo", "Position": "DF"},
    {"Speler": "Bryan", "Position": "DF"},
    {"Speler": "Cheveyo", "Position": "DF"},
    {"Speler": "Jesse K", "Position": "DF"},
    {"Speler": "Mark", "Position": "DF"},
    {"Speler": "Martijn", "Position": "DF"},
    {"Speler": "Mike", "Position": "DF"},
    {"Speler": "Robin", "Position": "DF"},
    {"Speler": "Sven", "Position": "DF"},
    {"Speler": "Swen", "Position": "DF"},
    {"Speler": "Tim", "Position": "DF"},
    {"Speler": "Twan", "Position": "DF"},
    {"Speler": "Yannick", "Position": "GK"}
]
 
# ==========================================
# TAB 1: DATA ENTRY FORM
# ==========================================
with tab_entry:
    st.header("FLEVO BOYS 8 DATA LOG")
    
    # Match Metadata Inputs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        match_date = st.date_input("Wedstrijd datum")
    with col2:
        opponent = st.text_input("Tegenstander", value="SCE 5")
    with col3:
        competition = st.selectbox("Competitie", ["Beker", "Competitie", "Vriendschappelijk"])
    with col4:
        Goals_voor = st.number_input("Goals gescoord", min_value=0)
    with col5:
        Goals_tegen = st.number_input("Goals tegen", min_value=0)

    st.subheader("Lineup & Minutes")
    
    # Use st.form to group inputs together nicely
    with st.form("match_entry_form"):
        form_data = []
        for Speler in squad:
            c1, c2, c3, c4, c5, c6 = st.columns([3, 3, 3, 3, 3, 3])
            with c1:
                st.write(f"**{Speler['Speler']}** ({Speler['Position']})")
            with c2:
                starter = st.selectbox("Basis?", ["Ja", "Nee"], key=f"start_{Speler['Speler']}")
            with c3:
                mins = st.number_input("Minuten gespeeld", min_value=0, max_value=120, value=0, key=f"min_{Speler['Speler']}")
            with c4:
                mins_aanwezig = st.number_input("Minuten aanwezig", min_value=0, key=f"minaanwezig_{Speler['Speler']}")
            with c5:
                goals = st.number_input("Goals", min_value=0,key=f"goals_{Speler['Speler']}" )
            with c6:
                assist = st.number_input("Assist", min_value=0,key=f"assist_{Speler['Speler']}" )

            form_data.append({
                "Date": str(match_date),
                "Opponent": opponent,
                "Competition": competition,
                "Speler": Speler["Speler"],
                "Position": Speler["Position"],
                "Starter": starter,
                "Minutes": mins,
                "mins_aanwezig": mins_aanwezig,
                "Goals": goals, 
                "Assist": assist,
            })

        # Submit Button inside the form
        submitted = st.form_submit_button("Data versturen", type="primary")

    # Save logic triggers only when button is clicked
    if submitted:
        df_existing = load_data()
        df_new = pd.DataFrame(form_data)
        
        # Filter out players who didn't play (0 minutes)
        df_new = df_new[df_new["Minutes"] > 0]
        
        if not df_new.empty:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            conn.update(data=df_combined)
            st.success(f"Successfully recorded data for match vs {opponent}!")
        else:
            st.warning("No player minutes were entered (all set to 0).")

# ==========================================
# TAB 2: DASHBOARD & ANALYTICS
# ==========================================
with tab_dashboard:
    st.header("📊 Squad Analytics")
    df = load_data()
    
    if df.empty:
        st.warning("No match data logged yet. Use the Data Entry tab to log your first match!")
    else:
        # Ensure numerical types
        df["Minutes"] = pd.to_numeric(df["Minutes"], errors="coerce").fillna(0)

        # High-level KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Matches Logged", df["Date"].nunique())
        kpi2.metric("Total Minutes Logged", int(df["Minutes"].sum()))
        kpi3.metric("Avg Minutes / Match", round(df.groupby("Date")["Minutes"].sum().mean(), 1))

        # Squad Summary Calculation
        summary = df.groupby(["Speler", "Position"]).agg(
            Matches_Played=("Minutes", lambda x: (x > 0).sum()),
            Starts=("Starter", lambda x: (x == "Yes").sum()),
            Sub_Apps=("Starter", lambda x: (x == "No").sum()),
            Total_Minutes=("Minutes", "sum"),
            Avg_Minutes=("Minutes", "mean")
        ).reset_index()

        st.subheader("Speler Summary Table")
        st.dataframe(summary.style.format({"Avg_Minutes": "{:.1f}"}), use_container_width=True)

        # Interactive Chart
        fig = px.bar(summary, x="Speler", y="Total_Minutes", color="Position", title="Total Minutes by Player")
        st.plotly_chart(fig, use_container_width=True)
