import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import base64
from datetime import datetime, timedelta
import numpy as np

# ==========================================
# 1. ENHANCED CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Ibrox Analytics Pro",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENHANCED ASSETS ---
lion_svg = """
<svg width='80' height='80' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'>
<path d='M30,70 Q40,60 35,50 Q45,40 40,30 Q50,20 60,30 Q70,20 80,30 Q70,50 60,60 Q70,70 60,80 Q50,90 40,80 Q30,90 20,80 Q30,70 30,70 Z' 
      fill='#add8e6' opacity='0.08'/>
</svg>
"""
lion_b64 = base64.b64encode(lion_svg.encode('utf-8')).decode("utf-8")
sidebar_bg_img = f"url(\"data:image/svg+xml;base64,{lion_b64}\")"

# --- PREMIUM CSS WITH ANIMATIONS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* MAIN APP BACKGROUND WITH GRADIENT */
    .stApp {{ 
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        font-family: 'Inter', sans-serif;
    }}

    /* SIDEBAR WITH ENHANCED STYLING */
    section[data-testid="stSidebar"] {{ 
        background: linear-gradient(180deg, #1a3d7c 0%, #1b458f 100%);
        background-image: {sidebar_bg_img};
        background-repeat: repeat;
        box-shadow: 4px 0 20px rgba(0,0,0,0.1);
    }}
    
    /* SIDEBAR SPACING */
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }}
    div[data-testid="stSidebarUserContent"] div[data-testid="stVerticalBlock"] {{
        gap: 0.3rem;
    }}
    
    /* SIDEBAR TEXT */
    section[data-testid="stSidebar"] h1, h2, h3, label, p, .stMarkdown {{ 
        color: white !important; 
        font-family: 'Inter', sans-serif;
    }}

    /* LOGO AREA WITH GLOW */
    .sidebar-logo {{
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(255,255,255,0.15);
    }}
    .sidebar-logo img {{
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
        transition: transform 0.3s ease;
    }}
    .sidebar-logo img:hover {{
        transform: scale(1.05);
    }}
    
    /* ENHANCED RADIO BUTTONS AS MENU */
    div[role="radiogroup"] > label > div:first-child {{
        display: none;
    }}
    div[role="radiogroup"] label {{
        background: rgba(255, 255, 255, 0.08);
        padding: 12px 16px;
        margin-bottom: 6px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        backdrop-filter: blur(10px);
    }}
    div[role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(4px);
        border-color: rgba(255,255,255,0.3);
    }}
    div[role="radiogroup"] label[data-baseweb="radio"] {{
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%) !important;
        color: #1b458f !important;
        border: 2px solid white;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(6px);
    }}
    div[role="radiogroup"] label[data-baseweb="radio"] p {{
        color: #1b458f !important;
    }}

    /* GLASSMORPHISM FILTER BOX */
    .filter-box {{
        background: rgba(0, 0, 0, 0.15);
        border-radius: 12px;
        padding: 12px;
        margin-top: 12px;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
    }}
    
    /* PREMIUM METRIC CARDS */
    div[data-testid="metric-container"] {{ 
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-left: 4px solid #d61a21;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-radius: 12px;
        transition: all 0.3s ease;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }}
    
    /* ENHANCED HEADERS */
    h1, h2, h3 {{ 
        color: #1b458f;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    
    h1 {{
        font-size: 2.5rem;
        background: linear-gradient(135deg, #1b458f 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* PREMIUM TABS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(27, 69, 143, 0.1);
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #1b458f 0%, #2563eb 100%) !important;
        color: white !important;
    }}
    
    /* ENHANCED BUTTONS */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }}
    
    /* DATAFRAME STYLING */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    /* ADMIN FORM BOX */
    .admin-form-box {{
        background: white;
        border: 1px solid #e5e7eb;
        border-top: 4px solid #d61a21;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    /* BADGE STYLES */
    .status-badge {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* STREAK INDICATOR */
    .streak-indicator {{
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    }}
    
    /* LOADING ANIMATION */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    /* CARD CONTAINER */
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transform: translateY(-4px);
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ENHANCED DATA LOGIC WITH ANALYTICS
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

# ENHANCED ANALYTICS FUNCTIONS
def calculate_form_streak(matches_df):
    """Calculate current win/loss streak"""
    if matches_df.empty:
        return 0, ""
    results = matches_df.sort_values('Date', ascending=False)['ResultCode'].tolist()
    if not results:
        return 0, ""
    
    current = results[0]
    streak = 1
    for r in results[1:]:
        if r == current:
            streak += 1
        else:
            break
    
    streak_type = "W" if current == "W" else "L" if current == "L" else "D"
    return streak, streak_type

def calculate_momentum_score(matches_df, last_n=5):
    """Calculate momentum based on recent results (0-100 scale)"""
    if matches_df.empty or len(matches_df) < last_n:
        return 50
    
    recent = matches_df.sort_values('Date', ascending=False).head(last_n)
    wins = len(recent[recent['ResultCode'] == 'W'])
    draws = len(recent[recent['ResultCode'] == 'D'])
    
    # Weight more recent games higher
    weights = [1.5, 1.3, 1.1, 1.0, 0.9]
    score = 0
    for idx, (_, row) in enumerate(recent.iterrows()):
        if idx >= len(weights):
            break
        if row['ResultCode'] == 'W':
            score += 3 * weights[idx]
        elif row['ResultCode'] == 'D':
            score += 1 * weights[idx]
    
    max_score = sum(weights[:len(recent)]) * 3
    return int((score / max_score) * 100) if max_score > 0 else 50

def get_partnership_strength(df, player1, player2):
    """Calculate how well two players perform together"""
    starter_cols = [f'R{i}' for i in range(1, 12)]
    mask1 = df[starter_cols].isin([player1]).any(axis=1)
    mask2 = df[starter_cols].isin([player2]).any(axis=1)
    together = df[mask1 & mask2]
    
    if len(together) == 0:
        return 0, 0
    
    wins = len(together[together['ResultCode'] == 'W'])
    return len(together), (wins / len(together) * 100) if len(together) > 0 else 0

# ==========================================
# 3. ENHANCED SIDEBAR
# ==========================================

with st.sidebar.container():
    st.markdown("<div class='sidebar-logo'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/en/4/43/Rangers_FC.svg", width=80)
    st.markdown("### IBROX ANALYTICS PRO")
    st.caption("Advanced Performance Intelligence")
    st.markdown("</div>", unsafe_allow_html=True)

st.sidebar.caption("📊 NAVIGATION")
nav_selection = st.sidebar.radio(
    "Navigate",
    ["🎯 Player Dashboard", "⚔️ Head-to-Head", "📈 Team Analytics", "🏆 Season Overview", "🔒 Admin Panel"],
    index=0,
    label_visibility="collapsed"
)

# Map selection to page
page_map = {
    "🎯 Player Dashboard": "single",
    "⚔️ Head-to-Head": "h2h",
    "📈 Team Analytics": "team",
    "🏆 Season Overview": "season",
    "🔒 Admin Panel": "admin"
}
st.session_state['page'] = page_map[nav_selection]

# Data Loading
df = load_data()
players_list = []
if 'temp_new_players' not in st.session_state:
    st.session_state['temp_new_players'] = []

if not df.empty:
    all_p = pd.unique(df[[f'R{i}' for i in range(1, 23)]].values.ravel('K'))
    combined = list(set(list(all_p) + st.session_state['temp_new_players']))
    players_list = [p for p in combined if p and str(p).lower() != 'nan' and str(p).lower() != 'none']
    players_list.sort()

# Filters
df_f = df.copy()
s_sea = 'All Time'
s_comp = 'All Competitions'

if st.session_state['page'] != 'admin':
    st.sidebar.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    st.sidebar.caption("🔍 FILTERS")
    
    seasons = ['All Time'] + sorted(df['Tag Season'].unique().tolist(), reverse=True) if not df.empty else []
    s_sea = st.sidebar.selectbox("Season", seasons, label_visibility="collapsed")
    
    comps = ['All Competitions'] + sorted(df['Competition'].unique().tolist()) if not df.empty else []
    s_comp = st.sidebar.selectbox("Competition", comps, label_visibility="collapsed")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    if s_sea != 'All Time':
        df_f = df_f[df_f['Tag Season'] == s_sea]
    if s_comp != 'All Competitions':
        df_f = df_f[df_f['Competition'] == s_comp]
    
    # Quick Stats in Sidebar
    if not df_f.empty:
        st.sidebar.markdown("---")
        st.sidebar.caption("📊 QUICK STATS")
        total_matches = len(df_f)
        total_wins = len(df_f[df_f['ResultCode'] == 'W'])
        win_pct = (total_wins / total_matches * 100) if total_matches > 0 else 0
        st.sidebar.metric("Win Rate", f"{win_pct:.1f}%", f"{total_wins}/{total_matches}")

# ==========================================
# 4. ENHANCED PAGE CONTENT
# ==========================================

# --- ENHANCED PLAYER DASHBOARD ---
if st.session_state['page'] == 'single':
    if not players_list:
        st.info("👋 Welcome to Ibrox Analytics Pro! Add your first match in the Admin Panel.")
    else:
        # Player Selection
        if 'ps' not in st.session_state:
            st.session_state.ps = players_list[0]
        
        def pick_rand():
            st.session_state.ps = random.choice(players_list)
        
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            sel_p = st.selectbox("🔍 Search Player:", players_list, key='ps', label_visibility="collapsed")
        with col_header2:
            st.button("🎲 Random Player", on_click=pick_rand, use_container_width=True)

        # Calculate Stats
        starter_cols = [f'R{i}' for i in range(1, 12)]
        sub_cols = [f'R{i}' for i in range(12, 23)]
        mask = df_f[starter_cols + sub_cols].isin([sel_p]).any(axis=1)
        p_df = df_f[mask].copy()

        if not p_df.empty:
            p_df['Role'] = p_df.apply(lambda x: 'Starter' if sel_p in x[starter_cols].values else 'Sub', axis=1)
            starts = len(p_df[p_df['Role'] == 'Starter'])
            subs = len(p_df[p_df['Role'] == 'Sub'])
            wins = len(p_df[p_df['ResultCode'] == 'W'])
            draws = len(p_df[p_df['ResultCode'] == 'D'])
            losses = len(p_df[p_df['ResultCode'] == 'L'])
            total = starts + subs
            win_rate = (wins/total*100) if total else 0
            
            # Calculate advanced metrics
            streak, streak_type = calculate_form_streak(p_df)
            momentum = calculate_momentum_score(p_df)
            
            # Header Section
            st.markdown(f"<h1>⚽ {sel_p.upper()}</h1>", unsafe_allow_html=True)
            
            col_info1, col_info2, col_info3 = st.columns([2, 2, 1])
            with col_info1:
                st.caption(f"📅 {s_sea} • 🏆 {s_comp}")
            with col_info2:
                if streak > 0:
                    streak_emoji = "🔥" if streak_type == "W" else "❄️" if streak_type == "L" else "➖"
                    st.markdown(f"<div class='streak-indicator'>{streak_emoji} {streak} Game {streak_type}-Streak</div>", unsafe_allow_html=True)
            with col_info3:
                if win_rate > 75:
                    badge = f"<div class='status-badge' style='background: linear-gradient(135deg, #d61a21 0%, #ff4444 100%);'>🔥 ELITE</div>"
                elif win_rate > 60:
                    badge = f"<div class='status-badge' style='background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);'>🏆 STAR</div>"
                elif total > 100:
                    badge = f"<div class='status-badge' style='background: linear-gradient(135deg, #1b458f 0%, #2563eb 100%);'>👑 LEGEND</div>"
                else:
                    badge = f"<div class='status-badge' style='background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);'>⚡ SQUAD</div>"
                st.markdown(badge, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Enhanced KPI Grid
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            kpi1.metric("📊 Total Apps", total)
            kpi2.metric("🎯 Starts", starts, f"{(starts/total*100):.0f}%" if total > 0 else "0%")
            kpi3.metric("🔄 Sub Apps", subs)
            kpi4.metric("🏆 Win Rate", f"{win_rate:.1f}%")
            kpi5.metric("💪 Momentum", f"{momentum}/100")

            st.markdown("---")

            # Enhanced Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Performance Trends", "📜 Match Log", "🤝 Partnerships"])

            with tab1:
                col_over1, col_over2 = st.columns(2)
                
                with col_over1:
                    st.subheader("Results Distribution")
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Wins','Draws','Losses'],
                        values=[wins, draws, losses],
                        hole=.65,
                        marker=dict(colors=['#1b458f','#94a3b8','#d61a21']),
                        textinfo='label+percent',
                        textfont=dict(size=14, color='white', family='Inter'),
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                    )])
                    fig_pie.update_layout(
                        height=320,
                        margin=dict(t=0,b=0,l=0,r=0),
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                        font=dict(family='Inter', size=12)
                    )
                    # Add annotation in center
                    fig_pie.add_annotation(
                        text=f"<b>{win_rate:.1f}%</b><br>Win Rate",
                        showarrow=False,
                        font=dict(size=18, family='Inter', color='#1b458f')
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_over2:
                    st.subheader("Role Distribution")
                    role_data = pd.DataFrame({
                        'Role': ['Starter', 'Substitute'],
                        'Count': [starts, subs],
                        'Win Rate': [
                            (len(p_df[(p_df['Role']=='Starter') & (p_df['ResultCode']=='W')]) / starts * 100) if starts > 0 else 0,
                            (len(p_df[(p_df['Role']=='Sub') & (p_df['ResultCode']=='W')]) / subs * 100) if subs > 0 else 0
                        ]
                    })
                    
                    fig_role = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=('Appearances', 'Win Rate'),
                        specs=[[{'type':'bar'}, {'type':'bar'}]]
                    )
                    
                    fig_role.add_trace(
                        go.Bar(x=role_data['Role'], y=role_data['Count'], 
                               marker_color=['#1b458f', '#d61a21'],
                               text=role_data['Count'], textposition='auto'),
                        row=1, col=1
                    )
                    
                    fig_role.add_trace(
                        go.Bar(x=role_data['Role'], y=role_data['Win Rate'],
                               marker_color=['#1b458f', '#d61a21'],
                               text=[f"{v:.1f}%" for v in role_data['Win Rate']], 
                               textposition='auto'),
                        row=1, col=2
                    )
                    
                    fig_role.update_layout(
                        height=320,
                        showlegend=False,
                        margin=dict(t=40,b=0,l=0,r=0),
                        font=dict(family='Inter')
                    )
                    st.plotly_chart(fig_role, use_container_width=True)
                
                # Competition Breakdown
                st.subheader("Performance by Competition")
                comp_stats = p_df.groupby('Competition').agg({
                    'ResultCode': ['count', lambda x: (x=='W').sum()]
                }).reset_index()
                comp_stats.columns = ['Competition', 'Matches', 'Wins']
                comp_stats['Win Rate'] = (comp_stats['Wins'] / comp_stats['Matches'] * 100).round(1)
                comp_stats = comp_stats.sort_values('Matches', ascending=True)
                
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(
                    y=comp_stats['Competition'],
                    x=comp_stats['Matches'],
                    orientation='h',
                    marker=dict(
                        color=comp_stats['Win Rate'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Win %")
                    ),
                    text=[f"{m} games ({w:.0f}%)" for m, w in zip(comp_stats['Matches'], comp_stats['Win Rate'])],
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>Matches: %{x}<br>Win Rate: %{marker.color:.1f}%<extra></extra>'
                ))
                fig_comp.update_layout(
                    height=max(250, len(comp_stats) * 40),
                    margin=dict(t=20,b=0,l=0,r=0),
                    xaxis_title="Matches Played",
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_comp, use_container_width=True)

            with tab2:
                st.subheader("Performance Timeline")
                
                # Create monthly aggregation
                p_df_sorted = p_df.sort_values('Date')
                p_df_sorted['YearMonth'] = p_df_sorted['Date'].dt.to_period('M').astype(str)
                
                monthly = p_df_sorted.groupby('YearMonth').agg({
                    'ResultCode': ['count', lambda x: (x=='W').sum(), lambda x: (x=='D').sum(), lambda x: (x=='L').sum()]
                }).reset_index()
                monthly.columns = ['Month', 'Total', 'Wins', 'Draws', 'Losses']
                monthly['Win Rate'] = (monthly['Wins'] / monthly['Total'] * 100).round(1)
                
                fig_timeline = go.Figure()
                
                fig_timeline.add_trace(go.Scatter(
                    x=monthly['Month'], y=monthly['Win Rate'],
                    mode='lines+markers',
                    name='Win Rate',
                    line=dict(color='#1b458f', width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(27, 69, 143, 0.1)'
                ))
                
                fig_timeline.update_layout(
                    height=350,
                    xaxis_title="Period",
                    yaxis_title="Win Rate (%)",
                    hovermode='x unified',
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Form Guide (Last 10 Matches)
                col_form1, col_form2 = st.columns([2, 1])
                with col_form1:
                    st.subheader("Recent Form (Last 10)")
                    last_10 = p_df.sort_values('Date', ascending=False).head(10)
                    form_icons = []
                    for _, match in last_10.iterrows():
                        if match['ResultCode'] == 'W':
                            form_icons.append("🟢")
                        elif match['ResultCode'] == 'D':
                            form_icons.append("🟡")
                        else:
                            form_icons.append("🔴")
                    
                    st.markdown(f"<h2 style='text-align: center; letter-spacing: 8px;'>{''.join(form_icons)}</h2>", unsafe_allow_html=True)
                    
                with col_form2:
                    st.metric("Last 10 Win %", f"{(last_10['ResultCode']=='W').sum()/len(last_10)*100:.0f}%")
                    st.metric("Last 10 Games", len(last_10))

            with tab3:
                st.subheader("Complete Match History")
                
                # Add result emoji column
                def result_emoji(result):
                    if result == 'W': return '🟢'
                    elif result == 'D': return '🟡'
                    else: return '🔴'
                
                p_df_display = p_df.copy()
                p_df_display['Result'] = p_df_display['ResultCode'].apply(result_emoji)
                
                cols = ['Date', 'Result', 'Opponent', 'Competition', 'Score (Rangers First)', 'Role']
                v_cols = [c for c in cols if c in p_df_display.columns]
                
                st.dataframe(
                    p_df_display[v_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.DateColumn("Match Date", format="DD/MM/YYYY"),
                        "Score (Rangers First)": st.column_config.TextColumn("Score"),
                        "Result": st.column_config.TextColumn("", width="small")
                    }
                )
                
                # Download button
                csv = p_df_display[v_cols].to_csv(index=False)
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv,
                    file_name=f"{sel_p}_match_history.csv",
                    mime="text/csv"
                )

            with tab4:
                st.subheader("Partnership Analysis")
                
                if starts > 0:
                    s_df = p_df[p_df['Role']=='Starter']
                    mates = s_df[[f'R{i}' for i in range(1, 12)]].values.flatten()
                    mates = [m for m in mates if m != sel_p and str(m) != 'nan' and m is not None]
                    
                    if mates:
                        mate_counts = pd.Series(mates).value_counts().head(10).reset_index()
                        mate_counts.columns = ['Player','Games']
                        
                        # Calculate win rate for each partner
                        mate_counts['Win Rate'] = mate_counts['Player'].apply(
                            lambda p: get_partnership_strength(s_df, sel_p, p)[1]
                        )
                        
                        # Create enhanced bar chart
                        fig_partners = go.Figure()
                        
                        fig_partners.add_trace(go.Bar(
                            y=mate_counts['Player'],
                            x=mate_counts['Games'],
                            orientation='h',
                            marker=dict(
                                color=mate_counts['Win Rate'],
                                colorscale='RdYlGn',
                                showscale=True,
                                colorbar=dict(title="Win %", x=1.1)
                            ),
                            text=[f"{g} games ({wr:.0f}%)" for g, wr in zip(mate_counts['Games'], mate_counts['Win Rate'])],
                            textposition='auto',
                            hovertemplate='<b>%{y}</b><br>Games Together: %{x}<br>Win Rate: %{marker.color:.1f}%<extra></extra>'
                        ))
                        
                        fig_partners.update_layout(
                            yaxis={'categoryorder':'total ascending'},
                            height=max(300, len(mate_counts) * 35),
                            xaxis_title="Games Together",
                            margin=dict(t=20,b=0,l=0,r=100),
                            font=dict(family='Inter')
                        )
                        st.plotly_chart(fig_partners, use_container_width=True)
                        
                        # Best Partnership Highlight
                        best_partner = mate_counts.iloc[0]
                        st.info(f"🤝 **Best Partnership**: {best_partner['Player']} ({best_partner['Games']} games, {best_partner['Win Rate']:.1f}% win rate)")
                    else:
                        st.info("No partnership data available.")
                else:
                    st.info("Player has not started any games yet.")
        else:
            st.warning(f"No data found for **{sel_p}** in {s_sea}.")

# --- ENHANCED HEAD-TO-HEAD ---
elif st.session_state['page'] == 'h2h':
    st.markdown("<h1>⚔️ HEAD-TO-HEAD COMPARISON</h1>", unsafe_allow_html=True)
    
    if len(players_list) < 2:
        st.warning("Need at least 2 players in the database to compare.")
    else:
        col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])
        p1 = col_sel1.selectbox("👤 Player 1", players_list, index=0)
        p2 = col_sel2.selectbox("👤 Player 2", players_list, index=min(1, len(players_list)-1))
        
        if col_sel3.button("🔄 Swap", use_container_width=True):
            # Swap logic would go here
            pass

        if p1 == p2:
            st.error("⚠️ Please select different players.")
        else:
            def get_h2h_stats(p):
                starter_cols = [f'R{i}' for i in range(1, 12)]
                msk = df_f[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1)
                d = df_f[msk]
                w = len(d[d['ResultCode']=='W'])
                dr = len(d[d['ResultCode']=='D'])
                l = len(d[d['ResultCode']=='L'])
                starts = len(d[d[starter_cols].isin([p]).any(axis=1)])
                momentum = calculate_momentum_score(d)
                return {
                    'Total': len(d), 'Wins': w, 'Draws': dr, 'Losses': l,
                    'Starts': starts, 'Subs': len(d) - starts,
                    'Win Rate': (w/len(d)*100) if len(d) else 0,
                    'Momentum': momentum
                }

            s1 = get_h2h_stats(p1)
            s2 = get_h2h_stats(p2)

            st.markdown("<br>", unsafe_allow_html=True)

            # Comparison Cards
            card1, card_vs, card2 = st.columns([2, 1, 2])
            
            with card1:
                st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='color: #1b458f; text-align: center;'>{p1}</h2>
                    <h3 style='text-align: center; color: #64748b;'>Win Rate: {s1['Win Rate']:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1a, col1b = st.columns(2)
                col1a.metric("Total Apps", s1['Total'])
                col1a.metric("Wins", s1['Wins'])
                col1a.metric("Momentum", f"{s1['Momentum']}/100")
                col1b.metric("Starts", s1['Starts'])
                col1b.metric("Draws", s1['Draws'])
                col1b.metric("Losses", s1['Losses'])
            
            with card_vs:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("<h1 style='text-align: center; color: #d61a21;'>VS</h1>", unsafe_allow_html=True)
                
                # Winner indicator
                if s1['Win Rate'] > s2['Win Rate']:
                    st.markdown(f"<p style='text-align: center; color: #1b458f; font-weight: bold;'>← {p1} Leads</p>", unsafe_allow_html=True)
                elif s2['Win Rate'] > s1['Win Rate']:
                    st.markdown(f"<p style='text-align: center; color: #1b458f; font-weight: bold;'>{p2} Leads →</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='text-align: center; color: #64748b; font-weight: bold;'>Even Match</p>", unsafe_allow_html=True)
            
            with card2:
                st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='color: #d61a21; text-align: center;'>{p2}</h2>
                    <h3 style='text-align: center; color: #64748b;'>Win Rate: {s2['Win Rate']:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col2a, col2b = st.columns(2)
                col2a.metric("Total Apps", s2['Total'], delta=s2['Total']-s1['Total'])
                col2a.metric("Wins", s2['Wins'], delta=s2['Wins']-s1['Wins'])
                col2a.metric("Momentum", f"{s2['Momentum']}/100", delta=s2['Momentum']-s1['Momentum'])
                col2b.metric("Starts", s2['Starts'], delta=s2['Starts']-s1['Starts'])
                col2b.metric("Draws", s2['Draws'], delta=s2['Draws']-s1['Draws'])
                col2b.metric("Losses", s2['Losses'], delta=s2['Losses']-s1['Losses'])

            st.markdown("---")

            # Visual Comparisons
            tab_radar, tab_bars, tab_timeline = st.tabs(["📊 Radar Comparison", "📈 Detailed Stats", "📅 Timeline"])
            
            with tab_radar:
                categories = ['Total Apps', 'Wins', 'Starts', 'Win Rate', 'Momentum']
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=[s1['Total'], s1['Wins'], s1['Starts'], s1['Win Rate'], s1['Momentum']],
                    theta=categories,
                    fill='toself',
                    name=p1,
                    line_color='#1b458f',
                    fillcolor='rgba(27, 69, 143, 0.3)'
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=[s2['Total'], s2['Wins'], s2['Starts'], s2['Win Rate'], s2['Momentum']],
                    theta=categories,
                    fill='toself',
                    name=p2,
                    line_color='#d61a21',
                    fillcolor='rgba(214, 26, 33, 0.3)'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max(s1['Total'], s2['Total'], 100)])),
                    showlegend=True,
                    height=400,
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with tab_bars:
                comp_df = pd.DataFrame([
                    {'Player': p1, 'Metric': 'Total Apps', 'Value': s1['Total']},
                    {'Player': p2, 'Metric': 'Total Apps', 'Value': s2['Total']},
                    {'Player': p1, 'Metric': 'Starts', 'Value': s1['Starts']},
                    {'Player': p2, 'Metric': 'Starts', 'Value': s2['Starts']},
                    {'Player': p1, 'Metric': 'Wins', 'Value': s1['Wins']},
                    {'Player': p2, 'Metric': 'Wins', 'Value': s2['Wins']},
                    {'Player': p1, 'Metric': 'Win Rate', 'Value': s1['Win Rate']},
                    {'Player': p2, 'Metric': 'Win Rate', 'Value': s2['Win Rate']},
                ])
                
                fig_bar = px.bar(
                    comp_df, x='Metric', y='Value', color='Player',
                    barmode='group',
                    color_discrete_map={p1:'#1b458f', p2:'#d61a21'},
                    text='Value'
                )
                fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_bar.update_layout(height=400, font=dict(family='Inter'))
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with tab_timeline:
                st.subheader("Games Played Together")
                
                # Find matches where both played
                mask1 = df_f[[f'R{i}' for i in range(1, 23)]].isin([p1]).any(axis=1)
                mask2 = df_f[[f'R{i}' for i in range(1, 23)]].isin([p2]).any(axis=1)
                together = df_f[mask1 & mask2].sort_values('Date', ascending=False)
                
                if not together.empty:
                    together_wins = len(together[together['ResultCode']=='W'])
                    together_wr = (together_wins / len(together) * 100) if len(together) > 0 else 0
                    
                    col_tog1, col_tog2, col_tog3 = st.columns(3)
                    col_tog1.metric("Games Together", len(together))
                    col_tog2.metric("Combined Win Rate", f"{together_wr:.1f}%")
                    col_tog3.metric("Wins Together", together_wins)
                    
                    st.dataframe(
                        together[['Date', 'Opponent', 'Competition', 'Score (Rangers First)', 'Win/Lose/Draw']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={"Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY")}
                    )
                else:
                    st.info(f"**{p1}** and **{p2}** have not played together yet.")

# --- NEW TEAM ANALYTICS PAGE ---
elif st.session_state['page'] == 'team':
    st.markdown("<h1>📈 TEAM ANALYTICS</h1>", unsafe_allow_html=True)
    
    if df_f.empty:
        st.info("No data available for analysis.")
    else:
        # Overall Team Stats
        total_matches = len(df_f)
        total_wins = len(df_f[df_f['ResultCode'] == 'W'])
        total_draws = len(df_f[df_f['ResultCode'] == 'D'])
        total_losses = len(df_f[df_f['ResultCode'] == 'L'])
        team_win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0
        
        st.markdown(f"<h3>📊 Overall Performance: {s_sea} • {s_comp}</h3>", unsafe_allow_html=True)
        
        kpi_t1, kpi_t2, kpi_t3, kpi_t4, kpi_t5 = st.columns(5)
        kpi_t1.metric("Total Matches", total_matches)
        kpi_t2.metric("Wins", total_wins, f"{(total_wins/total_matches*100):.1f}%")
        kpi_t3.metric("Draws", total_draws)
        kpi_t4.metric("Losses", total_losses)
        kpi_t5.metric("Win Rate", f"{team_win_rate:.1f}%")
        
        st.markdown("---")
        
        tab_overview, tab_players, tab_opponents = st.tabs(["🎯 Overview", "👥 Player Stats", "🏟️ Opponents"])
        
        with tab_overview:
            col_o1, col_o2 = st.columns(2)
            
            with col_o1:
                st.subheader("Results Distribution")
                fig_team_pie = go.Figure(data=[go.Pie(
                    labels=['Wins','Draws','Losses'],
                    values=[total_wins, total_draws, total_losses],
                    hole=.6,
                    marker=dict(colors=['#1b458f','#94a3b8','#d61a21']),
                    textinfo='label+percent+value'
                )])
                fig_team_pie.update_layout(height=300, font=dict(family='Inter'))
                st.plotly_chart(fig_team_pie, use_container_width=True)
            
            with col_o2:
                st.subheader("Performance by Competition")
                comp_perf = df_f.groupby('Competition').agg({
                    'ResultCode': ['count', lambda x: (x=='W').sum()]
                }).reset_index()
                comp_perf.columns = ['Competition', 'Matches', 'Wins']
                comp_perf['Win Rate'] = (comp_perf['Wins'] / comp_perf['Matches'] * 100).round(1)
                
                fig_comp_team = px.bar(
                    comp_perf, x='Competition', y='Win Rate',
                    text='Win Rate',
                    color='Win Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig_comp_team.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_comp_team.update_layout(height=300, showlegend=False, font=dict(family='Inter'))
                st.plotly_chart(fig_comp_team, use_container_width=True)
        
        with tab_players:
            st.subheader("Player Appearance Rankings")
            
            # Calculate player appearances
            all_players_list = []
            for col in [f'R{i}' for i in range(1, 23)]:
                all_players_list.extend(df_f[col].dropna().tolist())
            
            player_apps = pd.Series(all_players_list).value_counts().reset_index()
            player_apps.columns = ['Player', 'Appearances']
            
            # Calculate win rate for each player
            player_apps['Wins'] = player_apps['Player'].apply(
                lambda p: len(df_f[df_f[[f'R{i}' for i in range(1, 23)]].isin([p]).any(axis=1) & (df_f['ResultCode']=='W')])
            )
            player_apps['Win Rate'] = (player_apps['Wins'] / player_apps['Appearances'] * 100).round(1)
            player_apps = player_apps.sort_values('Appearances', ascending=False).head(20)
            
            fig_players = go.Figure()
            fig_players.add_trace(go.Bar(
                x=player_apps['Player'],
                y=player_apps['Appearances'],
                marker=dict(
                    color=player_apps['Win Rate'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Win %")
                ),
                text=[f"{a} apps<br>{wr:.0f}%" for a, wr in zip(player_apps['Appearances'], player_apps['Win Rate'])],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Appearances: %{y}<br>Win Rate: %{marker.color:.1f}%<extra></extra>'
            ))
            fig_players.update_layout(
                height=400,
                xaxis_title="Player",
                yaxis_title="Appearances",
                xaxis_tickangle=-45,
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_players, use_container_width=True)
        
        with tab_opponents:
            st.subheader("Head-to-Head vs Opponents")
            
            opp_stats = df_f.groupby('Opponent').agg({
                'ResultCode': ['count', lambda x: (x=='W').sum(), lambda x: (x=='D').sum(), lambda x: (x=='L').sum()]
            }).reset_index()
            opp_stats.columns = ['Opponent', 'Played', 'W', 'D', 'L']
            opp_stats['Win Rate'] = (opp_stats['W'] / opp_stats['Played'] * 100).round(1)
            opp_stats = opp_stats.sort_values('Played', ascending=False).head(15)
            
            fig_opp = go.Figure()
            fig_opp.add_trace(go.Bar(name='Wins', x=opp_stats['Opponent'], y=opp_stats['W'], marker_color='#1b458f'))
            fig_opp.add_trace(go.Bar(name='Draws', x=opp_stats['Opponent'], y=opp_stats['D'], marker_color='#94a3b8'))
            fig_opp.add_trace(go.Bar(name='Losses', x=opp_stats['Opponent'], y=opp_stats['L'], marker_color='#d61a21'))
            
            fig_opp.update_layout(
                barmode='stack',
                height=400,
                xaxis_title="Opponent",
                yaxis_title="Matches",
                xaxis_tickangle=-45,
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_opp, use_container_width=True)

# --- NEW SEASON OVERVIEW PAGE ---
elif st.session_state['page'] == 'season':
    st.markdown("<h1>🏆 SEASON OVERVIEW</h1>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No seasonal data available.")
    else:
        # Season selector
        all_seasons = sorted(df['Tag Season'].unique().tolist(), reverse=True)
        selected_season = st.selectbox("Select Season", all_seasons)
        
        season_df = df[df['Tag Season'] == selected_season]
        
        if not season_df.empty:
            # Season KPIs
            s_total = len(season_df)
            s_wins = len(season_df[season_df['ResultCode'] == 'W'])
            s_draws = len(season_df[season_df['ResultCode'] == 'D'])
            s_losses = len(season_df[season_df['ResultCode'] == 'L'])
            s_wr = (s_wins / s_total * 100) if s_total > 0 else 0
            
            st.markdown(f"<h2>Season: {selected_season}</h2>", unsafe_allow_html=True)
            
            kpi_s1, kpi_s2, kpi_s3, kpi_s4, kpi_s5 = st.columns(5)
            kpi_s1.metric("Total Matches", s_total)
            kpi_s2.metric("Wins", s_wins)
            kpi_s3.metric("Draws", s_draws)
            kpi_s4.metric("Losses", s_losses)
            kpi_s5.metric("Win Rate", f"{s_wr:.1f}%")
            
            st.markdown("---")
            
            # Season timeline
            st.subheader("Season Timeline")
            season_df_sorted = season_df.sort_values('Date')
            season_df_sorted['Match_Num'] = range(1, len(season_df_sorted) + 1)
            season_df_sorted['Points'] = season_df_sorted['ResultCode'].map({'W': 3, 'D': 1, 'L': 0})
            season_df_sorted['Cumulative_Points'] = season_df_sorted['Points'].cumsum()
            season_df_sorted['Possible_Points'] = season_df_sorted['Match_Num'] * 3
            season_df_sorted['Points_Percentage'] = (season_df_sorted['Cumulative_Points'] / season_df_sorted['Possible_Points'] * 100).round(1)
            
            fig_timeline = go.Figure()
            fig_timeline.add_trace(go.Scatter(
                x=season_df_sorted['Match_Num'],
                y=season_df_sorted['Cumulative_Points'],
                mode='lines+markers',
                name='Points',
                line=dict(color='#1b458f', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(27, 69, 143, 0.2)'
            ))
            
            fig_timeline.update_layout(
                height=350,
                xaxis_title="Match Number",
                yaxis_title="Cumulative Points",
                hovermode='x unified',
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Top performers
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.subheader("🌟 Most Appearances")
                season_players = []
                for col in [f'R{i}' for i in range(1, 23)]:
                    season_players.extend(season_df[col].dropna().tolist())
                top_apps = pd.Series(season_players).value_counts().head(10).reset_index()
                top_apps.columns = ['Player', 'Appearances']
                
                fig_top = px.bar(top_apps, x='Appearances', y='Player', orientation='h',
                                 color_discrete_sequence=['#1b458f'])
                fig_top.update_layout(height=350, yaxis={'categoryorder':'total ascending'},
                                     font=dict(family='Inter'))
                st.plotly_chart(fig_top, use_container_width=True)
            
            with col_top2:
                st.subheader("🏆 Best Win Rates (Min 5 Games)")
                top_wr_list = []
                for player in set(season_players):
                    p_mask = season_df[[f'R{i}' for i in range(1, 23)]].isin([player]).any(axis=1)
                    p_games = season_df[p_mask]
                    if len(p_games) >= 5:
                        p_wins = len(p_games[p_games['ResultCode']=='W'])
                        p_wr = (p_wins / len(p_games) * 100)
                        top_wr_list.append({'Player': player, 'Win Rate': p_wr, 'Games': len(p_games)})
                
                if top_wr_list:
                    top_wr_df = pd.DataFrame(top_wr_list).sort_values('Win Rate', ascending=False).head(10)
                    
                    fig_wr = px.bar(top_wr_df, x='Win Rate', y='Player', orientation='h',
                                    color='Win Rate', color_continuous_scale='RdYlGn')
                    fig_wr.update_layout(height=350, yaxis={'categoryorder':'total ascending'},
                                        showlegend=False, font=dict(family='Inter'))
                    st.plotly_chart(fig_wr, use_container_width=True)
                else:
                    st.info("Not enough data for win rate analysis.")

# --- ADMIN PANEL (ENHANCED) ---
elif st.session_state['page'] == 'admin':
    st.markdown("<h1>🔒 ADMIN PANEL</h1>", unsafe_allow_html=True)
    
    if check_password():
        st.success("✅ Access Granted")
        
        tab_add, tab_edit, tab_bulk = st.tabs(["➕ Add Match", "✏️ Edit Match", "📊 Bulk Operations"])
        
        with tab_add:
            st.markdown("<div class='admin-form-box'>", unsafe_allow_html=True)
            st.subheader("Add New Match")
            
            ex_opps = sorted(df['Opponent'].unique().tolist()) if not df.empty else []
            ex_comps = sorted(df['Competition'].unique().tolist()) if not df.empty else []
            ex_seas = sorted(df['Tag Season'].unique().tolist()) if not df.empty else []
            
            c1, c2, c3 = st.columns(3)
            inp_date = c1.date_input("Date", datetime.today())
            
            opp_sel = c2.selectbox("Opponent", ["Select..."] + ex_opps + ["➕ Add New"])
            inp_opp = c2.text_input("New Opponent") if opp_sel == "➕ Add New" else (opp_sel if opp_sel != "Select..." else "")
            
            comp_sel = c3.selectbox("Competition", ["Select..."] + ex_comps + ["➕ Add New"])
            inp_comp = c3.text_input("New Competition") if comp_sel == "➕ Add New" else (comp_sel if comp_sel != "Select..." else "")

            c4, c5, c6 = st.columns(3)
            inp_score = c4.text_input("Score (Rangers-Opp)", placeholder="e.g. 3-1")
            inp_res = c5.selectbox("Result", ["Win", "Draw", "Lose"])
            
            sea_sel = c6.selectbox("Season", ["Select..."] + ex_seas + ["➕ Add New"])
            inp_sea = c6.text_input("New Season") if sea_sel == "➕ Add New" else (sea_sel if sea_sel != "Select..." else "")
            
            st.markdown("---")
            
            with st.expander("🆕 Register New Player"):
                np_col1, np_col2 = st.columns([3,1])
                new_p = np_col1.text_input("Player Name", placeholder="e.g. J. Butland", label_visibility="collapsed")
                if np_col2.button("➕ Add", use_container_width=True):
                    if new_p and new_p not in players_list:
                        st.session_state['temp_new_players'].append(new_p)
                        st.success(f"Added {new_p}")
                        st.rerun()
            
            st.markdown("##### 📋 Team Sheet")
            sc1, sc2 = st.columns(2)
            selections = {}
            with sc1:
                st.caption("Starting XI (1-11)")
                for i in range(1, 12):
                    selections[f"R{i}"] = st.selectbox(f"Position {i}", [""] + players_list, key=f"r{i}")
            with sc2:
                st.caption("Substitutes (12-22)")
                for i in range(12, 23):
                    selections[f"R{i}"] = st.selectbox(f"Sub {i-11}", [""] + players_list, key=f"r{i}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("💾 Save Match", type="primary", use_container_width=True):
                if not inp_opp or not inp_score or not inp_comp or not inp_sea:
                    st.error("⚠️ Please fill in all required fields.")
                else:
                    row = {
                        'Day': inp_date.day, 'Month': inp_date.month, 'Year': inp_date.year,
                        'Opponent': inp_opp, 'Competition': inp_comp,
                        'Score (Rangers First)': inp_score, 'Win/Lose/Draw': inp_res, 'Tag Season': inp_sea
                    }
                    for k,v in selections.items():
                        row[k] = v if v else None
                    
                    df_cur = pd.read_csv(DATA_FILE) if not df.empty else pd.DataFrame()
                    df_final = pd.concat([df_cur, pd.DataFrame([row])], ignore_index=True)
                    if save_data(df_final):
                        st.success("✅ Match saved successfully!")
                        st.balloons()
                        st.session_state['temp_new_players'] = []
            
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_edit:
            st.markdown("<div class='admin-form-box'>", unsafe_allow_html=True)
            st.subheader("Edit Existing Match")
            
            if not df.empty:
                df['Label'] = df['Date'].dt.strftime('%Y-%m-%d') + " vs " + df['Opponent'] + " (" + df['Competition'] + ")"
                target = st.selectbox("🔍 Select Match to Edit", df['Label'].unique())
                
                if target:
                    orig = df[df['Label'] == target].iloc[0]
                    
                    ed1, ed2, ed3 = st.columns(3)
                    new_d = ed1.date_input("Date", orig['Date'])
                    new_o = ed2.text_input("Opponent", orig['Opponent'])
                    new_c = ed3.text_input("Competition", orig['Competition'])
                    
                    ed4, ed5, ed6 = st.columns(3)
                    new_s = ed4.text_input("Score", orig['Score (Rangers First)'])
                    new_r = ed5.selectbox("Result", ["Win", "Draw", "Lose"], 
                                         index=["Win", "Draw", "Lose"].index(orig['Win/Lose/Draw']))
                    new_sea = ed6.text_input("Season", orig['Tag Season'])
                    
                    st.markdown("---")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💾 Update Match", type="primary", use_container_width=True):
                            raw = pd.read_csv(DATA_FILE)
                            mask = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & \
                                   (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                            
                            if mask.any():
                                idx = raw[mask].index[0]
                                raw.at[idx, 'Day'] = new_d.day
                                raw.at[idx, 'Month'] = new_d.month
                                raw.at[idx, 'Year'] = new_d.year
                                raw.at[idx, 'Opponent'] = new_o
                                raw.at[idx, 'Competition'] = new_c
                                raw.at[idx, 'Score (Rangers First)'] = new_s
                                raw.at[idx, 'Win/Lose/Draw'] = new_r
                                raw.at[idx, 'Tag Season'] = new_sea
                                
                                if save_data(raw):
                                    st.success("✅ Match updated!")
                                    st.rerun()
                            else:
                                st.error("❌ Match not found")
                    
                    with col_btn2:
                        if st.button("🗑️ Delete Match", type="secondary", use_container_width=True):
                            raw = pd.read_csv(DATA_FILE)
                            mask = (raw['Day']==orig['Day']) & (raw['Month']==orig['Month']) & \
                                   (raw['Year']==orig['Year']) & (raw['Opponent']==orig['Opponent'])
                            
                            if mask.any():
                                raw = raw[~mask]
                                if save_data(raw):
                                    st.success("✅ Match deleted!")
                                    st.rerun()
            else:
                st.info("No matches to edit.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_bulk:
            st.markdown("<div class='admin-form-box'>", unsafe_allow_html=True)
            st.subheader("Bulk Operations")
            
            st.markdown("##### 📊 Database Statistics")
            if not df.empty:
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                col_stat1.metric("Total Matches", len(df))
                col_stat2.metric("Unique Players", len(players_list))
                col_stat3.metric("Seasons", len(df['Tag Season'].unique()))
                col_stat4.metric("Competitions", len(df['Competition'].unique()))
                
                st.markdown("---")
                
                # Export
                st.markdown("##### 📥 Export Data")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Database (CSV)",
                    data=csv,
                    file_name=f"rangers_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.markdown("---")
                
                # Import
                st.markdown("##### 📤 Import Data")
                st.warning("⚠️ Warning: This will replace the current database!")
                uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
                
                if uploaded_file is not None:
                    try:
                        new_df = pd.read_csv(uploaded_file)
                        st.dataframe(new_df.head(), use_container_width=True)
                        
                        if st.button("✅ Confirm Import", type="primary"):
                            if save_data(new_df):
                                st.success("✅ Data imported successfully!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading file: {e}")
                
                st.markdown("---")
                
                # Danger Zone
                st.markdown("##### 🚨 Danger Zone")
                with st.expander("⚠️ Clear All Data"):
                    st.error("This action cannot be undone!")
                    confirm_text = st.text_input("Type 'DELETE ALL' to confirm")
                    
                    if st.button("🗑️ Clear Database", type="secondary"):
                        if confirm_text == "DELETE ALL":
                            empty_df = pd.DataFrame()
                            if save_data(empty_df):
                                st.success("Database cleared.")
                                st.rerun()
                        else:
                            st.error("Confirmation text incorrect.")
            else:
                st.info("Database is empty.")
            
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 20px;'>
    <p><strong>Ibrox Analytics Pro</strong> • Advanced Performance Intelligence System</p>
    <p style='font-size: 0.8rem;'>Built with ❤️ for Rangers FC • Version 2.0</p>
</div>
""", unsafe_allow_html=True)
