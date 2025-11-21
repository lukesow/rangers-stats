import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stSelectbox label, section[data-testid="stSidebar"] .stRadio label { color: white !important; }
    
    /* Metric Cards */
    div[data-testid="metric-container"] { 
        background-color: white; 
        border-left: 5px solid #d61a21; 
        padding: 15px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        border-radius: 5px; 
    }
    
    /* Headers */
    h1, h2, h3 { color: #1b458f; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    
    /* Dataframe Border */
    .stDataFrame { border: 1px solid #1b458f; }
    
    /* Random Button Styling */
    div.stButton > button:first-child {
        background-color: #d61a21;
        color: white;
        border: none;
        font-weight: bold;
        width: 100%;
    }
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
        
        # 1. Create Date Object
        # Assumes columns Day, Month, Year exist
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], errors='coerce')
        
        # 2. Result Code (W/D/L)
        df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        
        # 3. Fix Score (Force String) to prevent Date Auto-formatting
        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)

        # 4. Clean Player Names (R1 to R22)
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
                
        return df.sort_values('Date', ascending=False)
        
    except FileNotFoundError:
        return "FILE_NOT_FOUND"
    except Exception as e:
        return str(e)

# Load Data
data_response = load_data()
if isinstance(data_response, str):
    if data_response == "FILE_NOT_FOUND":
        st.error("⚠️ File not found! Ensure 'rangers_data.csv' is in the repository.")
    else:
        st.error(f"⚠️ Error reading CSV: {data_response}")
    st.stop()
else:
    df = data_response

# ==========================================
# 3. ANALYTICS ENGINE
# ==========================================

@st.cache_data
def get_player_summary(df):
    """Pre-calculates stats for sorting logic."""
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    players = [p for p in all_p if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    
    summary_list = []
    for p in players:
        mask = df[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
        p_games = df[mask]
        total = len(p_games)
        if total > 0:
            wins = len(p_games[p_games['ResultCode'] == 'W'])
            win_rate = (wins / total) * 100
            summary_list.append({'Player': p, 'Total': total, 'WinRate': win_rate})
            
    return pd.DataFrame(summary_list)

def get_player_stats(player_name, df):
    """Calculates detailed stats for a single player."""
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
        'df': player_matches,
        'starts': starts,
        'subs': subs,
        'total': total,
        'record': {'W': wins, 'D': draws, 'L': losses},
        'win_rate': win_rate,
        'last_5': last_5
    }

def get_h2h_chem(p1, p2, df):
    """Calculates stats for games where BOTH players started."""
    starter_cols = [f'R{i}' for i in range(1, 12)]
    
    # Filter for games where P1 started
    p1_starts = df[df[starter_cols].isin([p1]).any(axis=1)]
    
    if p1_starts.empty:
        return 0, 0
        
    # Filter that subset for games where P2 ALSO started
    both_starts = p1_starts[p1_starts[starter_cols].isin([p2]).any(axis=1)]
    
    games_together = len(both_starts)
    if games_together == 0:
        return 0, 0
        
    wins = len(both_starts[both_starts['ResultCode'] == 'W'])
    win_rate = (wins / games_together) * 100
    return games_together, win_rate

# ==========================================
# 4. SIDEBAR CONTROLS
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=100)
st.sidebar.title("IBROX ANALYTICS")

# --- MODE SELECTION ---
mode = st.sidebar.radio("Select Mode", ["Single Player", "Head-to-Head"], index=0)
st.sidebar.markdown("---")

# --- PLAYER DATA PREP ---
summary_df = get_player_summary(df)

# --- FILTERS (Apply to both modes) ---
seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True)
selected_season = st.sidebar.selectbox("Season", seasons)

comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist())
selected_comp = st.sidebar.selectbox("Competition", comps)

# Apply Filters to DF
df_filtered = df.copy()
if selected_season != 'All Time':
    df_filtered = df_filtered[df_filtered['Tag Season'] == selected_season]
if selected_comp != 'All Competitions':
    df_filtered = df_filtered[df_filtered['Competition'] == selected_comp]

# ==========================================
# 5. SINGLE PLAYER MODE
# ==========================================
if mode == "Single Player":
    
    # --- SORTING LOGIC ---
    sort_option = st.sidebar.selectbox(
        "Sort List By:",
        ["A-Z (Alphabetical)", "Most Appearances", "Highest Win %"]
    )

    if sort_option == "A-Z (Alphabetical)":
        sorted_players = sorted(summary_df['Player'].tolist())
    elif sort_option == "Most Appearances":
        sorted_players = summary_df.sort_values('Total', ascending=False)['Player'].tolist()
    else: # Highest Win %
        # Filter to 5+ games to avoid 1-game wonders
        qual = summary_df[summary_df['Total'] >= 5]
        sorted_players = qual.sort_values('WinRate', ascending=False)['Player'].tolist()

    # --- SESSION STATE (Random Button) ---
    if 'selected_player_name' not in st.session_state:
        st.session_state['selected_player_name'] = sorted_players[0]

    # If list changes (e.g. filter change), ensure selection is valid
    if st.session_state['selected_player_name'] not in sorted_players:
        st.session_state['selected_player_name'] = sorted_players[0]

    if st.sidebar.button("🔀 Pick Random Player"):
        st.session_state['selected_player_name'] = random.choice(sorted_players)

    def update_player():
        st.session_state['selected_player_name'] = st.session_state.player_selectbox

    selected_player = st.sidebar.selectbox(
        "Select Player",
        options=sorted_players,
        key='player_selectbox',
        index=sorted_players.index(st.session_state['selected_player_name']),
        on_change=update_player
    )

    # --- DISPLAY ---
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
        st.warning("No data for this player in current filters.")

# ==========================================
# 6. HEAD-TO-HEAD MODE
# ==========================================
else:
    # Basic A-Z sort for H2H selectors
    sorted_players_h2h = sorted(summary_df['Player'].tolist())
    
    st.sidebar.header("Select Players")
    p1 = st.sidebar.selectbox("Player 1", sorted_players_h2h, index=0)
    # Default P2 to someone else
    p2_index = 1 if len(sorted_players_h2h) > 1 else 0
    p2 = st.sidebar.selectbox("Player 2", sorted_players_h2h, index=p2_index)

    if p1 == p2:
        st.error("Please select two different players.")
    else:
        # Get Stats
        s1 = get_player_stats(p1, df_filtered)
        s2 = get_player_stats(p2, df_filtered)
        
        st.title("⚔️ HEAD-TO-HEAD")
        st.markdown(f"**{p1}** vs **{p2}**")

        if s1 and s2:
            # --- TOP LEVEL METRICS ---
            col1, col2 = st.columns(2)
            
            # Helper to render metrics with comparison
            def render_h2h_col(col, name, stats, opp_stats):
                with col:
                    st.subheader(name)
                    # Win Rate Delta
                    delta_val = stats['win_rate'] - opp_stats['win_rate']
                    st.metric("Win Rate", f"{stats['win_rate']:.1f}%", f"{delta_val:.1f}%")
                    
                    # Apps Delta
                    app_delta = stats['total'] - opp_stats['total']
                    st.metric("Total Apps", stats['total'], f"{app_delta}")
                    
                    # Starts Delta
                    start_delta = stats['starts'] - opp_stats['starts']
                    st.metric("Starts", stats['starts'], f"{start_delta}")

            render_h2h_col(col1, p1, s1, s2)
            render_h2h_col(col2, p2, s2, s1)

            st.markdown("---")
            
            # --- COMPARISON CHART ---
            st.subheader("Comparison Chart")
            
            comp_data = [
                {'Player': p1, 'Metric': 'Starts', 'Value': s1['starts']},
                {'Player': p2, 'Metric': 'Starts', 'Value': s2['starts']},
                {'Player': p1, 'Metric': 'Sub Apps', 'Value': s1['subs']},
                {'Player': p2, 'Metric': 'Sub Apps', 'Value': s2['subs']},
                {'Player': p1, 'Metric': 'Wins', 'Value': s1['record']['W']},
                {'Player': p2, 'Metric': 'Wins', 'Value': s2['record']['W']},
            ]
            comp_df = pd.DataFrame(comp_data)
            
            fig_comp = px.bar(comp_df, x='Metric', y='Value', color='Player', barmode='group',
                              color_discrete_map={p1: '#1b458f', p2: '#d61a21'})
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # --- CHEMISTRY ---
            st.markdown("---")
            st.subheader(f"🔗 Chemistry: {p1} & {p2}")
            
            games_together, win_rate_together = get_h2h_chem(p1, p2, df_filtered)
            
            c_chem1, c_chem2 = st.columns(2)
            c_chem1.metric("Games Started Together", games_together)
            if games_together > 0:
                c_chem2.metric("Win Rate as Duo", f"{win_rate_together:.1f}%")
            else:
                c_chem2.info("These players have never started a game together in this selection.")
                
        else:
            st.warning("Insufficient data for one or both players in this filter selection.")
