import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="Global Voyage Commander", layout="wide")

# --- 1. THE TOP 40 PORT DATABASE (Simulated Live Snapshot) ---
# Prices = Approx VLSFO $/mt (2025 estimates) | Dev_Cost = Deviation penalty
PORTS_DB = {
    # --- ASIA GIANTS ---
    'Shanghai (CN)':       {'Region': 'Asia', 'Price': 610, 'Lat': 31.23, 'Lon': 121.47},
    'Singapore (SG)':      {'Region': 'Asia', 'Price': 620, 'Lat': 1.29,  'Lon': 103.85},
    'Ningbo-Zhoushan (CN)':{'Region': 'Asia', 'Price': 605, 'Lat': 29.88, 'Lon': 121.64},
    'Shenzhen (CN)':       {'Region': 'Asia', 'Price': 615, 'Lat': 22.54, 'Lon': 114.05},
    'Guangzhou (CN)':      {'Region': 'Asia', 'Price': 625, 'Lat': 23.12, 'Lon': 113.26},
    'Busan (KR)':          {'Region': 'Asia', 'Price': 640, 'Lat': 35.10, 'Lon': 129.04},
    'Qingdao (CN)':        {'Region': 'Asia', 'Price': 612, 'Lat': 36.06, 'Lon': 120.38},
    'Hong Kong (HK)':      {'Region': 'Asia', 'Price': 630, 'Lat': 22.31, 'Lon': 114.16},
    'Tianjin (CN)':        {'Region': 'Asia', 'Price': 620, 'Lat': 38.99, 'Lon': 117.71},
    'Port Klang (MY)':     {'Region': 'Asia', 'Price': 635, 'Lat': 3.00,  'Lon': 101.40},
    'Kaohsiung (TW)':      {'Region': 'Asia', 'Price': 645, 'Lat': 22.62, 'Lon': 120.28},
    'Tokyo (JP)':          {'Region': 'Asia', 'Price': 660, 'Lat': 35.68, 'Lon': 139.76},
    'Laem Chabang (TH)':   {'Region': 'Asia', 'Price': 650, 'Lat': 13.08, 'Lon': 100.91},
    
    # --- INDIA & MIDDLE EAST ---
    'Mundra (IN)':         {'Region': 'India', 'Price': 660, 'Lat': 22.84, 'Lon': 69.70},
    'Mumbai JNPT (IN)':    {'Region': 'India', 'Price': 665, 'Lat': 18.95, 'Lon': 72.95},
    'Chennai (IN)':        {'Region': 'India', 'Price': 680, 'Lat': 13.08, 'Lon': 80.29},
    'Cochin (IN)':         {'Region': 'India', 'Price': 675, 'Lat': 9.96,  'Lon': 76.24},
    'Visakhapatnam (IN)':  {'Region': 'India', 'Price': 685, 'Lat': 17.69, 'Lon': 83.29},
    'Kolkata (IN)':        {'Region': 'India', 'Price': 700, 'Lat': 22.54, 'Lon': 88.33},
    'Fujairah (UAE)':      {'Region': 'ME',    'Price': 600, 'Lat': 25.11, 'Lon': 56.32}, # Major Hub
    'Jebel Ali (UAE)':     {'Region': 'ME',    'Price': 610, 'Lat': 24.98, 'Lon': 55.07},
    'Salalah (OM)':        {'Region': 'ME',    'Price': 630, 'Lat': 16.94, 'Lon': 54.00},
    
    # --- EUROPE ---
    'Rotterdam (NL)':      {'Region': 'EU', 'Price': 595, 'Lat': 51.92, 'Lon': 4.47},
    'Antwerp (BE)':        {'Region': 'EU', 'Price': 600, 'Lat': 51.22, 'Lon': 4.40},
    'Hamburg (DE)':        {'Region': 'EU', 'Price': 610, 'Lat': 53.54, 'Lon': 9.98},
    'Algeciras (ES)':      {'Region': 'EU', 'Price': 620, 'Lat': 36.14, 'Lon': -5.45},
    'Valencia (ES)':       {'Region': 'EU', 'Price': 625, 'Lat': 39.46, 'Lon': -0.37},
    'Piraeus (GR)':        {'Region': 'EU', 'Price': 640, 'Lat': 37.94, 'Lon': 23.64},
    'Gibraltar (UK)':      {'Region': 'EU', 'Price': 635, 'Lat': 36.14, 'Lon': -5.35},
    
    # --- AMERICAS ---
    'Los Angeles (US)':    {'Region': 'US', 'Price': 650, 'Lat': 33.72, 'Lon': -118.27},
    'Long Beach (US)':     {'Region': 'US', 'Price': 655, 'Lat': 33.76, 'Lon': -118.19},
    'New York/NJ (US)':    {'Region': 'US', 'Price': 640, 'Lat': 40.66, 'Lon': -74.02},
    'Houston (US)':        {'Region': 'US', 'Price': 580, 'Lat': 29.76, 'Lon': -95.36}, # Cheap Fuel
    'Savannah (US)':       {'Region': 'US', 'Price': 660, 'Lat': 32.08, 'Lon': -81.09},
    'Santos (BR)':         {'Region': 'SA', 'Price': 690, 'Lat': -23.96, 'Lon': -46.33},
    'Panama Canal (PA)':   {'Region': 'SA', 'Price': 645, 'Lat': 9.08,  'Lon': -79.68},
    
    # --- AFRICA/OTHERS ---
    'Tanger Med (MA)':     {'Region': 'Africa', 'Price': 630, 'Lat': 35.88, 'Lon': -5.50},
    'Durban (ZA)':         {'Region': 'Africa', 'Price': 690, 'Lat': -29.88, 'Lon': 31.02},
    'Port Said (EG)':      {'Region': 'Africa', 'Price': 650, 'Lat': 31.26, 'Lon': 32.30},
}

# --- 2. SMART DISTANCE ENGINE ---
# Instead of hardcoding 1600 routes, we map regions and add logical distances
# This acts as a "Mock API" for the demo
def get_distance(p1, p2):
    # Simplified lookup for major trade lanes
    # Key = (Region A, Region B)
    base_distances = {
        ('Asia', 'EU'): 8500,    ('EU', 'Asia'): 8500,
        ('Asia', 'US'): 5800,    ('US', 'Asia'): 5800,
        ('EU', 'US'): 3500,      ('US', 'EU'): 3500,
        ('India', 'EU'): 6500,   ('EU', 'India'): 6500,
        ('India', 'Asia'): 2500, ('Asia', 'India'): 2500,
        ('India', 'ME'): 1200,   ('ME', 'India'): 1200,
        ('ME', 'EU'): 6000,      ('EU', 'ME'): 6000,
        ('Africa', 'Asia'): 5000,('Asia', 'Africa'): 5000,
    }
    
    r1 = PORTS_DB[p1]['Region']
    r2 = PORTS_DB[p2]['Region']
    
    if p1 == p2: return 0
    if r1 == r2: return 1200 # Intra-region average
    
    # Return base distance + random variation to make it look realistic per port
    base = base_distances.get((r1, r2)) or 7000 # Default if unknown
    return base + random.randint(-200, 200)

# --- SIDEBAR ---
st.sidebar.header("🕹️ Mission Control")

# Sort ports alphabetically for the dropdown
sorted_ports = sorted(list(PORTS_DB.keys()))
origin_port = st.sidebar.selectbox("🚩 Origin Port", sorted_ports, index=sorted_ports.index('Mumbai JNPT (IN)'))
dest_port = st.sidebar.selectbox("🏁 Destination Port", sorted_ports, index=sorted_ports.index('Rotterdam (NL)'))

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Vessel Specs")
cargo_size = st.sidebar.number_input("Cargo (mt)", value=55000)
freight_rate = st.sidebar.number_input("Freight Rate ($/mt)", value=45.0)
base_speed = st.sidebar.slider("Cruising Speed (kts)", 10.0, 18.0, 14.0)

# Constants
OPEX_DAILY = 8500 
CARBON_TAX_PRICE = 95 # EU ETS Price
FACTOR_VLSFO = 3.151

# --- MAIN APP ---
st.title("⚓ Global Voyage Commander")
st.markdown("### Top 40 Port Intelligence & Route Optimization")

# 1. LIVE ROUTE DATA
dist_nm = get_distance(origin_port, dest_port)
days_at_sea = dist_nm / (base_speed * 24)
revenue = cargo_size * freight_rate

# Top Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Route Distance", f"{dist_nm:,.0f} nm")
m2.metric("Est. Duration", f"{days_at_sea:.1f} days")
m3.metric("Projected Revenue", f"${revenue:,.0f}")
m4.metric("EU Carbon Price", f"${CARBON_TAX_PRICE}/mt")

st.divider()

# --- 2. THE OPTIMIZER ENGINE ---
# We calculate 3 Strategies: Standard, Eco-Steaming, and "Green Premium"
strategies = []

scenarios = [
    {"Name": "Standard Speed (14kts)", "Speed": 14.0, "Fuel": "VLSFO", "Bio": False},
    {"Name": "Eco-Steaming (11kts)",   "Speed": 11.0, "Fuel": "VLSFO", "Bio": False},
    {"Name": "Green Corridor (Bio)",   "Speed": 13.0, "Fuel": "Bio-B30", "Bio": True}
]

for sc in scenarios:
    s_speed = sc['Speed']
    s_days = dist_nm / (s_speed * 24)
    total_days = s_days + 3 # Port turnaround
    
    # Fuel Model (Cubic Law)
    base_cons = 45 # mt/day at 14 knots
    daily_cons = base_cons * ((s_speed / 14.0) ** 3)
    total_fuel = s_days * daily_cons
    
    # Price Logic (Destination Price used as Proxy)
    fuel_price = PORTS_DB[dest_port]['Price']
    if sc['Bio']: fuel_price *= 1.4 # 40% Premium for Biofuel
    
    fuel_cost = total_fuel * fuel_price
    opex_cost = total_days * OPEX_DAILY
    
    # Carbon Tax Logic
    emissions = total_fuel * FACTOR_VLSFO
    if sc['Bio']: emissions *= 0.7 # 30% reduction for B30 blend
    
    # Tax applies if touching EU ports
    is_eu_route = 'EU' in [PORTS_DB[origin_port]['Region'], PORTS_DB[dest_port]['Region']]
    tax_cost = (emissions * CARBON_TAX_PRICE) if is_eu_route else 0
    
    total_cost = fuel_cost + opex_cost + tax_cost
    profit = revenue - total_cost
    tce = profit / total_days
    
    # CII Logic
    cii_score = (emissions * 1e6) / (cargo_size * dist_nm)
    grade = 'A' if cii_score < 5 else 'C' if cii_score < 7 else 'E'
    
    strategies.append({
        "Strategy": sc['Name'],
        "Speed": s_speed,
        "Net Profit": profit,
        "TCE ($/day)": tce,
        "Total Cost": total_cost,
        "Carbon Tax": tax_cost,
        "CII Grade": grade,
        "Emissions (mt)": emissions
    })

df_strat = pd.DataFrame(strategies).sort_values(by="Net Profit", ascending=False)
best_strat = df_strat.iloc[0]

# --- 3. VISUALIZATION CENTER ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Financial Performance Comparison")
    fig = px.bar(df_strat, x="Strategy", y=["Net Profit", "Carbon Tax"], 
                 title="Profit vs. Regulatory Cost",
                 color_discrete_map={"Net Profit": "#00CC96", "Carbon Tax": "#EF553B"},
                 text_auto='.2s')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🤖 AI Recommendation")
    
    if best_strat['Strategy'] == "Eco-Steaming (11kts)":
        st.success("Recommendation: **SLOW DOWN**")
        st.write("Slowing to 11 knots saves significantly on fuel & tax, outweighing the extra days.")
    else:
        st.info(f"Recommendation: **{best_strat['Strategy']}**")
        st.write("Current market conditions favor maintaining speed for higher TCE turnover.")
        
    st.metric("Optimal TCE", f"${best_strat['TCE ($/day)']:,.0f} / day")
    
    with st.expander("Show Compliance (CII)"):
        for i, row in df_strat.iterrows():
            color = "green" if row['CII Grade'] == 'A' else "red"
            st.markdown(f"**{row['Strategy']}**: :{color}[Grade {row['CII Grade']}]")

# --- 4. DATA TABLE ---
st.markdown("### 📋 Detailed Voyage P&L")
st.dataframe(
    df_strat[['Strategy', 'Speed', 'Net Profit', 'TCE ($/day)', 'Carbon Tax', 'CII Grade', 'Emissions (mt)']]
    .style.format({"Net Profit": "${:,.0f}", "TCE ($/day)": "${:,.0f}", "Carbon Tax": "${:,.0f}", "Emissions (mt)": "{:,.0f}"}),
    use_container_width=True
)

st.sidebar.info("Data Sources: Simulated snapshot based on 2025 Global Top 40 Rankings & VLSFO Averages.")
