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
# Lion Rampant SVG (Subtle Blue on Dark Blue)
lion_svg = """
<svg width='80' height='80' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'>
<path d='M30,70 Q40,60 35,50 Q45,40 40,30 Q50,20 60,30 Q70,20 80,30 Q70,50 60,60 Q70,70 60,80 Q50,90 40,80 Q30,90 20,80 Q30,70 30,70 Z' 
      fill='#add8e6' opacity='0.05'/>
</svg>
"""
lion_b64 = base64.b64encode(lion_svg.encode('utf-8')).decode("utf-8")
sidebar_bg_img = f"url(\"data:image/svg+xml;base64,{lion_b64}\")"

# --- CUSTOM CSS (UX EXPERT MODE) ---
st.markdown(f"""
    <style>
    /* MAIN APP BACKGROUND */
    .stApp {{ background-color: #f8f9fa; }}

    /* SIDEBAR CONTAINER */
    section[data-testid="stSidebar"] {{ 
        background-color: #1b458f; 
        background-image: {sidebar_bg_img};
        background-repeat: repeat;
        color: white; 
    }}
    
    /* CONDENSE SIDEBAR SPACING */
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 2rem;
        padding-bottom: 1rem;
    }}
    div[data-testid="stSidebarUserContent"] div[data-testid="stVerticalBlock"] {{
        gap: 0.5rem; /* Tighter spacing between elements */
    }}
    
    /* TEXT COLOURS IN SIDEBAR */
    section[data-testid="stSidebar"] h1, h2, h3, label, p, .stMarkdown {{ color: white !important; }}

    /* LOGO AREA */
    .sidebar-logo {{
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    
    /* CUSTOM RADIO BUTTONS AS MENU ITEMS */
    /* Hide the actual radio circles */
    div[role="radiogroup"] > label > div:first-child {{
        display: None;
    }}
    div[role="radiogroup"] label {{
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 15px;
        margin-bottom: 4px;
        border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.1);
        cursor: pointer;
        transition: background 0.2s;
        width: 100%;
    }}
    div[role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.15);
    }}
    /* Selected Item Styling */
    div[role="radiogroup"] label[data-baseweb="radio"] {{
        background: white !important;
        color: #1b458f !important;
        border: 1px solid white;
        font-weight: bold;
    }}
    /* Force text color fix for selected item inside the label */
    div[role="radiogroup"] label[data-baseweb="radio"] p {{
        color: #1b458f !important;
    }}

    /* GLASSMORPHISM FILTER BOX */
    .filter-box {{
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    /* METRIC CARDS */
    div[data-testid="metric-container"] {{ 
        background-color: white; 
        border-left: 5px solid #d61a21; 
        padding: 10px 15px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-radius: 8px; 
    }}
    
    /* ADMIN AREA STYLING */
    .admin-footer {{
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        font-size: 0.8rem;
        color: rgba(255,255,255,0.6);
    }}
    
    /* HEADERS */
    h1, h2, h3 {{ color: #1b458f; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -0.5px; }}
    
    /* ADMIN FORM BOX */
    .admin-form-box {{
        background: white;
        border: 1px solid #e0e0e0;
        border-top: 4px solid #d61a21;
        border-radius: 8px;
        padding: 20px;
    }}
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
# 3. SIDEBAR LAYOUT (REDESIGNED)
# ==========================================

# 1. Header & Logo
with st.sidebar.container():
    st.markdown("<div class='sidebar-logo'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=80)
    st.markdown("### IBROX ANALYTICS")
    st.markdown("</div>", unsafe_allow_html=True)

# 2. Navigation (Radio as Menu)
st.sidebar.caption("MENU")
# We use a radio button styled like a list for navigation. It's faster and cleaner.
nav_selection = st.sidebar.radio(
    "Navigate",
    ["Single Player", "Head-to-Head", "Admin Panel"],
    index=0,
    label_visibility="collapsed"
)

# Update session state based on radio selection
st.session_state['page'] = 'single' if nav_selection == "Single Player" else 'h2h' if nav_selection == "Head-to-Head" else 'admin'

# 3. Data Loading & Global Lists
df = load_data()
players_list = []
if 'temp_new_players' not in st.session_state: st.session_state['temp_new_players'] = []

if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

# 4. Filters (Glassmorphism Box) - Only show if NOT in Admin
df_f = df.copy()
s_sea = 'All Time'
s_comp = 'All Competitions'

if st.session_state['page'] != 'admin':
    st.sidebar.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    st.sidebar.caption("GLOBAL FILTERS")
    
    seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True) if not df.empty else []
    s_sea = st.sidebar.selectbox("Season", seasons, label_visibility="collapsed")
    
    comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist()) if not df.empty else []
    s_comp = st.sidebar.selectbox("Competition", comps, label_visibility="collapsed")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    # Apply Filters
    if s_sea != 'All Time': df_f = df_f[df_f['Tag Season'] == s_sea]
    if s_comp != 'All Competitions': df_f = df_f[df_f['Competition'] == s_comp]

# ==========================================
# 4. PAGE CONTENT
# ==========================================

# --- SINGLE PLAYER DASHBOARD ---
if st.session_state['page'] == 'single':
    if not players_list:
        st.info("👋 Welcome! The database is currently empty. Go to the **Admin Panel** to add your first match.")
    else:
        # Random Player Helper
        if 'ps' not in st.session_state: st.session_state.ps = players_list[0]
        def pick_rand(): st.session_state.ps = random.choice(players_list)
        
        # Top Control Bar
        c_top1, c_top2 = st.columns([3, 1])
        with c_top1:
            sel_p = st.selectbox("Search Player:", players_list, key='ps', label_visibility="collapsed")
        with c_top2:
            st.button("🔀 Pick Random", on_click=pick_rand, use_container_width=True)

        # Calc Stats
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
            
            # Header
            h1, h2 = st.columns([3, 1])
            with h1:
                st.title(sel_p.upper())
                st.caption(f"{s_sea} • {s_comp}")
            with h2:
                if win_rate > 70: t, c = "🔥 ON FIRE", "#d61a21"
                elif total > 100: t, c = "🏆 LEGEND", "#FFD700"
                else: t, c = "⚡ SQUAD", "#1b458f"
                st.markdown(f"<div style='text-align:center; padding:8px; background:{c}; color:white; font-weight:bold; border-radius:6px; margin-top:10px;'>{t}</div>", unsafe_allow_html=True)

            # KPI Grid
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Apps", total)
            k2.metric("Starts", starts)
            k3.metric("Sub Apps", subs)
            k4.metric("Win Rate", f"{win_rate:.1f}%")

            st.markdown("---")

            # Tabs
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "📜 Match Log", "🤝 Connections"])

            with tab1:
                g1, g2 = st.columns(2)
                with g1:
                    st.subheader("Results Breakdown")
                    fig = go.Figure(data=[go.Pie(labels=['Wins','Draws','Losses'], values=[wins, len(p_df[p_df['ResultCode']=='D']), len(p_df[p_df['ResultCode']=='L'])], hole=.6, marker=dict(colors=['#1b458f','#e0e0e0','#d61a21']))])
                    fig.update_layout(height=280, margin=dict(t=0,b=0,l=0,r=0), showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.subheader("Recent Activity")
                    fig2 = px.histogram(p_df, x='Date', color='Role', color_discrete_map={'Starter':'#1b458f','Sub':'#d61a21'}, nbins=20)
                    fig2.update_layout(height=280, bargap=0.2, margin=dict(t=20,b=0,l=0,r=0))
                    st.plotly_chart(fig2, use_container_width=True)

            with tab2:
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

            with tab3:
                st.subheader("Common Starters")
                if starts > 0:
                    s_df = p_df[p_df['Role']=='Starter']
                    mates = s_df[[f'R{i}' for i in range(1, 12)]].values.flatten()
                    mates = [m for m in mates if m != sel_p and str(m) != 'nan' and m is not None]
                    if mates:
                        cnt = pd.Series(mates).value_counts().head(8).reset_index()
                        cnt.columns = ['Player','Games']
                        f3 = px.bar(cnt, x='Games', y='Player', orientation='h', color_discrete_sequence=['#1b458f'])
                        f3.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
                        st.plotly_chart(f3, use_container_width=True)
                    else: st.info("No shared start data.")
                else: st.info("Player has not started any games yet.")
        else:
            st.warning(f"No data found for **{sel_p}** in {s_sea}.")

# --- HEAD TO HEAD ---
elif st.session_state['page'] == 'h2h':
    st.title("⚔️ Head-to-Head")
    if len(players_list) < 2:
        st.warning("Need at least 2 players in the database to compare.")
    else:
        col_sel1, col_sel2 = st.columns(2)
        p1 = col_sel1.selectbox("Player 1", players_list, index=0)
        p2 = col_sel2.selectbox("Player 2", players_list, index=1)

        if p1 == p2: st.error("Select different players.")
        else:
            def get_h2h_stats(p):
                msk = df_f[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
                d = df_f[msk]
                w = len(d[d['ResultCode']=='W'])
                starts = len(d[d[[f'R{i}' for i in range(1, 12)]].isin([p]).any(axis=1)])
                return {'Total': len(d), 'Wins': w, 'Starts': starts, 'Win Rate': (w/len(d)*100) if len(d) else 0}

            s1 = get_h2h_stats(p1)
            s2 = get_h2h_stats(p2)

            # Metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.subheader(p1)
                st.metric("Win Rate", f"{s1['Win Rate']:.1f}%")
                st.metric("Apps", s1['Total'])
            with m3:
                st.subheader(p2)
                st.metric("Win Rate", f"{s2['Win Rate']:.1f}%", delta=f"{s2['Win Rate']-s1['Win Rate']:.1f}%")
                st.metric("Apps", s2['Total'], delta=s2['Total']-s1['Total'])
            with m2:
                # Radar Chart Logic
                categories = ['Total Apps', 'Wins', 'Starts', 'Win Rate']
                # Normalize Win Rate to be visually comparable with counts (scale it? or just raw?) 
                # Radar charts work best when scales are similar, but let's just try raw first.
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[s1['Total'], s1['Wins'], s1['Starts'], s1['Win Rate']],
                    theta=categories, fill='toself', name=p1, line_color='#1b458f'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=[s2['Total'], s2['Wins'], s2['Starts'], s2['Win Rate']],
                    theta=categories, fill='toself', name=p2, line_color='#d61a21'
                ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, height=250, margin=dict(t=20,b=20,l=20,r=20))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            # Comparison Bar
            comp_df = pd.DataFrame([
                {'Player': p1, 'Metric': 'Total Apps', 'Value': s1['Total']},
                {'Player': p2, 'Metric': 'Total Apps', 'Value': s2['Total']},
                {'Player': p1, 'Metric': 'Starts', 'Value': s1['Starts']},
                {'Player': p2, 'Metric': 'Starts', 'Value': s2['Starts']},
                {'Player': p1, 'Metric': 'Wins', 'Value': s1['Wins']},
                {'Player': p2, 'Metric': 'Wins', 'Value': s2['Wins']},
            ])
            fig_bar = px.bar(comp_df, x='Metric', y='Value', color='Player', barmode='group', color_discrete_map={p1:'#1b458f', p2:'#d61a21'})
            st.plotly_chart(fig_bar, use_container_width=True)

# --- ADMIN PANEL ---
elif st.session_state['page'] == 'admin':
    st.title("🔒 Admin Panel")
    if check_password():
        st.success("Logged in successfully")
        
        tab_add, tab_edit = st.tabs(["➕ Add Match", "✏️ Edit Fixture"])
        
        # ADD MATCH
        with tab_add:
            st.markdown("<div class='admin-form-box'>", unsafe_allow_html=True)
            st.subheader("New Match Record")
            
            # Autocomplete Data
            ex_opps = sorted(df['Opponent'].unique().tolist()) if not df.empty else []
            ex_comps = sorted(df['Competition'].unique().tolist()) if not df.empty else []
            ex_seas = sorted(df['Tag Season'].unique().tolist()) if not df.empty else []
            
            c1, c2, c3 = st.columns(3)
            inp_date = c1.date_input("Date", datetime.today())
            
            # Smart Select/Add for Opponent
            opp_sel = c2.selectbox("Opponent", ["Select..."] + ex_opps + ["➕ Add New"])
            inp_opp = c2.text_input("New Opponent Name") if opp_sel == "➕ Add New" else (opp_sel if opp_sel != "Select..." else "")
            
            # Smart Select/Add for Competition
            comp_sel = c3.selectbox("Competition", ["Select..."] + ex_comps + ["➕ Add New"])
            inp_comp = c3.text_input("New Competition Name") if comp_sel == "➕ Add New" else (comp_sel if comp_sel != "Select..." else "")

            c4, c5, c6 = st.columns(3)
            inp_score = c4.text_input("Score (Rangers-Opp)", placeholder="e.g. 3-1")
            inp_res = c5.selectbox("Result", ["Win", "Draw", "Lose"])
            
            # Smart Select/Add for Season
            sea_sel = c6.selectbox("Season", ["Select..."] + ex_seas + ["➕ Add New"])
            inp_sea = c6.text_input("New Season (e.g. 25/26)") if sea_sel == "➕ Add New" else (sea_sel if sea_sel != "Select..." else "")
            
            st.markdown("---")
            
            # NEW PLAYER REG
            with st.expander("🆕 Register New Player (If not in list)"):
                np_col1, np_col2 = st.columns([3,1])
                new_p = np_col1.text_input("Name", placeholder="e.g. J. Butland", label_visibility="collapsed")
                if np_col2.button("Add Player"):
                    if new_p and new_p not in players_list:
                        st.session_state['temp_new_players'].append(new_p)
                        st.rerun()
            
            # SQUAD ENTRY
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
            st.markdown("<div class='admin-form-box'>", unsafe_allow_html=True)
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
                        # Strict match
                        m = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                        if m.any():
                            idx = raw[mask].index[0]
                            raw.at[idx, 'Day'] = new_d.day
                            raw.at[idx, 'Month'] = new_d.month
                            raw.at[idx, 'Year'] = new_d.year
                            raw.at[idx, 'Opponent'] = new_o
                            if save_data(raw): st.success("Updated.")
                        else: st.error("Record not found.")
            else: st.info("No matches.")
            st.markdown("</div>", unsafe_allow_html=True)
