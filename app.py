import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import base64
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
lion_svg_path = "M45.5 10.2c-1.3.6-3.1 2.4-3.1 3.1 0 .2.4.6.9.8 1.1.5 1.3 1.8.3 2.4-1.8 1.1-1.1 3.3.9 2.8 1.3-.3 2.2.4 1.8 1.5-.3.8-.2 1.3.4 1.3.5 0 1.1.9 1.3 2 .4 2.2 2.9 2.6 3.3.6.2-1.1.9-1.8 1.8-1.8 1.3 0 1.5.4.9 1.8-.9 1.8-.2 2.2 2.9 1.5 2.4-.5 2.6-.5 3.5.7.6.7 1.5 1.1 2.4.9 2.4-.5 3.5 1.3 1.3 2.2-1.3.5-1.1 1.5.4 1.5 1.3 0 2.2.7 2.2 1.8 0 1.5-.7 1.8-2.6 1.1-2.9-1.1-3.3-1.1-3.3.2 0 .7-1.3 2.2-2.9 3.3-3.1 2.2-3.1 2.4-1.3 4.6.9 1.1 1.3 2.4.9 2.9-.9 1.1-1.1 3.5-.2 3.5.4 0 .7.9.7 2 0 1.5.7 2 2.9 2 2.4 0 2.9.4 2.9 2.6 0 1.5-.4 2.4-1.3 2.4-1.5 0-1.5.2 0 1.8 2.2 2.2 1.5 3.7-1.8 3.7-2.2 0-2.4.2-1.1 1.3 2.6 2.4 2.6 2.4 0 1.1-1.3-.7-2.6-.5-2.9.4-.4 1.8-.2 2.9.4 2.4 2.4 1.8 3.7-1.5 3.5-1.5-.1-2.4-.7-2.4-1.5 0-.7-.7-1.1-1.8-1.1-1.5 0-2-.7-1.8-2.6.2-1.5-.2-2.6-.9-2.6-.7 0-1.3-.7-1.3-1.5 0-1.3-.9-1.5-4.4-1.3-4.4.2-4.6.2-3.3-1.1 1.8-1.8 1.3-2.4-2.2-2.4-3.1 0-3.5.2-3.1 1.5.4 1.1.2 1.8-.7 1.8-1.3 0-1.5.7-1.1 2.4.5 2.2.5 2.6-.2 2.6-.5 0-1.5.9-2.2 2-.7 1.1-1.3 1.8-1.3 1.5 0-.2.7-1.1 1.5-2 .9-1.1 1.5-2.2 1.5-2.6 0-.4-.9-1.3-2-2-2.2-1.3-2-1.5 1.1-1.5 1.8 0 3.3-.4 3.3-.9 0-.5-.9-2-2-3.3-1.8-2.2-1.8-2.4.2-2.4 1.3 0 2.4-.7 2.4-1.5 0-.9.7-1.5 1.5-1.5.9 0 1.5-.7 1.5-1.5 0-1.1-.9-1.5-2.6-1.3-2.4.2-3.1-.2-3.1-1.5 0-1.1-1.3-2.6-3.1-3.7-3.5-2.2-5.7-2-5.7.6 0 .7-.7 1.3-1.5 1.3-.9 0-2-.7-2.6-1.5-.7-1.1-1.1-1.1-1.5-.2-.4.7-1.5.9-2.6.4-1.8-.7-1.8-.9.2-1.1 1.5-.2 2.6-.2 2.6.2 0 .4-.9 1.5-2 2.4-1.5 1.3-2 1.3-2 0 0-1.1.9-2.2 2.2-2.6 1.1-.4 2-.4 2 0 0 .4.7.4 1.5 0 .9-.4 1.3-.4 1.1 0-.2.4-.4 1.8-.4 3.1 0 1.3.4 2.4.9 2.4.4 0 .7-.4.7-.9 0-.4-1.1-1.5-2.4-2.4-2-1.3-2.2-1.8-1.3-2.2.7-.4.9-.9.7-1.3-.4-.7 1.5-2.6 2.6-2.6.9 0 1.1-.4.7-.9-.7-.9 0-1.5 1.5-1.5 1.3 0 1.5-.2.9-.9-.4-.4-.2-1.1.4-1.5.7-.4.9-1.3.4-2z"
lion_svg = f"<svg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'><path d='{lion_svg_path}' fill='#ffffff' opacity='0.08'/></svg>"
lion_b64 = base64.b64encode(lion_svg.encode('utf-8')).decode("utf-8")
sidebar_bg_img = f"url(\"data:image/svg+xml;base64,{lion_b64}\")"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f4f4; color: #333333; }}
    section[data-testid="stSidebar"] {{ background-color: #1b458f; background-image: {sidebar_bg_img}; background-repeat: repeat; background-size: 60px 60px; }}
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

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], errors='coerce')
        df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
        return df.sort_values('Date', ascending=False)
    except:
        return pd.DataFrame()

def save_data(df_to_save):
    try:
        cols_drop = ['DateStr', 'Date', 'ResultCode']
        df_c = df_to_save.drop(columns=[c for c in cols_drop if c in df_to_save.columns])
        df_c.to_csv(DATA_FILE, index=False)
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
        st.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=60)
    with col_txt:
        st.markdown("<h3 style='margin:0; padding-top:10px;'>IBROX<br>ANALYTICS</h3>", unsafe_allow_html=True)

st.sidebar.markdown("---")

nav_options = ["Dashboard", "Head-to-Head", "Admin Panel"]
icons = ["📊", "⚔️", "🔒"]
nav_labels = [f"{icon}  {opt}" for icon, opt in zip(icons, nav_options)]
selected_nav = st.sidebar.radio("Main Menu", nav_labels, label_visibility="collapsed")
page_map = {nav_labels[0]: 'single', nav_labels[1]: 'h2h', nav_labels[2]: 'admin'}
st.session_state['page'] = page_map[selected_nav]

df = load_data()
players_list = []
if 'temp_new_players' not in st.session_state: st.session_state['temp_new_players'] = []

if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

df_f = df.copy()
s_sea = 'All Time'
s_comp = 'All Competitions'

if st.session_state['page'] != 'admin':
    st.sidebar.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    st.sidebar.caption("GLOBAL FILTERS")
    seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True) if not df.empty else []
    s_sea = st.sidebar.selectbox("Season", seasons)
    comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist()) if not df.empty else []
    s_comp = st.sidebar.selectbox("Competition", comps)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    if s_sea != 'All Time': df_f = df_f[df_f['Tag Season'] == s_sea]
    if s_comp != 'All Competitions': df_f = df_f[df_f['Competition'] == s_comp]

# ==========================================
# 4. MAIN AREA CONTENT
# ==========================================

# --- SINGLE PLAYER DASHBOARD ---
if st.session_state['page'] == 'single':
    if not players_list:
        st.info("👋 Welcome! The database is empty. Go to the **Admin Panel** to add data.")
    else:
        # --- CONTROL BAR ---
        st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
        c_search, c_rand = st.columns([3, 1])
        
        with c_search:
            if 'ps' not in st.session_state: st.session_state.ps = players_list[0]
            sel_p = st.selectbox("Search Player", players_list, key='ps', label_visibility="collapsed")
            
        with c_rand:
            def pick_rand(): st.session_state.ps = random.choice(players_list)
            st.button("🔀 Random Player", on_click=pick_rand, use_container_width=True)
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
            
            # PARTNERSHIP CALCULATION (For header summary)
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
                    # Filter for meaningful partnerships (>5 games) unless none exist
                    meaningful = tm_stats[tm_stats['Apps'] >= 5]
                    if meaningful.empty: meaningful = tm_stats
                    
                    # Get Best (Highest Win Rate, then Most Apps)
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

            # --- TAB 2: PERFORMANCE (NEW) ---
            with tab2:
                col_trend, col_comp = st.columns(2)
                
                with col_trend:
                    st.markdown("##### 📈 Performance Timeline")
                    # Group by Season
                    p_df['IsWin'] = p_df['ResultCode'] == 'W'
                    season_stats = p_df.groupby('Tag Season').agg(
                        Games=('ResultCode', 'count'),
                        Wins=('IsWin', 'sum')
                    ).reset_index()
                    season_stats['Win Rate'] = (season_stats['Wins'] / season_stats['Games']) * 100
                    # Sort by Season (assuming standard format YYYY/YY, simple sort works roughly, or use Date min)
                    # Better: Sort by 'Games' count or explicit Season order if known? Let's use alphabetical for now as 2024/25 > 2023/24
                    season_stats = season_stats.sort_values('Tag Season') 
                    
                    fig_trend = px.line(season_stats, x='Tag Season', y='Win Rate', markers=True, 
                                        title="Win Rate % per Season",
                                        color_discrete_sequence=['#1b458f'])
                    fig_trend.update_layout(yaxis_range=[0, 100], height=350)
                    st.plotly_chart(fig_trend, use_container_width=True)

                with col_comp:
                    st.markdown("##### 🏆 By Competition")
                    comp_stats = p_df.groupby('Competition').agg(
                        Games=('ResultCode', 'count'),
                        Wins=('IsWin', 'sum')
                    ).reset_index()
                    comp_stats['Win Rate'] = (comp_stats['Wins'] / comp_stats['Games']) * 100
                    comp_stats = comp_stats.sort_values('Win Rate', ascending=True)
                    
                    fig_comp = px.bar(comp_stats, x='Win Rate', y='Competition', orientation='h', 
                                      text='Games', title="Win Rate (Total Games)",
                                      color_discrete_sequence=['#d61a21'])
                    fig_comp.update_traces(texttemplate='%{text} games', textposition='inside')
                    fig_comp.update_layout(xaxis_range=[0, 100], height=350)
                    st.plotly_chart(fig_comp, use_container_width=True)

            # --- TAB 3: MATCH LOG ---
            with tab3:
                cols = ['Date', 'Opponent', 'Competition', 'Score (Rangers First)', 'Win/Lose/Draw', 'Role']
                v_cols = [c for c in cols if c in p_df.columns]
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
                # We calculated meaningful stats above for the summary, let's re-display the full table here
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
                else:
                    st.info("No data available.")

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

        def h2h_rand_p1(): st.session_state.h2h_p1 = random.choice(players_list)
        def h2h_rand_p2(): st.session_state.h2h_p2 = random.choice(players_list)
        def h2h_rand_teammate():
            p1_current = st.session_state.h2h_p1
            mask = df_f[[f'R{i}' for i in range(1, 23)]].isin([p1_current]).any(axis=1)
            games = df_f[mask]
            if not games.empty:
                all_p = games[[f'R{i}' for i in range(1, 23)]].values.ravel()
                mates = [p for p in all_p if pd.notna(p) and p != p1_current and str(p) != 'nan']
                mates = list(set(mates))
                if mates: st.session_state.h2h_p2 = random.choice(mates)
                else: st.toast("No teammates found.")
            else: st.toast("Player has no matches.")

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
            
            ex_opps = sorted(df['Opponent'].unique().tolist()) if not df.empty else []
            ex_comps = sorted(df['Competition'].unique().tolist()) if not df.empty else []
            ex_seas = sorted(df['Tag Season'].unique().tolist()) if not df.empty else []
            
            c1, c2, c3 = st.columns(3)
            inp_date = c1.date_input("Date", datetime.today())
            
            opp_sel = c2.selectbox("Opponent", ["Select..."] + ex_opps + ["➕ Add New"])
            inp_opp = c2.text_input("New Opponent Name") if opp_sel == "➕ Add New" else (opp_sel if opp_sel != "Select..." else "")
            
            comp_sel = c3.selectbox("Competition", ["Select..."] + ex_comps + ["➕ Add New"])
            inp_comp = c3.text_input("New Competition Name") if comp_sel == "➕ Add New" else (comp_sel if comp_sel != "Select..." else "")

            c4, c5, c6 = st.columns(3)
            inp_score = c4.text_input("Score (Rangers-Opp)", placeholder="e.g. 3-1")
            inp_res = c5.selectbox("Result", ["Win", "Draw", "Lose"])
            sea_sel = c6.selectbox("Season", ["Select..."] + ex_seas + ["➕ Add New"])
            inp_sea = c6.text_input("New Season (e.g. 25/26)") if sea_sel == "➕ Add New" else (sea_sel if sea_sel != "Select..." else "")
            
            st.markdown("---")
            with st.expander("🆕 Register New Player (If not in list)"):
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
                for i in range(1, 12):
                    selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, key=f"r{i}")
            with sc2:
                st.caption("Subs (12-22)")
                for i in range(12, 23):
                    selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, key=f"r{i}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Save Match", type="primary", use_container_width=True):
                if not inp_opp or not inp_score or not inp_comp or not inp_sea:
                    st.error("Please fill in all Match Details (Opponent, Score, Comp, Season).")
                else:
                    row = {
                        'Day': inp_date.day, 'Month': inp_date.month, 'Year': inp_date.year,
                        'Opponent': inp_opp, 'Competition': inp_comp, 
                        'Score (Rangers First)': inp_score, 'Win/Lose/Draw': inp_res, 'Tag Season': inp_sea
                    }
                    for k,v in selections.items(): row[k] = v if v else None
                    
                    df_cur = pd.read_csv(DATA_FILE)
                    df_final = pd.concat([df_cur, pd.DataFrame([row])], ignore_index=True)
                    if save_data(df_final):
                        st.success("Match Saved!")
                        st.session_state['temp_new_players'] = []
            st.markdown("</div>", unsafe_allow_html=True)

        # EDIT FIXTURE
        with tab_edit:
            st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
            if not df.empty:
                df['Label'] = df['Date'].dt.strftime('%Y-%m-%d') + " vs " + df['Opponent']
                target = st.selectbox("Select Match to Edit", df['Label'].unique())
                if target:
                    orig = df[df['Label'] == target].iloc[0]
                    ed1, ed2 = st.columns(2)
                    new_d = ed1.date_input("Correct Date", orig['Date'])
                    new_o = ed2.text_input("Correct Opponent", orig['Opponent'])
                    
                    if st.button("Update Info"):
                        raw = pd.read_csv(DATA_FILE)
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
