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
tab_entry, tab_dashboard = st.tabs(["📝 Data Entry Form", "📊 Dashboard"])

# Default Squad Roster
squad = [
    {"Speler": "Alex Morgan", "Position": "FW"},
    {"Speler": "Marcus Rashford", "Position": "FW"},
    {"Speler": "Kevin De Bruyne", "Position": "MF"},
    {"Speler": "Jude Bellingham", "Position": "MF"},
    {"Speler": "Declan Rice", "Position": "MF"},
    {"Speler": "Virgil van Dijk", "Position": "DF"},
    {"Speler": "Willia Saliba", "Position": "DF"},
    {"Speler": "William Salib", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    {"Speler": "William Sliba", "Position": "DF"},
    
]

# ==========================================
# TAB 1: DATA ENTRY FORM
# ==========================================
with tab_entry:
    st.header("FlevoBoys data log")
    
    # Match Metadata Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        match_date = st.date_input("Wedstrijd datum")
    with col2:
        opponent = st.text_input("Tegenstander", value="SCE 5")
    with col3:
        competition = st.selectbox("Competitie", ["Beker", "Competitie", "Vriendschappelijk"])

    st.subheader("Lineup & Minutes")
    
    # Use st.form to group inputs together nicely
    with st.form("match_entry_form"):
        form_data = []
        for Speler in squad:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 4])
            with c1:
                st.write(f"**{Speler['Speler']}** ({Speler['Position']})")
            with c2:
                starter = st.selectbox("Starter?", ["Yes", "No"], key=f"start_{Speler['Speler']}")
            with c3:
                mins = st.number_input("Minutes", min_value=0, max_value=120, value=0, key=f"min_{Speler['Speler']}")
            with c4:
                notes = st.text_input("Notes", key=f"note_{Speler['Speler']}")
            
            form_data.append({
                "Date": str(match_date),
                "Opponent": opponent,
                "Competition": competition,
                "Speler": Speler["Speler"],
                "Position": Speler["Position"],
                "Starter": starter,
                "Minutes": mins,
                "Notes": notes
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
