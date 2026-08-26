import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

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
        return pd.DataFrame(columns=[
            "Date", "Opponent", "Competition", "Speler", "Position", 
            "Starter", "Minutes", "mins_aanwezig", "Goals", "Assist"
        ])

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
        
        # Added enumerate(squad) to ensure unique keys with _{i}
        for i, Speler in enumerate(squad):
            c1, c2, c3, c4, c5, c6 = st.columns([3, 3, 3, 3, 3, 3])
            with c1:
                st.write(f"**{Speler['Speler']}** ({Speler['Position']})")
            with c2:
                starter = st.selectbox("Basis?", ["Ja", "Nee"], key=f"start_{Speler['Speler']}_{i}")
            with c3:
                mins = st.number_input("Minuten gespeeld", min_value=0, max_value=120, value=0, key=f"min_{Speler['Speler']}_{i}")
            with c4:
                mins_aanwezig = st.number_input("Minuten aanwezig", min_value=0, value=0, key=f"minaanwezig_{Speler['Speler']}_{i}")
            with c5:
                goals = st.number_input("Goals", min_value=0, key=f"goals_{Speler['Speler']}_{i}")
            with c6:
                assist = st.number_input("Assist", min_value=0, key=f"assist_{Speler['Speler']}_{i}")

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
        
        # Filter out players who were not present (0 minutes present)
        df_new = df_new[df_new["mins_aanwezig"] > 0]
        
        if not df_new.empty:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            conn.update(data=df_combined)
            st.success(f"Successfully recorded data for match vs {opponent}!")
        else:
            st.warning("No player presence was entered (all set to 0).")

# ==========================================
# TAB 2: DASHBOARD & ANALYTICS
# ==========================================

#---------------------------------------------------
#Calc
#---------------------------------------------------
match_summary = df.groupby(["Date", "Opponent"]).agg(
    Goals_Voor=("Goals", "sum"),  # Or pull directly from your metadata log
    Goals_Tegen=("Goals_tegen", "first")
).reset_index()

# Determine outcome
def get_points(row):
    if row["Goals_Voor"] > row["Goals_Tegen"]:
        return 3  # Win
    elif row["Goals_Voor"] == row["Goals_Tegen"]:
        return 1  # Draw
    return 0     # Loss

match_summary["Points"] = match_summary.apply(get_points)
total_points = match_summary["Points"].sum()
total_wins = (match_summary["Points"] == 3).sum()
total_draws = (match_summary["Points"] == 1).sum()
total_losses = (match_summary["Points"] == 0).sum()



with tab_dashboard:
    st.header("Flevo Boys 8 - Data")
    df = load_data()
    
    if df.empty:
        st.warning("Nog geen wedstrijd data")
    else:
        # Ensure numerical types
        df["Minutes"] = pd.to_numeric(df["Minutes"], errors="coerce").fillna(0)
        df["mins_aanwezig"] = pd.to_numeric(df["mins_aanwezig"], errors="coerce").fillna(0)
        df["Goals"] = pd.to_numeric(df["Goals"], errors="coerce").fillna(0)
        df["Assist"] = pd.to_numeric(df["Assist"], errors="coerce").fillna(0)

        # High-level KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Matches Logged", df["Date"].nunique())
        kpi2.metric("Total Minutes Logged", int(df["Goals"].sum()))
        kpi3.metric("Avg Minutes / Match", round(df.groupby("Date")["Minutes"].sum().mean(), 1))

        # Fixed GroupBy Aggregation Syntax and matched 'Ja' / 'Nee' check
        summary = df.groupby(["Speler", "Position"]).agg(
            Matches_Played=("Minutes", lambda x: (x > 0).sum()),
            Starts=("Starter", lambda x: (x == "Ja").sum()),
            Sub_Apps=("Starter", lambda x: (x == "Nee").sum()),
            Total_Minutes=("Minutes", "sum"),
            Minuten_aanwezig=("mins_aanwezig", "sum"),
            Goals=("Goals", "sum"),
            Assists=("Assist", "sum"),
            Avg_Minutes=("Minutes", "mean"),
        ).reset_index()

        summary = summary.sort_values(by="Minuten_aanwezig", ascending=False)

        st.subheader("Team statistieken")
        col1 = st.columns(1)

        col1.metric(
            Label = "Totale punten",
            value=total_points,
            delta=f"{int(total_points)} punten"
        )

        st.subheader("Speel data")
        st.dataframe(
        summary.style.format({
        "Matches_Played": "{:.0f}",
        "Starts": "{:.0f}",
        "Sub_Apps": "{:.0f}",
        "Total_Minutes": "{:.0f}",
        "Minuten_aanwezig": "{:.0f}",
        "Goals": "{:.0f}",
        "Assists": "{:.0f}",
        "Avg_Minutes": "{:.1f}"  # Keeps 1 decimal for averages
    }), 
    use_container_width=True
    )
       # st.dataframe(summary.style.format({"Avg_Minutes": "{:.1f}", "Goals": "{:0.f}"}), use_container_width=True)

        # Interactive Overlay Bar Chart
        fig = go.Figure()
        
        # Background Bar: Total Minutes Present
        fig.add_trace(go.Bar(
            x=summary["Speler"],
            y=summary["Minuten_aanwezig"],
            name="Totale Aanwezigheid (Minuten)",
            marker_color="lightgray",
            opacity=0.6,
            width=0.6
        ))

        # Foreground Bar: Minutes Played
        fig.add_trace(go.Bar(
            x=summary["Speler"],
            y=summary["Total_Minutes"],
            name="Gespeelde minuten",
            marker_color="#2ca02c",
            width=0.4
        ))

        fig.update_layout(
            barmode="overlay",
            title="Speeltijd vs. aanwezigheid per speler",
            xaxis_title="Speler",
            yaxis_title="Minuten",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)