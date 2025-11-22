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

# --- LION RAMPANT BACKGROUND SVG ---
# Changed fill to a subtle light blue (#add8e6) with very low opacity
lion_svg = """
<svg width='80' height='80' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'>
<path d='M30,70 Q40,60 35,50 Q45,40 40,30 Q50,20 60,30 Q70,20 80,30 Q70,50 60,60 Q70,70 60,80 Q50,90 40,80 Q30,90 20,80 Q30,70 30,70 Z' 
      fill='#add8e6' opacity='0.05'/>
</svg>
"""
lion_b64 = base64.b64encode(lion_svg.encode('utf-8')).decode("utf-8")
sidebar_bg_img = f"url(\"data:image/svg+xml;base64,{lion_b64}\")"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f4f4; }}
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {{ 
        background-color: #1b458f; 
        background-image: {sidebar_bg_img};
        background-repeat: repeat;
        color: white; 
    }}
    
    /* Sidebar Text Colors */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stRadio label {{ color: white !important; }}
    
    /* CENTERING LOGO & TITLE */
    .sidebar-header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .sidebar-header img {{
        display: block;
        margin: 0 auto;
    }}
    
    /* NAVIGATION BUTTONS */
    div.stButton > button {{
        width: 100%;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        margin-bottom: 5px;
        transition: all 0.3s ease;
    }}
    
    /* Hover State - White Button, Blue Text */
    div.stButton > button:hover {{
        background-color: white !important;
        color: #1b458f !important;
        border-color: white !important;
        transform: scale(1.02);
    }}
    
    /* Selected State Indicator (Optional visual cue) */
    .nav-active {{
        border-left: 4px solid #d61a21 !important;
    }}

    /* ADMIN LOGIN AREA styling */
    .admin-login-container {{
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }}

    /* Metric Cards */
    div[data-testid="metric-container"] {{ 
        background-color: white; 
        border-left: 5px solid #d61a21; 
        padding: 15px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        border-radius: 5px; 
    }}
    
    /* Headers */
    h1, h2, h3 {{ color: #1b458f; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }}
    
    /* Admin Box */
    .admin-box {{
        border: 2px solid #d61a21;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA FUNCTIONS
# ==========================================
DATA_FILE = "rangers_data.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        # Date
        df['DateStr'] = df['Day'].astype(str) + "-" + df['Month'].astype(str) + "-" + df['Year'].astype(str)
        df['Date'] = pd.to_datetime(df['DateStr'], errors='coerce')
        # Result
        df['ResultCode'] = df['Win/Lose/Draw'].astype(str).str[0].str.upper()
        # Score
        if 'Score (Rangers First)' in df.columns:
            df['Score (Rangers First)'] = df['Score (Rangers First)'].astype(str)
        # Players
        cols_to_clean = [f'R{i}' for i in range(1, 23)]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', None).replace('None', None)
        
        return df.sort_values('Date', ascending=False)
    except:
        return pd.DataFrame()

def save_data(df_to_save):
    try:
        cols_to_drop = ['DateStr', 'Date', 'ResultCode']
        df_clean = df_to_save.drop(columns=[c for c in cols_to_drop if c in df_to_save.columns])
        df_clean.to_csv(DATA_FILE, index=False)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

def check_password():
    if "admin_password" not in st.secrets:
        st.error("🚨 Configure 'admin_password' in .streamlit/secrets.toml")
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
        st.error("😕 Password incorrect")
        return False
    return True

# ==========================================
# 3. INIT STATE
# ==========================================
if 'page' not in st.session_state: st.session_state['page'] = 'single'
if 'temp_new_players' not in st.session_state: st.session_state['temp_new_players'] = []

# ==========================================
# 4. SIDEBAR
# ==========================================
# Header Container
with st.sidebar.container():
    st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=100)
    st.markdown("<h2>IBROX ANALYTICS</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation Container
st.sidebar.markdown("### 🧭 MENU")
if st.sidebar.button("👤 Single Player Analysis"): 
    st.session_state['page'] = 'single'
if st.sidebar.button("⚔️ Head-to-Head Stats"): 
    st.session_state['page'] = 'h2h'

# Spacer logic to push Admin to bottom (using empty lines and a visual divider)
st.sidebar.markdown("<br>" * 8, unsafe_allow_html=True)
st.sidebar.markdown("<div class='admin-login-container'></div>", unsafe_allow_html=True)

# Bottom Admin Button
c_lock, c_btn = st.sidebar.columns([1, 5])
with c_lock:
    st.markdown("🔒")
with c_btn:
    if st.button("Admin Panel", key="adm_btn"):
        st.session_state['page'] = 'admin'

# ==========================================
# 5. DATA PREP
# ==========================================
df = load_data()
players_list = []
if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

# ==========================================
# 6. PAGE LOGIC
# ==========================================

# --- SINGLE PLAYER ---
if st.session_state['page'] == 'single':
    if not players_list:
        st.warning("Database empty.")
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 FILTERS")
        seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True)
        s_sea = st.sidebar.selectbox("Season", seasons)
        comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist())
        s_comp = st.sidebar.selectbox("Competition", comps)
        
        df_f = df.copy()
        if s_sea != 'All Time': df_f = df_f[df_f['Tag Season'] == s_sea]
        if s_comp != 'All Competitions': df_f = df_f[df_f['Competition'] == s_comp]

        # Random & Select
        if 'ps' not in st.session_state: st.session_state.ps = players_list[0]
        def rand_p(): st.session_state.ps = random.choice(players_list)
        st.sidebar.button("🔀 Pick Random Player", on_click=rand_p)
        
        sel_p = st.sidebar.selectbox("Select Player", players_list, key='ps')
        
        # Stats Logic
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
            
            c1, c2 = st.columns([3,1])
            with c1:
                st.title(f"{sel_p.upper()}")
                st.markdown(f"**{s_sea}** | **{s_comp}**")
            with c2:
                if win_rate > 70: t, c = "🔥 ON FIRE", "#d61a21"
                elif total > 100: t, c = "🏆 LEGEND", "#FFD700"
                else: t, c = "⚡ SQUAD", "#1b458f"
                st.markdown(f"<div style='text-align:center; padding:10px; border:2px solid {c}; color:{c}; font-weight:bold; border-radius:8px;'>{t}</div>", unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Apps", total)
            m2.metric("Starts", starts)
            m3.metric("Bench", subs)
            m4.metric("Win Rate", f"{win_rate:.1f}%")
            st.markdown("---")
            
            t1, t2, t3 = st.tabs(["📊 Stats", "📜 History", "⚽ Mates"])
            with t1:
                cc1, cc2 = st.columns(2)
                with cc1:
                    fig = go.Figure(data=[go.Pie(labels=['W','D','L'], values=[wins, len(p_df[p_df['ResultCode']=='D']), len(p_df[p_df['ResultCode']=='L'])], hole=.5, marker=dict(colors=['#1b458f','#B0B0B0','#d61a21']))])
                    fig.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=0))
                    st.plotly_chart(fig, use_container_width=True)
                with cc2:
                    fig2 = px.histogram(p_df, x='Date', color='Role', color_discrete_map={'Starter':'#1b458f','Sub':'#d61a21'}, nbins=20)
                    fig2.update_layout(height=250, bargap=0.1)
                    st.plotly_chart(fig2, use_container_width=True)
            with t2:
                cols = ['Date', 'Opponent', 'Competition', 'Score (Rangers First)', 'Win/Lose/Draw', 'Role']
                v_cols = [c for c in cols if c in p_df.columns]
                st.dataframe(p_df[v_cols], use_container_width=True, hide_index=True, column_config={"Score (Rangers First)": st.column_config.TextColumn("Score"), "Date": st.column_config.DateColumn("Match Date", format="DD/MM/YYYY")})
            with t3:
                if starts > 0:
                    s_df = p_df[p_df['Role']=='Starter']
                    mates = s_df[[f'R{i}' for i in range(1, 12)]].values.flatten()
                    mates = [m for m in mates if m != sel_p and str(m) != 'nan' and m is not None]
                    if mates:
                        cnt = pd.Series(mates).value_counts().head(10).reset_index()
                        cnt.columns = ['Player','Games']
                        f3 = px.bar(cnt, x='Games', y='Player', orientation='h', color_discrete_sequence=['#1b458f'])
                        f3.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(f3, use_container_width=True)
                    else: st.write("No data")
                else: st.info("Not enough starts")
        else: st.warning("No stats found.")

# --- H2H ---
elif st.session_state['page'] == 'h2h':
    st.title("⚔️ Head-to-Head")
    if len(players_list) < 2:
        st.warning("Need more players.")
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👥 PLAYERS")
        p1 = st.sidebar.selectbox("Player 1", players_list, index=0)
        p2 = st.sidebar.selectbox("Player 2", players_list, index=1)
        
        if p1 == p2: st.error("Select different players")
        else:
            # Simple Calc
            def calc(p):
                msk = df[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
                d = df[msk]
                w = len(d[d['ResultCode']=='W'])
                return len(d), w, (w/len(d)*100) if len(d) else 0
            
            t1, w1, wr1 = calc(p1)
            t2, w2, wr2 = calc(p2)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(p1)
                st.metric("Win Rate", f"{wr1:.1f}%")
                st.metric("Apps", t1)
            with c2:
                st.subheader(p2)
                st.metric("Win Rate", f"{wr2:.1f}%", delta=f"{wr2-wr1:.1f}%")
                st.metric("Apps", t2, delta=t2-t1)
            
            st.markdown("---")
            dat = pd.DataFrame([
                {'Player':p1, 'Metric':'Apps', 'Value':t1},
                {'Player':p2, 'Metric':'Apps', 'Value':t2},
                {'Player':p1, 'Metric':'Wins', 'Value':w1},
                {'Player':p2, 'Metric':'Wins', 'Value':w2}
            ])
            st.plotly_chart(px.bar(dat, x='Metric', y='Value', color='Player', barmode='group', color_discrete_map={p1:'#1b458f', p2:'#d61a21'}), use_container_width=True)

# --- ADMIN ---
elif st.session_state['page'] == 'admin':
    st.title("🔒 Admin Panel")
    if check_password():
        st.success("Logged in as Admin")
        
        tab_add, tab_edit = st.tabs(["➕ Add Match", "✏️ Edit Fixture"])
        
        # === ADD MATCH ===
        with tab_add:
            st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
            st.subheader("New Match Record")
            
            # --- AUTOCOMPLETE HELPERS ---
            # Get unique existing values for autocomplete
            ex_opps = sorted(df['Opponent'].unique().tolist()) if not df.empty else []
            ex_comps = sorted(df['Competition'].unique().tolist()) if not df.empty else []
            ex_seas = sorted(df['Tag Season'].unique().tolist()) if not df.empty else []

            c1, c2, c3 = st.columns(3)
            
            # DATE
            inp_date = c1.date_input("Date", datetime.today())
            
            # OPPONENT (Select or Add New)
            opp_choice = c2.selectbox("Opponent", ["Add New..."] + ex_opps, index=1 if ex_opps else 0)
            if opp_choice == "Add New...":
                inp_opp = c2.text_input("Type New Opponent", placeholder="e.g. Celtic")
            else:
                inp_opp = opp_choice
            
            # COMPETITION (Select or Add New)
            comp_choice = c3.selectbox("Competition", ["Add New..."] + ex_comps, index=1 if ex_comps else 0)
            if comp_choice == "Add New...":
                inp_comp = c3.text_input("Type New Competition", placeholder="e.g. Scottish Cup")
            else:
                inp_comp = comp_choice
            
            c4, c5, c6 = st.columns(3)
            
            # SCORE
            inp_score = c4.text_input("Score (Rangers First)", "0-0")
            
            # RESULT
            inp_res = c5.selectbox("Win/Lose/Draw", ["Win", "Draw", "Lose"])
            
            # SEASON (Select or Add New)
            sea_choice = c6.selectbox("Season Tag", ["Add New..."] + ex_seas, index=1 if ex_seas else 0)
            if sea_choice == "Add New...":
                inp_sea = c6.text_input("Type New Season", placeholder="e.g. 2025/2026")
            else:
                inp_sea = sea_choice
            
            st.markdown("---")
            
            # NEW PLAYER REGISTRATION
            st.markdown("#### 🆕 Register New Player")
            st.caption("Can't find a player in the dropdowns below? Add them here first.")
            c_new1, c_new2 = st.columns([3, 1])
            new_p_name = c_new1.text_input("Player Name (e.g. J. Tavernier)", label_visibility="collapsed", placeholder="Type new player name...")
            if c_new2.button("Add to List"):
                if new_p_name and new_p_name not in players_list:
                    st.session_state['temp_new_players'].append(new_p_name)
                    st.rerun() # Rerun to update dropdowns
                elif new_p_name in players_list:
                    st.warning("Player already exists.")
            
            st.markdown("---")
            st.markdown("#### 📋 Team Sheet (CSV Order)")
            
            # R1 to R22 Inputs
            col_starts, col_subs = st.columns(2)
            team_selections = {}
            
            with col_starts:
                st.markdown("**Starters (R1 - R11)**")
                for i in range(1, 12):
                    team_selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, index=0, key=f"sel_r{i}")
            
            with col_subs:
                st.markdown("**Subs (R12 - R22)**")
                for i in range(12, 23):
                    team_selections[f"R{i}"] = st.selectbox(f"R{i}", [""] + players_list, index=0, key=f"sel_r{i}")
            
            if st.button("💾 Save Match to Database"):
                if not inp_opp or not inp_score:
                    st.error("Missing Opponent or Score.")
                else:
                    row = {
                        'Day': inp_date.day,
                        'Month': inp_date.month,
                        'Year': inp_date.year,
                        'Opponent': inp_opp,
                        'Competition': inp_comp,
                        'Score (Rangers First)': inp_score,
                        'Win/Lose/Draw': inp_res,
                        'Tag Season': inp_sea
                    }
                    for k, v in team_selections.items():
                        row[k] = v if v != "" else None
                        
                    df_curr = pd.read_csv(DATA_FILE)
                    df_new = pd.DataFrame([row])
                    df_final = pd.concat([df_curr, df_new], ignore_index=True)
                    
                    if save_data(df_final):
                        st.success(f"Match vs {inp_opp} saved! Data refreshed.")
                        st.session_state['temp_new_players'] = []
                        
            st.markdown("</div>", unsafe_allow_html=True)

        # === EDIT FIXTURE ===
        with tab_edit:
            st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
            st.subheader("Edit Existing")
            if not df.empty:
                df['MatchLabel'] = df['Date'].dt.strftime('%Y-%m-%d') + " vs " + df['Opponent']
                mtch = st.selectbox("Select Match", df['MatchLabel'].unique())
                if mtch:
                    orig = df[df['MatchLabel'] == mtch].iloc[0]
                    
                    e1, e2 = st.columns(2)
                    ed_date = e1.date_input("Date", orig['Date'], key="ed_d")
                    ed_opp = e2.text_input("Opponent", orig['Opponent'], key="ed_o")
                    
                    st.info("Editing supports Date/Opponent correction. For full team edits, currently standard practice is to delete from CSV or ensure strict matching. This basic edit mode updates the main details.")
                    
                    if st.button("Update Metadata"):
                        raw = pd.read_csv(DATA_FILE)
                        mask = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                        if mask.any():
                            idx = raw[mask].index[0]
                            raw.at[idx, 'Day'] = ed_date.day
                            raw.at[idx, 'Month'] = ed_date.month
                            raw.at[idx, 'Year'] = ed_date.year
                            raw.at[idx, 'Opponent'] = ed_opp
                            if save_data(raw): st.success("Updated.")
                        else: st.error("Original record not found.")
            else: st.write("No data.")
            st.markdown("</div>", unsafe_allow_html=True)
