# app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(layout="wide", page_title="DNA Platform - Maharashtra MVP")

st.title("🧬 DNA - Distributor Network Analysis")
st.subheader("State Focus: Maharashtra (PoC Prototype)")

# --- Data Loading ---
@st.cache_data
def load_data():
    internal = pd.read_csv("data/internal_touchpoints.csv")
    customers = pd.read_csv("data/customer_touchpoints.csv")
    history = pd.read_csv("data/historical_performance.csv")
    
    # Safely load proposals if the ML script has been run
    if os.path.exists("data/proposed_ro_locations.csv"):
        proposals = pd.read_csv("data/proposed_ro_locations.csv")
    else:
        proposals = pd.DataFrame() # Empty dataframe fallback
        
    return internal, customers, history, proposals

@st.cache_data
def load_geo_data():
    territories = gpd.read_file("data/territory_boundaries.geojson")
    state_border = gpd.read_file("data/maharashtra_border.geojson")
    return territories, state_border

internal_df, customer_df, history_df, proposals_df = load_data()
territories_gdf, state_border_gdf = load_geo_data()

# --- Layout ---
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📊 Network Overview")
    st.metric("Internal Touchpoints (i.e. MW, AW, RO, Dealer)", len(internal_df))
    st.metric("Total Customer Locations", len(customer_df))
    
    total_rev = history_df["Revenue_INR"].sum() / 10000000 
    st.metric("Total Historical Revenue", f"₹{total_rev:.2f} Cr")
    
    st.markdown("---")
    st.markdown("### 🗺️ Map Controls")
    show_territories = st.checkbox("Show Territory Boundaries", value=True)
    show_internal = st.checkbox("Show Internal Touchpoints", value=True)
    show_customers = st.checkbox("Show Customer Network", value=False) 
    
    # Only show the ML toggle if the data exists
    if not proposals_df.empty:
        st.markdown("### 🤖 ML Insights")
        show_proposals = st.checkbox("✨ Show Proposed RO Locations", value=True)
    else:
        show_proposals = False

with col2:
    # Initialize Map
    m = folium.Map(location=[19.0, 75.5], zoom_start=7, tiles="CartoDB positron")
    
    # 1. State Border
    folium.GeoJson(
        state_border_gdf,
        name="Maharashtra Border",
        style_function=lambda feature: {"color": "black", "weight": 4, "fillOpacity": 0}
    ).add_to(m)
    
    # 2. Territory Polygons
    if show_territories:
        folium.GeoJson(
            territories_gdf,
            name="Territories",
            style_function=lambda feature: {"fillColor": "#3186cc", "color": "black", "weight": 1, "fillOpacity": 0.2},
            tooltip=folium.GeoJsonTooltip(fields=["ID", "Type", "Hub"])
        ).add_to(m)

    # 3. Customer Network
    if show_customers:
        for _, row in customer_df.sample(min(500, len(customer_df)), random_state=42).iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=2, color="orange", fill=True, fill_opacity=0.6,
                popup=f"{row['Type']} ({row['ID']})"
            ).add_to(m)

    # 4. Internal Touchpoints
    if show_internal:
        for _, row in internal_df.iterrows():
            if row["Type"] == "Mother Warehouse (MW)":
                marker_color = "darkred"
            elif row["Type"] == "Additional Warehouse (AW)":
                marker_color = "orange"
            elif row["Type"] == "Retail Office (RO)":
                marker_color = "green"
            else:
                marker_color = "blue"
                
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                icon=folium.Icon(color=marker_color, icon="info-sign"),
                popup=f"<b>{row['Type']}</b><br>{row['ID']}"
            ).add_to(m)

    # 5. ML Proposed RO Locations (The Red Stars)
    if show_proposals and not proposals_df.empty:
        for _, row in proposals_df.iterrows():
            folium.Marker(
                location=[row["Proposed_RO_Lat"], row["Proposed_RO_Lon"]],
                icon=folium.Icon(color="purple", icon="star"),
                popup=f"<b>✨ ML Proposed RO</b><br>Target Workshop Capacity: {row['Target_Customers']}"
            ).add_to(m)

    # 6. Custom Map Legend (Updated)
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 230px; height: 180px; 
         background-color: white; z-index:9999; font-size:14px;
         border:2px solid grey; border-radius:5px; padding: 10px;">
         <b>Touchpoint Legend</b><br>
         <i class="fa fa-map-marker" style="color:darkred"></i> Mother Warehouse (MW)<br>
         <i class="fa fa-map-marker" style="color:orange"></i> Addl. Warehouse (AW)<br>
         <i class="fa fa-map-marker" style="color:green"></i> Retail Office (RO)<br>
         <i class="fa fa-map-marker" style="color:blue"></i> Dealer<br>
         <i class="fa fa-circle" style="color:orange; opacity:0.6;"></i> Customer Network<br>
         <i class="fa fa-star" style="color:purple;"></i> <b>ML Proposed RO</b>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
            
    # Render map
    st_folium(m, width="100%", height=650)