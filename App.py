import streamlit as st
import pandas as pd
import os
import plotly.express as px

# File paths for backend data storage
LOGS_FILE = "match_logs.csv"

# Load or initialize the hidden match database
def load_data():
    if os.path.exists(LOGS_FILE):
        return pd.read_csv(LOGS_FILE)
    return pd.DataFrame(columns=["Date", "Opponent", "Competition", "Player", "Position", "Starter", "Minutes", "Notes"])

def save_data(df):
    df.to_csv(LOGS_FILE, index=False)

# App Navigation
st.set_page_config(page_title="Squad Minutes Tracker", layout="wide")
tab_entry, tab_dashboard = st.tabs(["📝 Data Entry Form", "📊 Dashboard"])

# Default Squad Roster
squad = [
    {"Player": "Alex Morgan", "Position": "FW"},
    {"Player": "Marcus Rashford", "Position": "FW"},
    {"Player": "Kevin De Bruyne", "Position": "MF"},
    {"Player": "Jude Bellingham", "Position": "MF"},
    {"Player": "Declan Rice", "Position": "MF"},
    {"Player": "Virgil van Dijk", "Position": "DF"},
    {"Player": "William Saliba", "Position": "DF"},
]

# ==========================================
# TAB 1: DATA ENTRY FORM
# ==========================================
with tab_entry:
    st.header("⚽ Match Minutes Entry Form")
    
    # 1. Match Metadata Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        match_date = st.date_input("Match Date")
    with col2:
        opponent = st.text_input("Opponent", value="FC Rival")
    with col3:
        competition = st.selectbox("Competition", ["League", "Cup", "Friendly"])

    st.subheader("Lineup & Minutes")
    
    # 2. Interactive Squad Input Form
    form_data = []
    for player in squad:
        c1, c2, c3, c4 = st.columns([3, 2, 2, 4])
        with c1:
            st.write(f"**{player['Player']}** ({player['Position']})")
        with c2:
            starter = st.selectbox("Starter?", ["Yes", "No"], key=f"start_{player['Player']}")
        with c3:
            mins = st.number_input("Minutes", min_value=0, max_value=120, value=0, key=f"min_{player['Player']}")
        with c4:
            notes = st.text_input("Notes", key=f"note_{player['Player']}")
        
        form_data.append({
            "Date": match_date,
            "Opponent": opponent,
            "Competition": competition,
            "Player": player["Player"],
            "Position": player["Position"],
            "Starter": starter,
            "Minutes": mins,
            "Notes": notes
        })

    # 3. Save Button
    if st.button("🚀 Submit Match Minutes", type="primary"):
        df_existing = load_data()
        df_new = pd.DataFrame(form_data)
        # Filter out players who didn't play (0 minutes)
        df_new = df_new[df_new["Minutes"] > 0]
        
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        save_data(df_combined)
        st.success(f"Successfully recorded data for match vs {opponent}!")

# ==========================================
# TAB 2: DASHBOARD & ANALYTICS
# ==========================================
with tab_dashboard:
    st.header("📊 Squad Analytics")
    df = load_data()
    
    if df.empty:
        st.warning("No match data logged yet. Use the Data Entry tab to log your first match!")
    else:
        # High-level KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Matches Logged", df["Date"].nunique())
        kpi2.metric("Total Minutes Logged", df["Minutes"].sum())
        kpi3.metric("Avg Minutes / Match", round(df.groupby("Date")["Minutes"].sum().mean(), 1))

        # Squad Summary Calculation
        summary = df.groupby(["Player", "Position"]).agg(
            Matches_Played=("Minutes", lambda x: (x > 0).sum()),
            Starts=("Starter", lambda x: (x == "Yes").sum()),
            Sub_Apps=("Starter", lambda x: (x == "No").sum()),
            Total_Minutes=("Minutes", "sum"),
            Avg_Minutes=("Minutes", "mean")
        ).reset_index()

        st.subheader("Player Summary Table")
        st.dataframe(summary.style.format({"Avg_Minutes": "{:.1f}"}), use_container_width=True)

        # Interactive Chart
        fig = px.bar(summary, x="Player", y="Total_Minutes", color="Position", title="Total Minutes by Player")
        st.plotly_chart(fig, use_container_width=True)