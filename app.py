import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random

# ==========================================
# 1. CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Ibrox Analytics",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Rangers Theme
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; }
    section[data-testid="stSidebar"] { background-color: #1b458f; color: white; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stSelectbox label, section[data-testid="stSidebar"] .stButton button { color: white !important; }
    /* Style the random button */
    div.stButton > button:first-child {
        background-color: #d61a21;
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    div[data-testid="metric-container"] { background-color: white; border-left: 5px solid #d61a21; padding: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); border-radius: 5px; }
    h1, h2, h3 { color: #1b458f; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .stDataFrame { border: 1px solid #1b458f; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADER
# ==========================================
@st.cache_data
def load_data():
    filename = "rangers_data.csv"
    try:
        df = pd.read_csv(filename)
        
        # 1. Create Date
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], errors='coerce')
        
        # 2. Result Code
        df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        
        # 3. Fix Score (Force String)
        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)

        # 4. Clean Player Names
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None)
                
        return df.sort_values('Date', ascending=False)
    except Exception as e:
        return str(e)

# Load Data
data_response = load_data()
if isinstance(data_response, str):
    st.error(f"⚠️ Error: {data_response}")
    st.stop()
df = data_response

# ==========================================
# 3. GLOBAL STATS PRE-CALC (For Sorting)
# ==========================================
@st.cache_data
def get_player_summary(df):
    # Get all unique players
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    players = [p for p in all_p if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    
    summary_list = []
    
    # Calculate basic stats for sorting
    # Note: We do a quick calc here just for the list sorting
    for p in players:
        mask = df[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
        p_games = df[mask]
        total = len(p_games)
        if total > 0:
            wins = len(p_games[p_games['ResultCode'] == 'W'])
            win_rate = (wins / total) * 100
            summary_list.append({'Player': p, 'Total': total, 'WinRate': win_rate})
            
    return pd.DataFrame(summary_list)

summary_df = get_player_summary(df)

# ==========================================
# 4. ANALYTICS ENGINE
# ==========================================
def get_player_stats(player_name, df):
    starter_cols = [f'R{i}' for i in range(1, 12)]
    sub_cols = [f'R{i}' for i in range(12, 23)]
    
    mask = df[starter_cols + sub_cols].isin([player_name]).any(axis=1)
    player_matches = df[mask].copy()
    
    if player_matches.empty:
        return None

    def get_role(row):
        if player_name in row[starter_cols].values: return 'Starter'
        return 'Sub'

    player_matches['Role'] = player_matches.apply(get_role, axis=1)
    
    starts = len(player_matches[player_matches['Role'] == 'Starter'])
    subs = len(player_matches[player_matches['Role'] == 'Sub'])
    total = starts + subs
    
    wins = len(player_matches[player_matches['ResultCode'] == 'W'])
    draws = len(player_matches[player_matches['ResultCode'] == 'D'])
    losses = len(player_matches[player_matches['ResultCode'] == 'L'])
    
    win_rate = (wins / total * 100) if total > 0 else 0
    last_5 = player_matches.sort_values('Date', ascending=False).head(5)['ResultCode'].tolist()

    return {
        'df': player_matches, 'starts': starts, 'subs': subs, 'total': total,
        'record': {'W': wins, 'D': draws, 'L': losses},
        'win_rate': win_rate, 'last_5': last_5
    }

# ==========================================
# 5. UI & SIDEBAR LOGIC
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=100)
st.sidebar.title("IBROX ANALYTICS")

# --- SORTING OPTIONS ---
sort_option = st.sidebar.selectbox(
    "Sort Players By:",
    ["A-Z (Alphabetical)", "Most Appearances", "Fewest Appearances", "Highest Win %", "Lowest Win %"]
)

# Apply Sorting to the List
if sort_option == "A-Z (Alphabetical)":
    sorted_players = sorted(summary_df['Player'].tolist())
elif sort_option == "Most Appearances":
    sorted_players = summary_df.sort_values('Total', ascending=False)['Player'].tolist()
elif sort_option == "Fewest Appearances":
    sorted_players = summary_df.sort_values('Total', ascending=True)['Player'].tolist()
elif sort_option == "Highest Win %":
    # Filter out players with very few games to avoid 100% win rate from 1 game skewing top results
    qualified = summary_df[summary_df['Total'] >= 5] 
    sorted_players = qualified.sort_values('WinRate', ascending=False)['Player'].tolist()
else: # Lowest Win %
    qualified = summary_df[summary_df['Total'] >= 5]
    sorted_players = qualified.sort_values('WinRate', ascending=True)['Player'].tolist()

# --- SESSION STATE HANDLING ---
# Initialize if not set
if 'selected_player_name' not in st.session_state:
    st.session_state['selected_player_name'] = sorted_players[0]

# Ensure the current selection is actually in the sorted list (handles switching lists)
if st.session_state['selected_player_name'] not in sorted_players:
    st.session_state['selected_player_name'] = sorted_players[0]

# Random Button
if st.sidebar.button("🔀 Pick Random Player"):
    random_player = random.choice(sorted_players)
    st.session_state['selected_player_name'] = random_player

# The Dropdown (Controlled by Session State)
def update_player():
    st.session_state['selected_player_name'] = st.session_state.player_selectbox

selected_player = st.sidebar.selectbox(
    "Select Player",
    options=sorted_players,
    key='player_selectbox', # Key binds it to session state
    index=sorted_players.index(st.session_state['selected_player_name']),
    on_change=update_player
)

st.sidebar.markdown("---")

# Filters
seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True)
selected_season = st.sidebar.selectbox("Season", seasons)

comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist())
selected_comp = st.sidebar.selectbox("Competition", comps)

# Apply Filters
df_filtered = df.copy()
if selected_season != 'All Time':
    df_filtered = df_filtered[df_filtered['Tag Season'] == selected_season]
if selected_comp != 'All Competitions':
    df_filtered = df_filtered[df_filtered['Competition'] == selected_comp]

# Display Stats
stats = get_player_stats(selected_player, df_filtered)

if stats and stats['total'] > 0:
    c1, c2 = st.columns([3,1])
    with c1:
        st.title(f"{selected_player.upper()}")
        st.markdown(f"**{selected_season}** | **{selected_comp}**")
    with c2:
        if stats['total'] > 0:
            if stats['win_rate'] > 70: text, color = "🔥 ON FIRE", "#d61a21"
            elif stats['total'] > 100: text, color = "🏆 LEGEND", "#FFD700"
            else: text, color = "⚡ SQUAD", "#1b458f"
            st.markdown(f"<div style='text-align:center; padding:10px; border:2px solid {color}; color:{color}; font-weight:bold; border-radius:8px;'>{text}</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Apps", stats['total'])
    m2.metric("Starts", stats['starts'])
    m3.metric("Bench", stats['subs'])
    m4.metric("Win Rate", f"{stats['win_rate']:.1f}%")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📜 Match History", "⚽ Teammates"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Win/Draw/Loss")
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Wins', 'Draws', 'Losses'],
                values=[stats['record']['W'], stats['record']['D'], stats['record']['L']],
                hole=.5,
                marker=dict(colors=['#1b458f', '#B0B0B0', '#d61a21'])
            )])
            fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            st.subheader("Timeline")
            fig_bar = px.histogram(stats['df'], x='Date', color='Role', 
                                   color_discrete_map={'Starter': '#1b458f', 'Sub': '#d61a21'},
                                   nbins=20)
            fig_bar.update_layout(height=250, bargap=0.1)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.subheader("Recent Form")
        cols = st.columns(10)
        for i, res in enumerate(stats['last_5']):
            color = "#28a745" if res == 'W' else "#6c757d" if res == 'D' else "#dc3545"
            with cols[i]:
                st.markdown(f"<div style='background:{color}; color:white; text-align:center; padding:5px; border-radius:4px;'>{res}</div>", unsafe_allow_html=True)

    with tab2:
        display_cols = ['Date', 'Opponent', 'Competition', 'Score (Rangers First)', 'Win/Lose/Draw', 'Role']
        valid_cols = [c for c in display_cols if c in stats['df'].columns]
        
        st.dataframe(
            stats['df'][valid_cols], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Score (Rangers First)": st.column_config.TextColumn("Score"),
                "Date": st.column_config.DateColumn("Match Date", format="DD/MM/YYYY")
            }
        )

    with tab3:
        st.subheader("Chemistry (Starts Together)")
        if stats['starts'] > 0:
            starter_df = stats['df'][stats['df']['Role'] == 'Starter']
            teammates = starter_df[[f'R{i}' for i in range(1, 12)]].values.flatten()
            teammates = [t for t in teammates if t != selected_player and str(t) != 'nan' and t is not None]
            
            if len(teammates) > 0:
                tm_counts = pd.Series(teammates).value_counts().head(10).reset_index()
                tm_counts.columns = ['Player', 'Games']
                fig_tm = px.bar(tm_counts, x='Games', y='Player', orientation='h', color_discrete_sequence=['#1b458f'])
                fig_tm.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_tm, use_container_width=True)
            else:
                st.write("No teammate data found.")
        else:
            st.info("Player hasn't started enough games to calculate chemistry.")

else:
    st.warning("No data found for this player in the selected filters.")
