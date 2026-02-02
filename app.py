import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="Global Voyage Commander", layout="wide")

# --- CUSTOM CSS FOR DARK AESTHETIC ---
st.markdown("""
    <style>
    /* Dark Theme Tweaks */
    .stApp {
        background-color: #0E1117;
    }
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        color: #00CC96; /* Green Neon */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #888;
    }
    /* Custom Box for Alternative */
    .alt-box {
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        background-color: #191c24;
        margin-top: 10px;
    }
    .alt-title {
        color: #FFA15A;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .alt-text {
        color: #ccc;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA ASSETS ---
PORTS_DB = {
    # --- ASIA ---
    'Shanghai (CN)':       {'Region': 'Asia', 'Price': 610, 'IsHub': False},
    'Singapore (SG)':      {'Region': 'Asia', 'Price': 620, 'IsHub': True},
    'Ningbo-Zhoushan (CN)':{'Region': 'Asia', 'Price': 605, 'IsHub': False},
    'Shenzhen (CN)':       {'Region': 'Asia', 'Price': 615, 'IsHub': False},
    'Busan (KR)':          {'Region': 'Asia', 'Price': 640, 'IsHub': True},
    'Hong Kong (HK)':      {'Region': 'Asia', 'Price': 630, 'IsHub': True},
    'Tokyo (JP)':          {'Region': 'Asia', 'Price': 660, 'IsHub': False},
    
    # --- INDIA & MIDDLE EAST ---
    'Mumbai JNPT (IN)':    {'Region': 'India', 'Price': 665, 'IsHub': False},
    'Mundra (IN)':         {'Region': 'India', 'Price': 660, 'IsHub': False},
    'Fujairah (UAE)':      {'Region': 'ME',    'Price': 590, 'IsHub': True},
    'Jebel Ali (UAE)':     {'Region': 'ME',    'Price': 610, 'IsHub': True},
    'Salalah (OM)':        {'Region': 'ME',    'Price': 630, 'IsHub': True},

    # --- EUROPE ---
    'Rotterdam (NL)':      {'Region': 'EU', 'Price': 595, 'IsHub': True},
    'Antwerp (BE)':        {'Region': 'EU', 'Price': 600, 'IsHub': True},
    'Algeciras (ES)':      {'Region': 'EU', 'Price': 620, 'IsHub': True},
    'Piraeus (GR)':        {'Region': 'EU', 'Price': 640, 'IsHub': False},
    
    # --- AMERICAS ---
    'Los Angeles (US)':    {'Region': 'US', 'Price': 650, 'IsHub': False},
    'New York/NJ (US)':    {'Region': 'US', 'Price': 640, 'IsHub': False},
    'Houston (US)':        {'Region': 'US', 'Price': 580, 'IsHub': True},
    'Panama Canal (PA)':   {'Region': 'SA', 'Price': 645, 'IsHub': True},
    
    # --- AFRICA ---
    'Tanger Med (MA)':     {'Region': 'Africa', 'Price': 630, 'IsHub': True},
    'Durban (ZA)':         {'Region': 'Africa', 'Price': 690, 'IsHub': False},
}

def get_distance_engine(p1, p2):
    base_map = {
        frozenset(['Asia', 'EU']): 8500, frozenset(['Asia', 'US']): 5800,
        frozenset(['EU', 'US']): 3500, frozenset(['India', 'EU']): 6500,
        frozenset(['India', 'Asia']): 2500, frozenset(['ME', 'EU']): 6000
    }
    r1, r2 = PORTS_DB[p1]['Region'], PORTS_DB[p2]['Region']
    if p1 == p2: return 0
    if r1 == r2: return 1200 
    return base_map.get(frozenset([r1, r2]), 7000) + random.randint(-50, 50)

def find_best_hub(origin, dest):
    potential_hubs = [p for p, data in PORTS_DB.items() if data['IsHub'] and p != origin and p != dest]
    return random.choice(potential_hubs) if potential_hubs else None

# --- SIDEBAR ---
st.sidebar.header("🕹️ Mission Control")
sorted_ports = sorted(list(PORTS_DB.keys()))
origin_port = st.sidebar.selectbox("🚩 Origin Port", sorted_ports, index=sorted_ports.index('Mumbai JNPT (IN)'))
dest_port = st.sidebar.selectbox("🏁 Destination Port", sorted_ports, index=sorted_ports.index('Rotterdam (NL)'))

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Vessel Specs")
cargo_size = st.sidebar.number_input("Cargo (mt)", value=55000, step=1000)
freight_rate = st.sidebar.number_input("Freight Rate ($/mt)", value=45.0, step=0.5)
base_speed = st.sidebar.slider("Cruising Speed (kts)", 10.0, 18.0, 14.0)

# --- MAIN APP ---
st.title("⚓ Global Voyage Commander")
st.markdown("### Top 40 Port Intelligence & Route Optimization")

if origin_port == dest_port:
    st.error("⚠️ Origin and Destination cannot be the same.")
    st.stop()

# 1. LIVE ROUTE DATA
dist_direct = get_distance_engine(origin_port, dest_port)
revenue = cargo_size * freight_rate
OPEX_DAILY = 8500 
CARBON_TAX_PRICE = 95 
FACTOR_VLSFO = 3.151

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Route Distance", f"{dist_direct:,.0f} nm")
m2.metric("Market Rate", f"${freight_rate:.2f}/mt")
m3.metric("Projected Revenue", f"${revenue:,.0f}")
m4.metric("Carbon Price", f"${CARBON_TAX_PRICE}/mt")

st.divider()

# --- 2. THE OPTIMIZER ENGINE ---
strategies = []

# Dynamic Logic
eco_speed_target = 11.0 if base_speed > 11.0 else 10.0

scenarios = [
    {"Name": f"Selected Speed ({base_speed}kts)", "Speed": float(base_speed), "Fuel": "VLSFO", "Bio": False, "Type": "Direct"},
    {"Name": f"Eco-Steaming ({eco_speed_target}kts)", "Speed": eco_speed_target, "Fuel": "VLSFO", "Bio": False, "Type": "Direct"},
    {"Name": "Green Corridor (Bio)", "Speed": 13.0, "Fuel": "Bio-B30", "Bio": True, "Type": "Direct"}
]

# Multimodal Logic
hub_port = find_best_hub(origin_port, dest_port)
has_multimodal = False
if hub_port:
    has_multimodal = True
    scenarios.append({
        "Name": f"Re-export via {hub_port.split(' ')[0]}", 
        "Speed": 14.5, "Fuel": "VLSFO", "Bio": False, "Type": "Multimodal", "Hub": hub_port
    })

for sc in scenarios:
    s_speed = sc['Speed']
    
    if sc['Type'] == 'Direct':
        dist = dist_direct
        port_days = 3
        fuel_price = PORTS_DB[dest_port]['Price']
        tax_reduction, handling_fee = 0, 0
    else:
        dist = get_distance_engine(origin_port, sc['Hub']) + get_distance_engine(sc['Hub'], dest_port)
        port_days = 6 
        fuel_price = PORTS_DB[sc['Hub']]['Price'] 
        tax_reduction, handling_fee = 0.30, 45000 
    
    if sc['Bio']: fuel_price *= 1.4

    s_days = dist / (s_speed * 24)
    total_days = s_days + port_days
    
    daily_cons = 45 * ((s_speed / 14.0) ** 3) # Cubic Law
    total_fuel = s_days * daily_cons
    
    fuel_cost = total_fuel * fuel_price
    opex_cost = total_days * OPEX_DAILY
    
    emissions = total_fuel * FACTOR_VLSFO
    if sc['Bio']: emissions *= 0.7
    
    is_eu_route = 'EU' in [PORTS_DB[origin_port]['Region'], PORTS_DB[dest_port]['Region']]
    raw_tax = (emissions * CARBON_TAX_PRICE) if is_eu_route else 0
    final_tax = raw_tax * (1 - tax_reduction)
    
    total_cost = fuel_cost + opex_cost + final_tax + handling_fee
    profit = revenue - total_cost
    tce = profit / total_days
    
    strategies.append({
        "Strategy": sc['Name'],
        "Speed": s_speed,
        "Net Profit": profit,
        "TCE": tce,
        "Total Cost": total_cost,
        "Carbon Tax": final_tax,
        "Type": sc['Type'],
        "Details": "Transshipment" if sc['Type'] == "Multimodal" else "Direct Sea"
    })

df_strat = pd.DataFrame(strategies).sort_values(by="Net Profit", ascending=False)
best_strat = df_strat.iloc[0]

# Identify the "Alternative"
# If winner is Multimodal, alt is Direct. If winner is Direct, alt is Multimodal (if exists).
alternative_strat = None
if best_strat['Type'] == 'Multimodal':
    # Find best Direct
    alternative_strat = df_strat[df_strat['Type'] == 'Direct'].iloc[0]
elif has_multimodal:
    # Find Multimodal
    alternative_strat = df_strat[df_strat['Type'] == 'Multimodal'].iloc[0]
else:
    # Just the runner up
    alternative_strat = df_strat.iloc[1]

# --- 3. VISUALIZATION CENTER ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Financial Performance Comparison")
    
    # Clean Color Scheme
    color_map = {
        f"Selected Speed ({base_speed}kts)": "#00CC96", # Greenish/Teal
        f"Eco-Steaming ({eco_speed_target}kts)": "#636EFA", # Purple/Blue
        "Green Corridor (Bio)": "#EF553B" # Red/Orange
    }
    for s in strategies:
        if "Re-export" in s['Strategy']: color_map[s['Strategy']] = "#FFA15A" # Orange

    fig = px.bar(df_strat, x="Strategy", y="Net Profit", 
                 color="Strategy", 
                 color_discrete_map=color_map,
                 text_auto='.2s')
    
    # SLIM & CLEAN GRAPH
    fig.update_layout(
        height=280, # Slimmer
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title=None, # Remove "Strategy" text
        yaxis_title="Net Profit ($)",
        showlegend=False, # Remove Legend (Redundant with Axis)
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc')
    )
    # Customize Hover
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>')
    
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🤖 AI Recommendation")
    
    top_strat_name = best_strat['Strategy']
    speed_diff = best_strat['Speed'] - base_speed
    
    # Recommendation Logic
    rec_title = ""
    rec_text = ""
    
    if "Re-export" in top_strat_name:
        rec_title = "GO MULTIMODAL"
        hub_name = top_strat_name.split("via ")[1]
        rec_text = f"Route via **{hub_name}**. Tax & Fuel savings outweigh handling costs."
    elif abs(speed_diff) < 0.5:
        rec_title = "MAINTAIN SPEED"
        rec_text = f"Your input of **{base_speed} kts** is optimal."
    elif speed_diff < 0:
        rec_title = "SLOW DOWN"
        rec_text = f"Reduce to **{best_strat['Speed']} kts** to save fuel."
    else:
        rec_title = "SPEED UP"
        rec_text = f"Increase to **{best_strat['Speed']} kts** for higher turnover."

    st.success(f"**STRATEGY: {rec_title}**")
    st.write(rec_text)
    st.metric("Optimal TCE", f"${best_strat['TCE']:,.0f} / day")

    # --- BEST ALTERNATIVE BOX ---
    if alternative_strat is not None:
        diff_profit = best_strat['Net Profit'] - alternative_strat['Net Profit']
        st.markdown(f"""
        <div class="alt-box">
            <div class="alt-title">🔄 Best Alternative Route</div>
            <div class="alt-text"><b>{alternative_strat['Strategy']}</b></div>
            <div style="font-size: 12px; color: #888; margin-top:5px;">
                Profit Gap: -${diff_profit:,.0f} vs Winner
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 4. DATA TABLE ---
st.markdown("### 📋 Detailed Voyage P&L")
st.dataframe(
    df_strat[['Strategy', 'Speed', 'Net Profit', 'TCE', 'Carbon Tax', 'Total Cost']]
    .style.format({
        "Speed": "{:.1f} kts",
        "Net Profit": "${:,.0f}", 
        "TCE": "${:,.0f}", 
        "Carbon Tax": "${:,.0f}", 
        "Total Cost": "${:,.0f}"
    }),
    use_container_width=True
)
