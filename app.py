import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Global Voyage Commander",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (THEME PROOF) ---
# This forces "Business Light" mode even if your computer is in Dark Mode
st.markdown("""
    <style>
    /* Force Background to Light Grey */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    /* Force Sidebar to White */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    /* FORCE ALL TEXT TO DARK NAVY (Fixes the invisible text issue) */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #0f2537 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Fix Metric Values */
    div[data-testid="stMetricValue"] {
        color: #004e89 !important;
    }
    /* Fix Metric Labels */
    div[data-testid="stMetricLabel"] > label {
        color: #555 !important;
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
    # Simplified Logic for Demo
    base_map = {
        frozenset(['Asia', 'EU']): 8500,
        frozenset(['Asia', 'US']): 5800,
        frozenset(['EU', 'US']): 3500,
        frozenset(['India', 'EU']): 6500,
        frozenset(['India', 'Asia']): 2500,
        frozenset(['India', 'ME']): 1200,
        frozenset(['ME', 'EU']): 6000,
        frozenset(['Africa', 'Asia']): 5000,
    }
    r1, r2 = PORTS_DB[p1]['Region'], PORTS_DB[p2]['Region']
    if p1 == p2: return 0
    if r1 == r2: return 1200 
    key = frozenset([r1, r2])
    return base_map.get(key, 7000) + random.randint(-50, 50)

def find_best_hub(origin, dest):
    potential_hubs = [p for p, data in PORTS_DB.items() if data['IsHub'] and p != origin and p != dest]
    if not potential_hubs: return None
    return random.choice(potential_hubs)

# --- SIDEBAR ---
st.sidebar.title("Voyage Configuration")
sorted_ports = sorted(list(PORTS_DB.keys()))
origin_port = st.sidebar.selectbox("Origin Port", sorted_ports, index=sorted_ports.index('Mumbai JNPT (IN)'))
dest_port = st.sidebar.selectbox("Destination Port", sorted_ports, index=sorted_ports.index('Rotterdam (NL)'))
st.sidebar.markdown("---")
cargo_size = st.sidebar.number_input("Cargo (mt)", value=55000, step=1000)
freight_rate = st.sidebar.number_input("Freight Rate ($/mt)", value=45.0, step=0.5)
base_speed = st.sidebar.slider("Design Speed (kts)", 10.0, 18.0, 14.0)

# --- MAIN ENGINE ---
st.title("Global Voyage Commander")
st.markdown("### Logistics Optimization & Multimodal Analysis")

if origin_port == dest_port:
    st.error("⚠️ Invalid Route: Origin and Destination are identical.")
    st.stop()

# 1. BASELINE CALCULATIONS
dist_direct = get_distance_engine(origin_port, dest_port)
days_direct = dist_direct / (base_speed * 24)
revenue = cargo_size * freight_rate

# 2. STRATEGY GENERATION
strategies = []
OPEX_DAILY = 8500 
CARBON_TAX_PRICE = 95 
FACTOR_VLSFO = 3.151

# A. Standard Strategies
scenarios = [
    {"Name": "Direct (Standard)", "Speed": 14.0, "Fuel": "VLSFO", "Bio": False, "Type": "Direct"},
    {"Name": "Direct (Eco-Steam)", "Speed": 11.0, "Fuel": "VLSFO", "Bio": False, "Type": "Direct"},
    {"Name": "Direct (Green Bio)", "Speed": 13.0, "Fuel": "Bio-B30", "Bio": True, "Type": "Direct"}
]

# B. Add Multimodal/Re-export Strategy
hub_port = find_best_hub(origin_port, dest_port)
if hub_port:
    scenarios.append({
        "Name": f"Re-export via {hub_port.split(' ')[0]}", 
        "Speed": 14.5,
        "Fuel": "VLSFO", 
        "Bio": False, 
        "Type": "Multimodal",
        "Hub": hub_port
    })

for sc in scenarios:
    s_speed = sc['Speed']
    
    if sc['Type'] == 'Direct':
        dist = dist_direct
        port_days = 3
        fuel_price = PORTS_DB[dest_port]['Price']
        tax_reduction = 0
        handling_fee = 0
    else:
        dist1 = get_distance_engine(origin_port, sc['Hub'])
        dist2 = get_distance_engine(sc['Hub'], dest_port)
        dist = dist1 + dist2
        port_days = 6 
        fuel_price = PORTS_DB[sc['Hub']]['Price'] 
        tax_reduction = 0.30 
        handling_fee = 45000 
    
    if sc['Bio']: fuel_price *= 1.4

    s_days = dist / (s_speed * 24)
    total_days = s_days + port_days
    
    base_cons = 45 
    daily_cons = base_cons * ((s_speed / 14.0) ** 3)
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
        "Net Profit": profit,
        "TCE": tce,
        "Tax Cost": final_tax,
        "Total Cost": total_cost,
        "Details": "Transshipment" if sc['Type'] == "Multimodal" else "Direct Sea"
    })

df_strat = pd.DataFrame(strategies).sort_values(by="Net Profit", ascending=False)
best_strat = df_strat.iloc[0]

# --- 3. METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Direct Distance", f"{dist_direct:,.0f} nm")
m2.metric("Market Freight", f"${freight_rate:.2f}/mt")
m3.metric("Est. Revenue", f"${revenue:,.0f}")
m4.metric("Best Profit", f"${best_strat['Net Profit']:,.0f}", delta=best_strat['Strategy'])

st.divider()

# --- 4. VISUALIZATION & AI ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Financial Comparison")
    
    # Custom Color mapping
    color_map = {
        "Direct (Standard)": "#2F4858", 
        "Direct (Eco-Steam)": "#004e89",
        "Direct (Green Bio)": "#00CC96",
    }
    for s in strategies:
        if "Re-export" in s['Strategy']: color_map[s['Strategy']] = "#FF6B6B"

    fig = px.bar(df_strat, x="Strategy", y="Net Profit", 
                 title="Net Profit by Strategy (After Tax & Opex)",
                 color="Strategy", color_discrete_map=color_map,
                 text_auto='.2s',
                 template="plotly_white") # FORCES LIGHT THEME ON CHART
    
    fig.update_layout(height=350, showlegend=False, 
                      margin=dict(l=20, r=20, t=40, b=20),
                      plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("AI Strategic Advice")
    
    top_strat = best_strat['Strategy']
    
    if "Re-export" in top_strat:
        hub_name = top_strat.split("via ")[1]
        st.success(f"**RECOMMENDATION: MULTIMODAL / RE-EXPORT**")
        st.markdown(f"""
        **Route:** Origin ➔ **{hub_name}** ➔ Destination
        
        **Why it wins:**
        1. **Better Trade Agreement:** Utilizing {hub_name} as a re-export hub reduced regulatory tax exposure by 30%.
        2. **Fuel Arbitrage:** Bunkering at {hub_name} was cheaper than the destination price.
        """)
    elif "Eco-Steam" in top_strat:
        st.info("**RECOMMENDATION: SLOW STEAMING**")
        st.write("Current market rates do not justify high fuel consumption. Slow down to 11 knots to maximize TCE.")
    else:
        st.write(f"**Recommendation: {top_strat}**")
        st.write("Direct route at standard speed offers the best turnover.")

    st.metric("Profit Uplift", f"+${(df_strat.iloc[0]['Net Profit'] - df_strat.iloc[1]['Net Profit']):,.0f}", "vs next best option")

# --- 5. DETAILED TABLE ---
st.subheader("Scenario Analysis Data")
# Removed .background_gradient to fix the "requires matplotlib" error
st.dataframe(
    df_strat[['Strategy', 'Details', 'Net Profit', 'TCE', 'Tax Cost', 'Total Cost']]
    .style.format({
        "Net Profit": "${:,.0f}", 
        "TCE": "${:,.0f}", 
        "Tax Cost": "${:,.0f}", 
        "Total Cost": "${:,.0f}"
    }),
    use_container_width=True
)
