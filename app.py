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

# --- ASSETS & BACKGROUND GENERATION ---
RANGERS_CREST_URL = "https://i-p.rmcdn.net/64f5b85fe6a06b0052c2bc23/4535847/image-fa9870a3-f7d2-4499-b21c-f56c8b56f5d6.png?e=webp&nll=true"

def generate_professional_bg_svg():
    """
    Generates a professional, subtle abstract pattern (Bokeh/Particles).
    Uses an ISOLATED random instance so it doesn't break the app's global random state.
    """
    # FIX: Use a local Random instance instead of global random.seed()
    rng = random.Random(55) 
    w, h = 400, 400 
    
    svg_elements = []
    for _ in range(40):
        cx = rng.randint(0, w)
        cy = rng.randint(0, h)
        r = rng.randint(2, 15)
        opacity = rng.uniform(0.03, 0.08)
        
        svg_elements.append(
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='white' opacity='{opacity}'/>"
        )
    
    svg_content = f"""
    <svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg'>
        {''.join(svg_elements)}
    </svg>
    """
    return base64.b64encode(svg_content.encode('utf-8')).decode("utf-8")

bg_b64 = generate_professional_bg_svg()
sidebar_bg_img = f"url(\"data:image/svg+xml;base64,{bg_b64}\")"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f4f4; color: #333333; }}
    section[data-testid="stSidebar"] {{ background-color: #1b458f; background-image: {sidebar_bg_img}; background-repeat: repeat; background-size: 400px 400px; }}
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
    try:
        df = read_csv_safe(DATA_FILE)
        df.columns = df.columns.str.strip() # Clean headers
        
        # Safe numeric conversion
        for c in ['Day', 'Month', 'Year']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
        
        # Create Date object
        if all(x in df.columns for x in ['Day', 'Month', 'Year']):
            # Filter out invalid dates (0/0/0) before conversion to avoid errors
            valid_dates = (df['Day'] > 0) & (df['Month'] > 0) & (df['Year'] > 0)
            df = df[valid_dates].copy()
            df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
            df['Date'] = pd.to_datetime(df['DateStr'], format="%d-%m-%Y", errors='coerce')
        else:
            st.error("CSV Missing Date Columns.")
            return pd.DataFrame()

        if 'Win/Lose/Draw' in df.columns:
            df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        else: df['ResultCode'] = '?'

        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)
            
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
        
        return df.sort_values('Date', ascending=False)
    except Exception as e:
        st.error(f"⚠️ Error loading CSV: {e}")
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
# 3. LAYOUT
# ==========================================
with st.sidebar.container():
    c1, c2 = st.sidebar.columns([1, 3])
    with c1: st.image(RANGERS_CREST_URL, width=60)
    with c2: st.markdown("<h3 style='margin:0; padding-top:10px;'>IBROX<br>ANALYTICS</h3>", unsafe_allow_html=True)

st.sidebar.markdown("---")

nav_labels = ["📊  Dashboard", "⚔️  Head-to-Head", "🔒  Admin Panel"]
sel_nav = st.sidebar.radio("Menu", nav_labels, label_visibility="collapsed")
page = 'single' if "Dashboard" in sel_nav else 'h2h' if "Head-to-Head" in sel_nav else 'admin'
st.session_state['page'] = page

df = load_data()
players_list = []
if 'temp_new_players' not in st.session_state: st.session_state['temp_new_players'] = []

if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

df_f = df.copy()
s_sea, s_comp = 'All Time', 'All Competitions'

if page != 'admin' and not df.empty:
    st.sidebar.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    st.sidebar.caption("GLOBAL FILTERS")
    seasons = ['All Time'] + sorted(df['Tag Season'].dropna().unique().tolist(), reverse=True)
    s_sea = st.sidebar.selectbox("Season", seasons)
    comps = ['All Competitions'] + sorted(df['Competition'].dropna().unique().tolist())
    s_comp = st.sidebar.selectbox("Competition", comps)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    if s_sea != 'All Time': df_f = df_f[df_f['Tag Season'] == s_sea]
    if s_comp != 'All Competitions': df_f = df_f[df_f['Competition'] == s_comp]

# ==========================================
# 4. PAGES
# ==========================================

if page == 'single':
    if not players_list: st.info("Database empty.")
    else:
        st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1:
            if 'ps' not in st.session_state: st.session_state.ps = players_list[0]
            sel_p = st.selectbox("Player", players_list, key='ps', label_visibility="collapsed")
        with c2:
            # FIX: Exclude current player to ensure change
            def pick_rand(): 
                pool = [p for p in players_list if p != st.session_state.ps]
                if pool: st.session_state.ps = random.choice(pool)
            st.button("🔀 Random", on_click=pick_rand, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
            
            best_ptn = "N/A"
            if starts > 0:
                s_games = p_df[p_df['Role'] == 'Starter']
                mates = []
                for _, r in s_games.iterrows():
                    team = r[[f'R{i}' for i in range(1, 12)]].values
                    res = r['ResultCode']
                    for m in team:
                        if m and str(m)!='nan' and m!=sel_p: mates.append({'P':m, 'R':res})
                if mates:
                    m_df = pd.DataFrame(mates)
                    stats = m_df.groupby('P').agg(Apps=('R','count'), Wins=('R', lambda x: (x=='W').sum())).reset_index()
                    stats['WR'] = stats['Wins']/stats['Apps']*100
                    sig = stats[stats['Apps']>=5]
                    if sig.empty: sig = stats
                    if not sig.empty:
                        best = sig.sort_values(['WR','Apps'], ascending=False).iloc[0]
                        best_ptn = f"{best['P']} ({best['Apps']} gms, {best['WR']:.1f}%)"

            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"<h1>{sel_p.upper()}</h1>", unsafe_allow_html=True)
                st.caption(f"{s_sea} • {s_comp}")
                st.markdown(f"<div class='highlight-box'>🤝 Best Partner: <b>{best_ptn}</b></div>", unsafe_allow_html=True)
            with c2:
                bg = "#d61a21" if win_rate > 70 else "#FFD700" if total > 100 else "#1b458f"
                lbl = "🔥 ON FIRE" if win_rate > 70 else "🏆 LEGEND" if total > 100 else "⚡ SQUAD"
                st.markdown(f"<div style='text-align:center; padding:10px; background:{bg}; color:white; font-weight:bold; border-radius:6px; margin-top:15px;'>{lbl}</div>", unsafe_allow_html=True)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Apps", total); k2.metric("Starts", starts); k3.metric("Subs", subs); k4.metric("Win %", f"{win_rate:.1f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            t1, t2, t3, t4 = st.tabs(["📊 Dash", "📈 Trends", "📜 Log", "🤝 Mates"])
            
            with t1:
                c_a, c_b = st.columns(2)
                with c_a:
                    fig = go.Figure(data=[go.Pie(labels=['W','D','L'], values=[wins, len(p_df[p_df['ResultCode']=='D']), len(p_df[p_df['ResultCode']=='L'])], hole=.6, marker=dict(colors=['#1b458f','#e0e0e0','#d61a21']))])
                    fig.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=0)); st.plotly_chart(fig, use_container_width=True)
                with c_b:
                    fig2 = px.histogram(p_df, x='Date', color='Role', color_discrete_map={'Starter':'#1b458f','Sub':'#d61a21'}, nbins=20)
                    fig2.update_layout(height=250, bargap=0.2, margin=dict(t=20,b=0,l=0,r=0)); st.plotly_chart(fig2, use_container_width=True)
            
            with t2:
                if 'Tag Season' in p_df.columns:
                    p_df['IsWin'] = p_df['ResultCode'] == 'W'
                    sea = p_df.groupby('Tag Season').agg(G=('ResultCode','count'), W=('IsWin','sum')).reset_index()
                    sea['WR'] = sea['W']/sea['G']*100
                    st.plotly_chart(px.line(sea, x='Tag Season', y='WR', markers=True, color_discrete_sequence=['#1b458f'], title="Win Rate by Season"), use_container_width=True)
                if 'Competition' in p_df.columns:
                    cmp = p_df.groupby('Competition').agg(G=('ResultCode','count'), W=('IsWin','sum')).reset_index()
                    cmp['WR'] = cmp['W']/cmp['G']*100
                    st.plotly_chart(px.bar(cmp, x='WR', y='Competition', orientation='h', color_discrete_sequence=['#d61a21'], title="Win Rate by Comp"), use_container_width=True)

            with t3:
                d_cols = ['Date', 'Opponent', 'Competition', 'Venue', 'Score (Rangers First)', 'Win/Lose/Draw', 'Role']
                st.dataframe(p_df[[c for c in d_cols if c in p_df.columns]], use_container_width=True, hide_index=True)

            with t4:
                if 'stats' in locals():
                    stats = stats.sort_values(['Apps', 'WR'], ascending=False)
                    st.dataframe(stats, use_container_width=True, hide_index=True, column_config={"WR": st.column_config.ProgressColumn("Win %", format="%.1f%%", min_value=0, max_value=100)})
                else: st.info("No data")
        else: st.warning("No matches found.")

elif page == 'h2h':
    st.markdown("<h1>⚔️ Head-to-Head</h1>", unsafe_allow_html=True)
    if len(players_list) < 2: st.warning("Need 2+ players")
    else:
        if 'h2h_p1' not in st.session_state: st.session_state.h2h_p1 = players_list[0]
        if 'h2h_p2' not in st.session_state: st.session_state.h2h_p2 = players_list[1] if len(players_list)>1 else players_list[0]

        def r1(): 
            pool = [p for p in players_list if p != st.session_state.h2h_p1]
            if pool: st.session_state.h2h_p1 = random.choice(pool)
        def r2(): 
            pool = [p for p in players_list if p != st.session_state.h2h_p2 and p != st.session_state.h2h_p1]
            if pool: st.session_state.h2h_p2 = random.choice(pool)
        def rt():
            p1 = st.session_state.h2h_p1
            msk = df_f[[f'R{i}' for i in range(1, 23)]].isin([p1]).any(axis=1)
            g = df_f[msk]
            if not g.empty:
                pool = g[[f'R{i}' for i in range(1, 23)]].values.ravel()
                # Exclude P1 and current P2
                cur_p2 = st.session_state.h2h_p2
                valid = [x for x in pool if pd.notna(x) and x!=p1 and str(x)!='nan' and x!=cur_p2]
                if valid: st.session_state.h2h_p2 = random.choice(list(set(valid)))
                else: st.toast("No other teammates found.")
            else: st.toast("No matches for P1.")

        st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Player 1", players_list, key='h2h_p1', label_visibility="collapsed")
            st.button("🔀 Random P1", on_click=r1, use_container_width=True)
        with c2:
            st.selectbox("Player 2", players_list, key='h2h_p2', label_visibility="collapsed")
            ca, cb = st.columns(2)
            ca.button("🔀 Random P2", on_click=r2, use_container_width=True)
            cb.button("🤝 Teammate", on_click=rt, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        p1, p2 = st.session_state.h2h_p1, st.session_state.h2h_p2
        if p1 == p2: st.error("Select different players")
        else:
            def get_stats(p):
                msk = df_f[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
                d = df_f[msk]
                w = len(d[d['ResultCode']=='W'])
                return {'T':len(d), 'W':w, 'WR':(w/len(d)*100) if len(d) else 0}
            
            s1, s2 = get_stats(p1), get_stats(p2)
            
            # Shared logic
            start_cols = [f'R{i}' for i in range(1, 12)]
            mA = df_f[start_cols].isin([p1]).any(axis=1)
            mB = df_f[start_cols].isin([p2]).any(axis=1)
            shared = df_f[mA & mB]
            chem_g = len(shared)
            chem_w = len(shared[shared['ResultCode']=='W'])
            chem_r = (chem_w/chem_g*100) if chem_g else 0

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"### {p1}"); c1.metric("Win Rate", f"{s1['WR']:.1f}%"); c1.metric("Apps", s1['T'])
            c3.markdown(f"### {p2}"); c3.metric("Win Rate", f"{s2['WR']:.1f}%", delta=f"{s2['WR']-s1['WR']:.1f}%"); c3.metric("Apps", s2['T'], delta=s2['T']-s1['T'])
            
            with c2:
                fig = go.Figure()
                cats = ['Apps', 'Wins', 'Win Rate'] # Simple Radar
                # Normalize for radar shape roughly (Win Rate is 0-100, Counts vary)
                # Just showing raw might be skewed, but fine for now
                fig.add_trace(go.Scatterpolar(r=[s1['T'], s1['W'], s1['WR']], theta=cats, fill='toself', name=p1, line_color='#1b458f'))
                fig.add_trace(go.Scatterpolar(r=[s2['T'], s2['W'], s2['WR']], theta=cats, fill='toself', name=p2, line_color='#d61a21'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, height=200, margin=dict(t=20,b=20,l=20,r=20))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🔗 Partnership (Starts)")
            ca, cb = st.columns(2)
            ca.metric("Games Together", chem_g)
            cb.metric("Duo Win Rate", f"{chem_r:.1f}%")
            if chem_g: st.progress(chem_r/100)
            else: st.caption("Never started together.")

elif page == 'admin':
    st.markdown("<h1>🔒 Admin Panel</h1>", unsafe_allow_html=True)
    if check_password():
        st.success("Ready")
        tab1, tab2 = st.tabs(["Add Match", "Edit Match"])
        
        with tab1:
            st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
            if not df.empty:
                ops = sorted(df['Opponent'].dropna().unique())
                cmps = sorted(df['Competition'].dropna().unique())
                seas = sorted(df['Tag Season'].dropna().unique())
            else: ops, cmps, seas = [], [], []
            
            c1, c2, c3 = st.columns(3)
            date = c1.date_input("Date")
            opp = c2.selectbox("Opponent", ["Select..."] + ops + ["Add New"])
            if opp=="Add New": opp = c2.text_input("New Opponent")
            elif opp=="Select...": opp=""
            
            cmp = c3.selectbox("Competition", ["Select..."] + cmps + ["Add New"])
            if cmp=="Add New": cmp = c3.text_input("New Comp")
            elif cmp=="Select...": cmp=""

            c4, c5, c6 = st.columns(3)
            scr = c4.text_input("Score")
            res = c5.selectbox("Result", ["Win","Draw","Lose"])
            sea = c6.selectbox("Season", ["Select..."] + seas + ["Add New"])
            if sea=="Add New": sea = c6.text_input("New Season")
            elif sea=="Select...": sea=""

            # Extra fields
            c7, c8, c9 = st.columns(3)
            rnd = c7.text_input("Round")
            ven = c8.text_input("Venue")
            ha = c9.selectbox("H/A", ["Home","Away","Neutral"])
            
            st.markdown("---")
            with st.expander("Add New Player"):
                n_pl = st.text_input("Name")
                if st.button("Add"): 
                    if n_pl: 
                        st.session_state.temp_new_players.append(n_pl)
                        st.rerun()

            st.markdown("##### Squad")
            c_s1, c_s2 = st.columns(2)
            sel = {}
            with c_s1:
                st.caption("Starters")
                for i in range(1,12): sel[f"R{i}"] = st.selectbox(f"R{i}", [""]+players_list, key=f"r{i}")
            with c_s2:
                st.caption("Subs")
                for i in range(12,23): sel[f"R{i}"] = st.selectbox(f"R{i}", [""]+players_list, key=f"r{i}")

            if st.button("Save Match", type="primary"):
                if not opp or not scr: st.error("Missing Info")
                else:
                    row = {'Day':date.day, 'Month':date.month, 'Year':date.year, 'Opponent':opp, 'Competition':cmp, 'Score (Rangers First)':scr, 'Win/Lose/Draw':res, 'Tag Season':sea, 'Round':rnd, 'Venue':ven, 'Home/Away/Neutral':ha}
                    for k,v in sel.items(): row[k] = v if v else None
                    df_cur = read_csv_safe(DATA_FILE)
                    df_new = pd.concat([df_cur, pd.DataFrame([row])], ignore_index=True)
                    if save_data(df_new): 
                        st.success("Saved")
                        st.session_state.temp_new_players = []
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='control-bar'>", unsafe_allow_html=True)
            if not df.empty:
                # FIX: Robust filtering for edit
                # Use a safer label
                df['Label'] = df.apply(lambda x: f"{x['DateStr']} vs {x['Opponent']}", axis=1)
                target = st.selectbox("Select Match", df['Label'].unique())
                
                # FIX: IndexError Safe Check
                subset = df[df['Label'] == target]
                if not subset.empty:
                    orig = subset.iloc[0]
                    e1, e2 = st.columns(2)
                    nd = e1.date_input("New Date", orig['Date'])
                    no = e2.text_input("New Opponent", orig['Opponent'])
                    
                    if st.button("Update"):
                        raw = read_csv_safe(DATA_FILE)
                        # Match logic
                        mask = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                        if mask.any():
                            idx = raw[mask].index[0]
                            raw.at[idx, 'Day'] = nd.day
                            raw.at[idx, 'Month'] = nd.month
                            raw.at[idx, 'Year'] = nd.year
                            raw.at[idx, 'Opponent'] = no
                            if save_data(raw): st.success("Updated")
                        else: st.error("Row not found in CSV")
                else:
                    st.error("Match details not found.")
            st.markdown("</div>", unsafe_allow_html=True)
