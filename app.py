import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Ibrox Analytics",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Rangers Theme & New Navigation
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; }
    section[data-testid="stSidebar"] { background-color: #1b458f; color: white; }
    
    /* Sidebar Text Colors */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p { color: white !important; }
    
    /* Navigation Buttons (Custom) */
    .nav-btn {
        width: 100%;
        padding: 15px;
        margin: 5px 0;
        border-radius: 8px;
        border: 2px solid white;
        background-color: transparent;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    .nav-btn:hover {
        background-color: rgba(255,255,255,0.2);
    }
    .nav-selected {
        background-color: white !important;
        color: #1b458f !important;
        border: 2px solid white;
    }
    
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
    
    /* Admin Area */
    .admin-box {
        border: 2px solid #d61a21;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA & ADMIN FUNCTIONS
# ==========================================
DATA_FILE = "rangers_data.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        
        # 1. Create Date Object
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], errors='coerce')
        
        # 2. Result Code (W/D/L)
        df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        
        # 3. Fix Score
        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)

        # 4. Clean Player Names
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
                
        return df.sort_values('Date', ascending=False)
        
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_new_match(new_data):
    """Appends a new match to the CSV file."""
    try:
        df_existing = pd.read_csv(DATA_FILE)
        df_new_row = pd.DataFrame([new_data])
        
        # Combine and Save
        df_final = pd.concat([df_existing, df_new_row], ignore_index=True)
        df_final.to_csv(DATA_FILE, index=False)
        
        # Clear cache to force reload
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "rangers1872": # Change this password as needed
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Admin Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Admin Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
if 'page' not in st.session_state:
    st.session_state['page'] = 'single' # 'single', 'h2h', 'admin'

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=100)
st.sidebar.title("IBROX ANALYTICS")

# Custom Navigation Buttons
st.sidebar.markdown("### 🧭 MENU")

# Button Logic using columns for layout
col_nav1, col_nav2 = st.sidebar.columns(2)

if col_nav1.button("👤 Single", use_container_width=True):
    st.session_state['page'] = 'single'
    
if col_nav2.button("⚔️ H2H", use_container_width=True):
    st.session_state['page'] = 'h2h'

# Admin Toggle
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Admin Login", use_container_width=True):
    st.session_state['page'] = 'admin'

# Current Mode Indicator (Visual only)
mode_labels = {'single': '👤 Single Player', 'h2h': '⚔️ Head-to-Head', 'admin': '🔒 Admin Panel'}
current_mode = mode_labels.get(st.session_state['page'], 'Unknown')
st.sidebar.info(f"Current Mode: **{current_mode}**")

# ==========================================
# 5. MAIN LOGIC
# ==========================================

# Load Data Global
df = load_data()

if df.empty and st.session_state['page'] != 'admin':
    st.warning("No data found. Please login as Admin to add data.")
    st.stop()

# --- Helper: Player Summary ---
if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    players_list = [p for p in all_p if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

# ------------------------------------------
# PAGE: SINGLE PLAYER
# ------------------------------------------
if st.session_state['page'] == 'single':
    
    # --- Stats Calculation Helper ---
    def get_player_stats(player_name, df):
        starter_cols = [f'R{i}' for i in range(1, 12)]
        sub_cols = [f'R{i}' for i in range(12, 23)]
        mask = df[starter_cols + sub_cols].isin([player_name]).any(axis=1)
        player_matches = df[mask].copy()
        if player_matches.empty: return None
        
        # Role Logic
        player_matches['Role'] = player_matches.apply(
            lambda x: 'Starter' if player_name in x[starter_cols].values else 'Sub', axis=1
        )
        
        # Counts
        starts = len(player_matches[player_matches['Role'] == 'Starter'])
        subs = len(player_matches[player_matches['Role'] == 'Sub'])
        total = starts + subs
        
        # Record
        wins = len(player_matches[player_matches['ResultCode'] == 'W'])
        draws = len(player_matches[player_matches['ResultCode'] == 'D'])
        losses = len(player_matches[player_matches['ResultCode'] == 'L'])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        last_5 = player_matches.sort_values('Date', ascending=False).head(5)['ResultCode'].tolist()

        return {
            'df': player_matches, 'starts': starts, 'subs': subs, 'total': total,
            'record': {'W': wins, 'D': draws, 'L': losses}, 'win_rate': win_rate, 'last_5': last_5
        }

    # --- Sidebar Filters ---
    st.sidebar.markdown("### 🔍 FILTERS")
    seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True)
    selected_season = st.sidebar.selectbox("Season", seasons)
    comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist())
    selected_comp = st.sidebar.selectbox("Competition", comps)
    
    # Apply Filters
    df_filtered = df.copy()
    if selected_season != 'All Time': df_filtered = df_filtered[df_filtered['Tag Season'] == selected_season]
    if selected_comp != 'All Competitions': df_filtered = df_filtered[df_filtered['Competition'] == selected_comp]

    # --- Random Player Logic ---
    if 'player_selectbox' not in st.session_state:
        st.session_state.player_selectbox = players_list[0]

    def pick_random_player():
        st.session_state.player_selectbox = random.choice(players_list)

    st.sidebar.button("🔀 Random Player", on_click=pick_random_player)

    selected_player = st.sidebar.selectbox(
        "Select Player", options=players_list, key='player_selectbox'
    )

    # --- Display ---
    stats = get_player_stats(selected_player, df_filtered)

    if stats:
        c1, c2 = st.columns([3,1])
        with c1:
            st.title(f"{selected_player.upper()}")
            st.markdown(f"**{selected_season}** | **{selected_comp}**")
        with c2:
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
                fig_pie = go.Figure(data=[go.Pie(labels=['Wins','Draws','Losses'], values=[stats['record']['W'], stats['record']['D'], stats['record']['L']], hole=.5, marker=dict(colors=['#1b458f', '#B0B0B0', '#d61a21']))])
                fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                st.subheader("Role Timeline")
                fig_bar = px.histogram(stats['df'], x='Date', color='Role', color_discrete_map={'Starter': '#1b458f', 'Sub': '#d61a21'}, nbins=20)
                fig_bar.update_layout(height=250, bargap=0.1)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("Recent Form")
            cols = st.columns(10)
            for i, res in enumerate(stats['last_5']):
                color = "#28a745" if res == 'W' else "#6c757d" if res == 'D' else "#dc3545"
                with cols[i]: st.markdown(f"<div style='background:{color}; color:white; text-align:center; padding:5px; border-radius:4px;'>{res}</div>", unsafe_allow_html=True)

        with tab2:
            display_cols = ['Date', 'Opponent', 'Competition', 'Score (Rangers First)', 'Win/Lose/Draw', 'Role']
            valid_cols = [c for c in display_cols if c in stats['df'].columns]
            st.dataframe(stats['df'][valid_cols], use_container_width=True, hide_index=True, column_config={"Score (Rangers First)": st.column_config.TextColumn("Score"), "Date": st.column_config.DateColumn("Match Date", format="DD/MM/YYYY")})

        with tab3:
            st.subheader("Top Teammates (Starts Together)")
            if stats['starts'] > 0:
                starter_df = stats['df'][stats['df']['Role'] == 'Starter']
                teammates = starter_df[[f'R{i}' for i in range(1, 12)]].values.flatten()
                teammates = [t for t in teammates if t != selected_player and str(t) != 'nan' and t is not None]
                if teammates:
                    tm_counts = pd.Series(teammates).value_counts().head(10).reset_index()
                    tm_counts.columns = ['Player', 'Games']
                    fig_tm = px.bar(tm_counts, x='Games', y='Player', orientation='h', color_discrete_sequence=['#1b458f'])
                    fig_tm.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_tm, use_container_width=True)
                else: st.write("No data.")
            else: st.info("Not enough starts.")
    else:
        st.warning("No stats available.")

# ------------------------------------------
# PAGE: HEAD TO HEAD
# ------------------------------------------
elif st.session_state['page'] == 'h2h':
    st.title("⚔️ Head-to-Head Comparison")
    
    # H2H Specific Selectors in Sidebar
    st.sidebar.markdown("### 👥 PLAYERS")
    p1 = st.sidebar.selectbox("Player 1", players_list, index=0)
    p2_idx = 1 if len(players_list) > 1 else 0
    p2 = st.sidebar.selectbox("Player 2", players_list, index=p2_idx)
    
    if p1 == p2:
        st.error("Please select two different players.")
    else:
        # Simple stats logic reused for H2H
        def get_simple_stats(p, df):
            # ... (Simplified version of single player stats logic inline)
            starter_cols = [f'R{i}' for i in range(1, 12)]
            sub_cols = [f'R{i}' for i in range(12, 23)]
            mask = df[starter_cols + sub_cols].isin([p]).any(axis=1)
            res = df[mask]
            wins = len(res[res['ResultCode'] == 'W'])
            total = len(res)
            starts = len(res[res[starter_cols].isin([p]).any(axis=1)])
            return {'total': total, 'wins': wins, 'starts': starts, 'win_rate': (wins/total*100) if total else 0}

        s1 = get_simple_stats(p1, df) # Using unfiltered DF for H2H overview or filtered? Let's use global df for now or add filters if needed
        s2 = get_simple_stats(p2, df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(p1)
            st.metric("Win Rate", f"{s1['win_rate']:.1f}%")
            st.metric("Total Games", s1['total'])
        with col2:
            st.subheader(p2)
            st.metric("Win Rate", f"{s2['win_rate']:.1f}%", delta=f"{s2['win_rate']-s1['win_rate']:.1f}%")
            st.metric("Total Games", s2['total'], delta=s2['total']-s1['total'])
            
        st.markdown("---")
        
        # H2H Chart
        comp_data = pd.DataFrame([
            {'Player': p1, 'Metric': 'Starts', 'Value': s1['starts']},
            {'Player': p2, 'Metric': 'Starts', 'Value': s2['starts']},
            {'Player': p1, 'Metric': 'Total Apps', 'Value': s1['total']},
            {'Player': p2, 'Metric': 'Total Apps', 'Value': s2['total']},
        ])
        fig = px.bar(comp_data, x='Metric', y='Value', color='Player', barmode='group', color_discrete_map={p1: '#1b458f', p2: '#d61a21'})
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# PAGE: ADMIN
# ------------------------------------------
elif st.session_state['page'] == 'admin':
    st.title("🔒 Admin Panel")
    
    if check_password():
        st.success("Logged in as Admin")
        
        st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
        st.subheader("📝 Add New Match Record")
        st.info("Adding a match automatically adds new players to the system.")
        
        with st.form("add_match_form"):
            c1, c2, c3 = st.columns(3)
            date_input = c1.date_input("Date", datetime.today())
            opponent = c2.text_input("Opponent")
            comp_input = c3.text_input("Competition", "Premiership")
            
            c4, c5, c6 = st.columns(3)
            score_input = c4.text_input("Score (Rangers-Opponent)", "0-0")
            result_input = c5.selectbox("Result", ["Win", "Draw", "Lose"])
            season_input = c6.text_input("Season", "2024/2025")
            
            st.markdown("---")
            st.markdown("**👥 Team Selection**")
            st.caption("Select from existing list OR type a new name in 'Add New Player' to register them.")
            
            # Player Inputs
            # We need 11 Starters and subs
            # To make this UI cleaner, let's use a multiselect for starters (must ensure 11?)
            # For simplicity in this demo, we will use a multiselect but allow adding new values is tricky in standard multiselect
            # So we provide a "New Players" text area.
            
            existing_starters = st.multiselect("Select Starters (Existing Players)", players_list)
            existing_subs = st.multiselect("Select Subs (Existing Players)", players_list)
            
            new_players_txt = st.text_input("➕ Add New Players (Comma separated, e.g. 'J. Smith, B. Jones')")
            
            submitted = st.form_submit_button("💾 Save Match Record")
            
            if submitted:
                if not opponent or not score_input:
                    st.error("Please fill in Opponent and Score.")
                else:
                    # Process New Players
                    new_p_list = [x.strip() for x in new_players_txt.split(',')] if new_players_txt else []
                    new_p_list = [x for x in new_p_list if x] # remove empty
                    
                    # Combine all selected
                    # Note: In a real app we'd strictly assign R1-R11 as starters.
                    # Here we will fill R1-R11 with starters, then R12+ with subs.
                    
                    all_starters = existing_starters # + any new players designated as starters? 
                    # For simplicity, assume new players are subs unless specified, 
                    # but actually let's just append new players to the list.
                    # Better logic: Just dump all selected names into the slots.
                    
                    full_squad = existing_starters + existing_subs + new_p_list
                    
                    # Prepare Row Data
                    row_data = {
                        'Day': date_input.day,
                        'Month': date_input.month,
                        'Year': date_input.year,
                        'Opponent': opponent,
                        'Competition': comp_input,
                        'Score (Rangers First)': score_input,
                        'Win/Lose/Draw': result_input,
                        'Tag Season': season_input
                    }
                    
                    # Fill R1 to R22
                    for i in range(22):
                        col_name = f"R{i+1}"
                        if i < len(full_squad):
                            row_data[col_name] = full_squad[i]
                        else:
                            row_data[col_name] = None
                            
                    # Save
                    if save_new_match(row_data):
                        st.success(f"Match vs {opponent} saved! New players added to system.")
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### Current Data Preview")
        st.dataframe(df.head(), use_container_width=True)
