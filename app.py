import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
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

# --- ASSETS ---
RANGERS_CREST_URL = "https://i-p.rmcdn.net/64f5b85fe6a06b0052c2bc23/4535847/image-fa9870a3-f7d2-4499-b21c-f56c8b56f5d6.png?e=webp&nll=true"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f4f4; color: #333333; }}
    
    /* SIDEBAR - SOLID BLUE */
    section[data-testid="stSidebar"] {{ 
        background-color: #1b458f; 
        color: white;
    }}
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] .stMarkdown {{ color: #ffffff !important; }}
    
    /* MENU STYLING */
    div[role="radiogroup"] > label > div:first-child {{ display: None; }}
    div[role="radiogroup"] label {{ padding: 12px 16px; border-radius: 6px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); transition: all 0.2s ease-in-out; color: white !important; }}
    div[role="radiogroup"] label:hover {{ background: rgba(255, 255, 255, 0.15); border-color: white; cursor: pointer; }}
    div[role="radiogroup"] label[data-baseweb="radio"] {{ background: #ffffff !important; color: #1b458f !important; border-color: #ffffff; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    div[role="radiogroup"] label[data-baseweb="radio"] p {{ color: #1b458f !important; }}

    /* HEADERS & CARDS */
    .main .block-container h1, .main .block-container h2, .main .block-container h3 {{ color: #1b458f; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }}
    div[data-testid="metric-container"] {{ background-color: white; color: #333; border-left: 5px solid #d61a21; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
    div[data-testid="metric-container"] label {{ color: #666 !important; }} 
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: #1b458f !important; }}

    /* GLASSMORPHISM & MISC */
    .filter-box {{ background: rgba(0, 0, 0, 0.25); border-radius: 8px; padding: 15px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.15); }}
    .admin-footer {{ position: fixed; bottom: 20px; width: 100%; font-size: 0.9rem; }}
    .control-bar {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eee; }}
    
    /* HIGHLIGHT BOX */
    .highlight-box {{ background-color: #e3f2fd; border-left: 5px solid #1b458f; padding: 15px; border-radius: 5px; color: #0d47a1; font-weight: 500; margin-bottom: 1rem; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOGIC
# ==========================================
DATA_FILE = "rangers_data.csv"

def read_csv_safe(filepath):
    try:
        return pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding='cp1252')

@st.cache_data
def load_data():
    # Return a tuple: (DataFrame, ErrorMessage)
    try:
        df = read_csv_safe(DATA_FILE)
        
        # 1. STRIP HEADERS
        df.columns = df.columns.str.strip()
        
        # 2. SAFE DATE HANDLING
        # Verify columns exist before processing
        req_cols = ['Day', 'Month', 'Year']
        missing = [c for c in req_cols if c not in df.columns]
        if missing:
            return pd.DataFrame(), f"Missing required date columns: {', '.join(missing)}. Please ensure your CSV headers are correct."

        for c in req_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
        
        # Filter invalid dates
        valid_dates = (df['Day'] > 0) & (df['Month'] > 0) & (df['Year'] > 0)
        df = df[valid_dates].copy()
        
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], format="%d-%m-%Y", errors='coerce')

        # 3. CLEAN RESULTS
        if 'Win/Lose/Draw' in df.columns:
            df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        else: df['ResultCode'] = '?' 

        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)
            
        # 4. CLEAN PLAYERS (R1...R22)
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
        
        return df.sort_values('Date', ascending=False), None
        
    except FileNotFoundError:
        return pd.DataFrame(), f"File '{DATA_FILE}' not found. Please ensure the CSV is uploaded."
    except Exception as e:
        return pd.DataFrame(), str(e)

def save_data(df_to_save):
    try:
        # Define the exact columns to save based on the user's latest structure request
        standard_cols = ['Title', 'Opponent', 'Competition', 'Venue', 'Home/Away/Neutral', 
                         'Day', 'Month', 'Year', 'Tag Season', 'Score (Rangers First)', 
                         'Win/Lose/Draw', 'Referee:', 'Crowd', 'Manager']
        player_cols = [f'R{i}' for i in range(1, 23)]
        all_save_cols = standard_cols + player_cols

        # Filter the DataFrame to only include these columns
        df_c = df_to_save.copy()
        
        # Only keep columns that are in the save list AND present in the current dataframe
        df_final = df_c[[col for col in all_save_cols if col in df_c.columns]].copy()
        
        # We ensure all defined save columns exist by adding them if missing (with None/NaN)
        for col in all_save_cols:
            if col not in df_final.columns:
                df_final[col] = None 

        # Reorder to guarantee the user-defined CSV structure
        df_final = df_final[all_save_cols]
        
        df_final.to_csv(DATA_FILE, index=False)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def check_password():
    if "admin_password" not in st.secrets:
        st.error("🚨 Secrets config missing.")
        return False
    def password_entered():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect")
        return False
    return True

# ==========================================
# 3. LAYOUT & NAVIGATION
# ==========================================
with st.sidebar.container():
    col_logo, col_txt = st.sidebar.columns([1, 3])
    with col_logo:
        st.image(RANGERS_CREST_URL, width=60)
    with col_txt:
        st.markdown("<h3 style='margin:0; padding-top:10px;'>IBROX<br>ANALYTICS</h3>", unsafe_allow_html=True)

st.sidebar.markdown("---")

nav_options = ["Dashboard", "Head-to-Head", "Admin Panel"]
icons = ["📊", "⚔️", "🔒"]
nav_labels = [f"{icon}  {opt}" for icon, opt in zip(icons, nav_options)]
selected_nav = st.sidebar.radio("Main Menu", nav_labels, label_visibility="collapsed")
page_map = {nav_labels[0]: 'single', nav_labels[1]: 'h2h', nav_labels[2]: 'admin'}
st.session_state['page'] = page_map[selected_nav]

df, load_error = load_data()
players_list = []
if 'temp_new_players' not in st.session_state: st.session_state['temp_new_players'] = []

if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

df_f = df.copy()
s_sea, s_comp = 'All Time', 'All Competitions'

if st.session_state['page'] != 'admin':
    if not df.empty and 'Tag Season' in df.columns and 'Competition' in df.columns:
        st.sidebar.markdown("<div class='filter-box'>", unsafe_allow_html=True)
        st.sidebar.caption("GLOBAL FILTERS")
        
        seasons = ['All Time'] + sorted(df['Tag Season'].dropna().unique().tolist(), reverse=True)
        s_sea = st.sidebar.selectbox("Season", seasons)
        
        comps = ['All Competitions'] + sorted(df['Competition'].dropna().unique().tolist())
        s_comp = st.sidebar.selectbox("Competition", comps)
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        if s_sea != 'All Time': 
            df_f = df_f[df_f['Tag Season'] == s_sea]
        if s_comp != 'All Competitions': 
            df_f = df_f[df_f['Competition'] == s_comp]
    else:
        if df.empty:
            st.sidebar.warning("Data not loaded.")

# ==========================================
# 4. MAIN AREA CONTENT
# ==========================================

# --- SINGLE PLAYER DASHBOARD ---
if st.session_state['page'] == 'single':
    if not players_list:
        st.info("👋 Welcome! The database is empty.")
        # NEW: Display load error immediately if it exists
        if load_error:
            with st.expander("Database Load Error Details"):
                st.error(f"Error encountered while loading data: {load_error}")
                st.caption("Please check your `rangers_data.csv` file. Common errors include missing the file itself, or missing date columns ('Day', 'Month', 'Year').")
    else:
        # --- CONTROL BAR ---
        st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
        c_search, c_rand = st.columns([3, 1])
        
        with c_search:
            if 'ps' not in st.session_state: st.session_state.ps = players_list[0]
            sel_p = st.selectbox("Search Player", players_list, key='ps', label_visibility="collapsed")
            
        with c_rand:
            def pick_rand(): 
                pool = [p for p in players_list if p != st.session_state.ps]
                if pool: st.session_state.ps = random.choice(pool)
            st.button("🔀 Random", on_click=pick_rand, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- STATS CALC ---
        starter_cols = [f'R{i}' for i in range(1, 12)]
        sub_cols = [f'R{i}' for i in range(12, 23)]
        mask = df_f[starter_cols + sub_cols].isin([sel_p]).any(axis=1)
        p_df = df_f[mask].copy()

        if not p_df.empty:
            p_df['Role'] = p_df.apply(lambda x: 'Starter' if sel_p in x[starter_cols].values else 'Sub', axis=1)
            starts = len(p_df[p_df['Role'] == 'Starter'])
            subs = len(p_df[p_df['Role'] == 'Sub'])
            wins = len(p_df[p_df['ResultCode'] == 'W'])
            total = starts + subs
            win_rate = (wins/total*100) if total else 0
            
            # PARTNERSHIP CALCULATION
            best_partner_txt = "No partnership data yet"
            if starts > 0:
                start_games = p_df[p_df['Role'] == 'Starter']
                teammate_data = []
                for idx, row in start_games.iterrows():
                    res = row['ResultCode']
                    team_in_match = row[[f'R{i}' for i in range(1, 12)]].values
                    for mate in team_in_match:
                        if mate and str(mate) != 'nan' and mate != sel_p:
                            teammate_data.append({'Teammate': mate, 'Result': res})
                
                if teammate_data:
                    tm_df = pd.DataFrame(teammate_data)
                    tm_stats = tm_df.groupby('Teammate').agg(Apps=('Result', 'count'), Wins=('Result', lambda x: (x == 'W').sum())).reset_index()
                    tm_stats['WinRate'] = tm_stats['Wins'] / tm_stats['Apps'] * 100
                    meaningful = tm_stats[tm_stats['Apps'] >= 5]
                    if meaningful.empty: meaningful = tm_stats
                    
                    if not meaningful.empty:
                        best = meaningful.sort_values(['WinRate', 'Apps'], ascending=[False, False]).iloc[0]
                        best_partner_txt = f"{best['Teammate']} ({best['Apps']} gms, {best['WinRate']:.1f}% win rate)"

            # --- HEADER & SUMMARY ---
            col_head_L, col_head_R = st.columns([3, 1])
            with col_head_L:
                st.markdown(f"<h1>{sel_p.upper()}</h1>", unsafe_allow_html=True)
                st.caption(f"Analyzing: {s_sea} • {s_comp}")
                st.markdown(f"<div class='highlight-box'>🤝 Best Partnership: <b>{best_partner_txt}</b></div>", unsafe_allow_html=True)
            with col_head_R:
                if win_rate > 70: t, c = "🔥 ON FIRE", "#d61a21"
                elif total > 100: t, c = "🏆 LEGEND", "#FFD700"
                else: t, c = "⚡ SQUAD", "#1b458f"
                st.markdown(f"<div style='text-align:center; padding:8px; background:{c}; color:white; font-weight:bold; border-radius:6px; margin-top:15px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>{t}</div>", unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Apps", total)
            m2.metric("Starts", starts)
            m3.metric("Sub Apps", subs)
            m4.metric("Win Rate", f"{win_rate:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏆 Performance", "📜 Match Log", "🤝 Connections"])

            # --- TAB 1: OVERVIEW ---
            with tab1:
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown("##### Overall Record")
                    fig = go.Figure(data=[go.Pie(labels=['Wins','Draws','Losses'], values=[wins, len(p_df[p_df['ResultCode']=='D']), len(p_df[p_df['ResultCode']=='L'])], hole=.6, marker=dict(colors=['#1b458f','#e0e0e0','#d61a21']))])
                    fig.update_layout(height=300, margin=dict(t=0,b=0,l=0,r=0), showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.markdown("##### Role Timeline")
                    fig2 = px.histogram(p_df, x='Date', color='Role', color_discrete_map={'Starter':'#1b458f','Sub':'#d61a21'}, nbins=20)
                    fig2.update_layout(height=300, bargap=0.2, margin=dict(t=20,b=0,l=0,r=0))
                    st.plotly_chart(fig2, use_container_width=True)

            # --- TAB 2: PERFORMANCE ---
            with tab2:
                col_trend, col_comp = st.columns(2)
                
                with col_trend:
                    st.markdown("##### 📈 Performance Timeline")
                    if 'Tag Season' in p_df.columns:
                        p_df['IsWin'] = p_df['ResultCode'] == 'W'
                        season_stats = p_df.groupby('Tag Season').agg(Games=('ResultCode', 'count'), Wins=('IsWin', 'sum')).reset_index()
                        season_stats['Win Rate'] = (season_stats['Wins'] / season_stats['Games']) * 100
                        season_stats = season_stats.sort_values('Tag Season') 
                        fig_trend = px.line(season_stats, x='Tag Season', y='Win Rate', markers=True, color_discrete_sequence=['#1b458f'])
                        fig_trend.update_layout(yaxis_range=[0, 100], height=350)
                        st.plotly_chart(fig_trend, use_container_width=True)
                    else: st.warning("No Season Data")

                with col_comp:
                    st.markdown("##### 🏆 By Competition")
                    if 'Competition' in p_df.columns:
                        p_df['IsWin'] = p_df['ResultCode'] == 'W'
                        comp_stats = p_df.groupby('Competition').agg(Games=('ResultCode', 'count'), Wins=('IsWin', 'sum')).reset_index()
                        comp_stats['Win Rate'] = (comp_stats['Wins'] / comp_stats['Games']) * 100
                        comp_stats = comp_stats.sort_values('Win Rate', ascending=True)
                        fig_comp = px.bar(comp_stats, x='Win Rate', y='Competition', orientation='h', text='Games', color_discrete_sequence=['#d61a21'])
                        fig_comp.update_traces(texttemplate='%{text} games', textposition='inside')
                        fig_comp.update_layout(xaxis_range=[0, 100], height=350)
                        st.plotly_chart(fig_comp, use_container_width=True)
                    else: st.warning("No Competition Data")

            # --- TAB 3: MATCH LOG ---
            with tab3:
                # Removed 'Round' from this list
                potential_cols = ['Date', 'Opponent', 'Competition', 'Venue', 'Home/Away/Neutral', 'Score (Rangers First)', 'Win/Lose/Draw', 'Manager', 'Role']
                v_cols = [c for c in potential_cols if c in p_df.columns]
                st.dataframe(
                    p_df[v_cols], 
                    use_container_width=True, 
                    hide_index=True, 
                    column_config={
                        "Score (Rangers First)": st.column_config.TextColumn("Score"),
                        "Date": st.column_config.DateColumn("Match Date", format="DD/MM/YYYY")
                    }
                )

            # --- TAB 4: CONNECTIONS ---
            with tab4:
                st.markdown("##### Partnership Ranking (Starts Together)")
                if starts > 0 and 'tm_stats' in locals():
                    st.dataframe(
                        tm_stats,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Teammate": st.column_config.TextColumn("Teammate", width="medium"),
                            "Apps": st.column_config.NumberColumn("Games Together", format="%d"),
                            "Wins": st.column_config.NumberColumn("Wins Together", format="%d"),
                            "WinRate": st.column_config.ProgressColumn("Chemistry (Win %)", format="%.1f%%", min_value=0, max_value=100)
                        }
                    )
                else: st.info("No data available.")
        else:
            st.warning(f"No data found for **{sel_p}** with current filters.")

# --- HEAD TO HEAD ---
elif st.session_state['page'] == 'h2h':
    st.markdown("<h1>⚔️ Head-to-Head</h1>", unsafe_allow_html=True)
    if len(players_list) < 2:
        st.warning("Need at least 2 players in the database to compare.")
    else:
        if 'h2h_p1' not in st.session_state: st.session_state.h2h_p1 = players_list[0]
        if 'h2h_p2' not in st.session_state: st.session_state.h2h_p2 = players_list[1] if len(players_list) > 1 else players_list[0]

        def h2h_rand_p1(): 
            current = st.session_state.h2h_p1
            pool = [p for p in players_list if p != current]
            if pool: st.session_state.h2h_p1 = random.choice(pool)
        
        def h2h_rand_p2(): 
            current = st.session_state.h2h_p2
            pool = [p for p in players_list if p != current and p != st.session_state.h2h_p1]
            if pool: st.session_state.h2h_p2 = random.choice(pool)

        def h2h_rand_teammate():
            p1_current = st.session_state.h2h_p1
            mask = df_f[[f'R{i}' for i in range(1, 23)]].isin([p1_current]).any(axis=1)
            games = df_f[mask]
            if not games.empty:
                all_p = games[[f'R{i}' for i in range(1, 23)]].values.ravel()
                cur_p2 = st.session_state.h2h_p2
                mates = [p for p in all_p if pd.notna(p) and p != p1_current and str(p) != 'nan' and p in players_list]
                mates = list(set(mates))
                available = [m for m in mates if m != cur_p2]
                
                if available:
                    st.session_state.h2h_p2 = random.choice(available)
                elif mates:
                    st.toast(f"Teammate already selected: {cur_p2}")
                else:
                    st.toast("No teammates found.")
            else:
                st.toast("Player has no matches.")

        st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            st.selectbox("Player 1", players_list, key='h2h_p1', label_visibility="collapsed")
            st.button("🔀 Random Player 1", on_click=h2h_rand_p1, use_container_width=True)
        with col_sel2:
            st.selectbox("Player 2", players_list, key='h2h_p2', label_visibility="collapsed")
            c_r1, c_r2 = st.columns(2)
            c_r1.button("🔀 Random P2", on_click=h2h_rand_p2, use_container_width=True)
            c_r2.button("🤝 Random Teammate", on_click=h2h_rand_teammate, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        p1 = st.session_state.h2h_p1
        p2 = st.session_state.h2h_p2

        if p1 == p2: st.error("Select different players.")
        else:
            def get_h2h_stats(p):
                msk = df_f[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
                d = df_f[msk]
                w = len(d[d['ResultCode']=='W'])
                starts = len(d[d[[f'R{i}' for i in range(1, 12)]].isin([p]).any(axis=1)])
                return {'Total': len(d), 'Wins': w, 'Starts': starts, 'Win Rate': (w/len(d)*100) if len(d) else 0}
            
            def get_partnership_chem(pA, pB):
                starters = [f'R{i}' for i in range(1, 12)]
                mask_A = df_f[starters].isin([pA]).any(axis=1)
                mask_B = df_f[starters].isin([pB]).any(axis=1)
                combined = df_f[mask_A & mask_B]
                total = len(combined)
                wins = len(combined[combined['ResultCode'] == 'W'])
                rate = (wins/total*100) if total > 0 else 0
                return total, rate

            s1 = get_h2h_stats(p1)
            s2 = get_h2h_stats(p2)
            chem_games, chem_rate = get_partnership_chem(p1, p2)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"### {p1}")
                st.metric("Win Rate", f"{s1['Win Rate']:.1f}%")
                st.metric("Total Apps", s1['Total'])
            with m3:
                st.markdown(f"### {p2}")
                st.metric("Win Rate", f"{s2['Win Rate']:.1f}%", delta=f"{s2['Win Rate']-s1['Win Rate']:.1f}%")
                st.metric("Total Apps", s2['Total'], delta=s2['Total']-s1['Total'])
            with m2:
                categories = ['Total Apps', 'Wins', 'Starts', 'Win Rate']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[s1['Total'], s1['Wins'], s1['Starts'], s1['Win Rate']], theta=categories, fill='toself', name=p1, line_color='#1b458f'))
                fig.add_trace(go.Scatterpolar(r=[s2['Total'], s2['Wins'], s2['Starts'], s2['Win Rate']], theta=categories, fill='toself', name=p2, line_color='#d61a21'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, height=250, margin=dict(t=20,b=20,l=20,r=20))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🔗 Partnership Analysis")
            c_chem1, c_chem2 = st.columns(2)
            c_chem1.metric("Games Started Together", chem_games)
            c_chem2.metric("Win Rate as Duo", f"{chem_rate:.1f}%")
            if chem_games > 0: st.progress(chem_rate / 100)
            else: st.caption("No games started together.")

# --- ADMIN PANEL ---
elif st.session_state['page'] == 'admin':
    st.markdown("<h1>🔒 Admin Panel</h1>", unsafe_allow_html=True)
    if check_password():
        st.success("Authenticated")
        
        tab_add, tab_edit = st.tabs(["➕ Add Match", "✏️ Edit Fixture"])
        
        # ADD MATCH
        with tab_add:
            st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
            st.subheader("New Match Record")
            
            if not df.empty:
                ex_opps = sorted(df['Opponent'].dropna().unique().tolist()) if 'Opponent' in df.columns else []
                ex_comps = sorted(df['Competition'].dropna().unique().tolist()) if 'Competition' in df.columns else []
                ex_seas = sorted(df['Tag Season'].dropna().unique().tolist()) if 'Tag Season' in df.columns else []
                ex_venues = sorted(df['Venue'].dropna().unique().tolist()) if 'Venue' in df.columns else []
                ex_managers = sorted(df['Manager'].dropna().unique().tolist()) if 'Manager' in df.columns else []
                ex_referees = sorted(df['Referee:'].dropna().unique().tolist()) if 'Referee:' in df.columns else []
            else:
                ex_opps, ex_comps, ex_seas, ex_venues, ex_managers, ex_referees = [], [], [], [], [], []
            
            c1, c2, c3 = st.columns(3)
            inp_date = c1.date_input("Date", datetime.today())
            
            opp_sel = c2.selectbox("Opponent", ["Select..."] + ex_opps + ["➕ Add New"])
            inp_opp = c2.text_input("New Opponent Name") if opp_sel == "➕ Add New" else (opp_sel if opp_sel != "Select..." else "")
            
            comp_sel = c3.selectbox("Competition", ["Select..."] + ex_comps + ["➕ Add New"])
            inp_comp = c3.text_input("New Competition Name") if comp_sel == "➕ Add New" else (comp_sel if comp_sel != "Select..." else "")

            # Re-balanced columns after removing 'Round'
            c4, c5 = st.columns(2)
            ven_sel = c4.selectbox("Venue", ["Select..."] + ex_venues + ["➕ Add New"])
            inp_venue = c4.text_input("New Venue") if ven_sel == "➕ Add New" else (ven_sel if ven_sel != "Select..." else "")
            inp_ha = c5.selectbox("Home/Away/Neutral", ["Home", "Away", "Neutral"])

            c7, c8, c9 = st.columns(3)
            ref_sel = c7.selectbox("Referee", ["Select..."] + ex_referees + ["➕ Add New"])
            inp_ref = c7.text_input("New Referee") if ref_sel == "➕ Add New" else (ref_sel if ref_sel != "Select..." else "")
            inp_crowd = c8.text_input("Crowd", placeholder="e.g. 50000")
            man_sel = c9.selectbox("Manager", ["Select..."] + ex_managers + ["➕ Add New"])
            inp_man = c9.text_input("New Manager") if man_sel == "➕ Add New" else (man_sel if man_sel != "Select..." else "")

            c10, c11, c12 = st.columns(3)
            inp_score = c10.text_input("Score (Rangers-Opp)", placeholder="e.g. 3-1")
            inp_res = c11.selectbox("Result", ["Win", "Draw", "Lose"])
            sea_sel = c12.selectbox("Season", ["Select..."] + ex_seas + ["➕ Add New"])
            inp_sea = c12.text_input("New Season (e.g. 25/26)") if sea_sel == "➕ Add New" else (sea_sel if sea_sel != "Select..." else "")
            
            st.markdown("---")
            with st.expander("🆕 Register New Player"):
                np_col1, np_col2 = st.columns([3,1])
                new_p = np_col1.text_input("Name", placeholder="e.g. J. Butland", label_visibility="collapsed")
                if np_col2.button("Add Player"):
                    if new_p and new_p not in players_list:
                        st.session_state['temp_new_players'].append(new_p)
                        st.rerun()
            
            st.markdown("##### Team Sheet")
            sc1, sc2 = st.columns(2)
            selections = {}
            with sc1:
                st.caption("Starters (1-11)")
                for i in range(1, 12): selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, key=f"r{i}")
            with sc2:
                st.caption("Subs (12-22)")
                for i in range(12, 23): selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, key=f"r{i}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Save Match", type="primary", use_container_width=True):
                if not inp_opp or not inp_score:
                    st.error("Missing Details")
                else:
                    row = {
                        'Title': f"{inp_opp} ({inp_ha[0]})", 'Opponent': inp_opp, 'Competition': inp_comp,
                        'Venue': inp_venue, 'Home/Away/Neutral': inp_ha,
                        'Day': inp_date.day, 'Month': inp_date.month, 'Year': inp_date.year,
                        'Tag Season': inp_sea, 'Score (Rangers First)': inp_score, 
                        'Win/Lose/Draw': inp_res, 'Referee:': inp_ref, 'Crowd': inp_crowd, 'Manager': inp_man
                    }
                    for k,v in selections.items(): row[k] = v if v else None
                    df_cur, _ = load_data()
                    df_final = pd.concat([df_cur, pd.DataFrame([row])], ignore_index=True)
                    if save_data(df_final):
                        st.success("Match Saved!")
                        st.session_state['temp_new_players'] = []
            st.markdown("</div>", unsafe_allow_html=True)

        # EDIT FIXTURE
        with tab_edit:
            st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
            if not df.empty:
                df['Label'] = df.apply(lambda x: f"{x['DateStr']} vs {x['Opponent']}", axis=1)
                target = st.selectbox("Select Match to Edit", df['Label'].unique())
                
                subset = df[df['Label'] == target]
                if not subset.empty:
                    orig = subset.iloc[0]
                    ed1, ed2 = st.columns(2)
                    new_d = ed1.date_input("Correct Date", orig['Date'])
                    new_o = ed2.text_input("Correct Opponent", orig['Opponent'])
                    if st.button("Update Info"):
                        raw, _ = load_data()
                        m = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                        if m.any():
                            idx = raw[m].index[0]
                            raw.at[idx, 'Day'] = new_d.day
                            raw.at[idx, 'Month'] = new_d.month
                            raw.at[idx, 'Year'] = new_d.year
                            raw.at[idx, 'Opponent'] = new_o
                            if save_data(raw): st.success("Updated.")
                        else: st.error("Record not found.")
            else: st.info("No matches.")
            st.markdown("</div>", unsafe_allow_html=True)
